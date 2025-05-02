from contextlib import asynccontextmanager
from typing import Any, AsyncIterable, Dict, Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

from ephor_cli.types import MCPServerConfig

import logging

logger = logging.getLogger(__name__)

memory = MemorySaver()


@asynccontextmanager
async def get_tools(mcpServers: list[MCPServerConfig]):
    config = {
        mcpServer.name: {
            "url": mcpServer.url,
            "transport": mcpServer.transport,
        }
        for mcpServer in mcpServers
    }
    async with MultiServerMCPClient(config) as client:
        logger.info(f"Loaded {len(client.get_tools())} tools")
        yield client.get_tools()


class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal["input_required", "completed", "error"] = "input_required"
    message: str


class Agent:
    def __init__(
        self,
        prompt: str = None,
        model: str = "claude-3-5-sonnet-20240620",
        temperature: float = 0.2,
        mcpServers: list[MCPServerConfig] = [],
        supported_content_types: list[str] = ["text", "text/plain"],
    ):
        self.prompt = prompt
        self.model = ChatAnthropic(model=model, temperature=temperature)
        self.mcpServers = mcpServers
        self.supported_content_types = supported_content_types
        self.tools = []
        self.graph = None
        self.tools_context = None

    async def shutdown(self):
        if self.tools_context:
            await self.tools_context.__aexit__(None, None, None)

    async def initialize_graph(self):
        if self.graph:
            return

        if self.mcpServers:
            self.tools_context = get_tools(self.mcpServers)
            self.tools = await self.tools_context.__aenter__()

        self.graph = create_react_agent(
            self.model,
            prompt=self.prompt,
            tools=self.tools,
            checkpointer=memory,
            response_format=ResponseFormat,
        )

    async def invoke(self, query, sessionId) -> str:
        await self.initialize_graph()
        config = {"configurable": {"thread_id": sessionId}}
        logger.info(
            f"Invoking agent with query: {query}, sessionId: {sessionId}, current state: {self.graph.get_state(config)}"
        )
        await self.graph.ainvoke({"messages": [("user", query)]}, config)
        return self.get_agent_response(config)

    async def stream(self, query, sessionId) -> AsyncIterable[Dict[str, Any]]:
        await self.initialize_graph()
        inputs = {"messages": [("user", query)]}
        config = {"configurable": {"thread_id": sessionId}}

        logger.info(
            f"Streaming agent with query: {query}, sessionId: {sessionId}, current state: {self.graph.get_state(config)}"
        )

        async for item in self.graph.astream(inputs, config, stream_mode="values"):
            message = item["messages"][-1]
            logger.info(f"Message: {message}")
            if isinstance(message, AIMessage):
                if message.tool_calls and len(message.tool_calls) > 0:
                    yield {
                        "is_task_complete": False,
                        "require_user_input": False,
                        "content": f"Looking up the tool {message.tool_calls[0]['name']}...",
                    }
            elif isinstance(message, ToolMessage):
                yield {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "content": "Processing the tool response...",
                }

        yield self.get_agent_response(config)

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get("structured_response")

        # Get the final AI message which might contain the complete response
        messages = current_state.values.get("messages", [])
        final_ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]
        final_content = final_ai_messages[-1].content if final_ai_messages else ""

        if structured_response and isinstance(structured_response, ResponseFormat):
            if structured_response.status == "input_required":
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": final_content + "\n\n" + structured_response.message,
                }
            elif structured_response.status == "error":
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": final_content + "\n\n" + structured_response.message,
                }
            elif structured_response.status == "completed":
                return {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "content": final_content + "\n\n" + structured_response.message,
                }

        return {
            "is_task_complete": False,
            "require_user_input": True,
            "content": "We are unable to process your request at the moment. Please try again.",
        }
