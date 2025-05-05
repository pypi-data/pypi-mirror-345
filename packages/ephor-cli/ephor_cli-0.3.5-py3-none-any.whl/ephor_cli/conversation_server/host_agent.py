from datetime import datetime, UTC
import json
import uuid
import asyncio
from typing import List

from ephor_cli.conversation_server.types import Event

from ephor_cli.conversation_server.remote_agent_connection import (
    RemoteAgentConnections,
    TaskUpdateCallback,
)
from google_a2a.common.client import A2ACardResolver
from google_a2a.common.types import (
    AgentCard,
    Message,
    TaskState,
    Task,
    TaskSendParams,
    TextPart,
    Part,
)
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.graph.graph import CompiledGraph
from langchain.tools.base import StructuredTool
from typing import AsyncIterable
from langchain_core.messages import AIMessage, ToolMessage, BaseMessage

memory = MemorySaver()


class HostAgent:
    """The host agent.

    This is the agent responsible for choosing which remote agents to send
    tasks to and coordinate their work.
    """

    conversation_id: str
    user_id: str
    project_id: str
    remote_agent_addresses: List[str]
    initial_state: list[BaseMessage]
    task_callback: TaskUpdateCallback | None

    def __init__(
        self,
        conversation_id: str,
        user_id: str,
        project_id: str,
        remote_agent_addresses: List[str],
        initial_state: list[BaseMessage] = None,
        task_callback: TaskUpdateCallback | None = None,
    ):
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.project_id = project_id
        self.task_callback = task_callback
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.cards: dict[str, AgentCard] = {}
        for address in remote_agent_addresses:
            card_resolver = A2ACardResolver(address)
            card = card_resolver.get_agent_card()
            remote_connection = RemoteAgentConnections(card)
            self.remote_agent_connections[card.name] = remote_connection
            self.cards[card.name] = card
        agent_info = []
        for ra in self._list_remote_agents():
            agent_info.append(json.dumps(ra))
        self.agents = "\n".join(agent_info)
        self._agent: CompiledGraph = self.create_agent(initial_state)

    def register_agent_card(self, card: AgentCard):
        remote_connection = RemoteAgentConnections(card)
        self.remote_agent_connections[card.name] = remote_connection
        self.cards[card.name] = card
        agent_info = []
        for ra in self._list_remote_agents():
            agent_info.append(json.dumps(ra))
        self.agents = "\n".join(agent_info)
        self.update_agent()

    def create_agent(self, initial_state: list[BaseMessage] = None) -> CompiledGraph:
        model = ChatAnthropic(model="claude-3-5-sonnet-20240620")
        config = {"configurable": {"thread_id": self.conversation_id}}
        agent = create_react_agent(
            model,
            prompt=self.root_instruction(),
            tools=[
                StructuredTool.from_function(self.list_remote_agents),
                StructuredTool.from_function(self.send_task),
            ],
            checkpointer=memory,
        )
        if initial_state:
            agent.update_state(config, {"messages": initial_state})
        return agent

    def update_agent(self):
        config = {"configurable": {"thread_id": self.conversation_id}}
        current_state = self._agent.get_state(config)
        current_state = current_state.values.get("messages", [])
        self._agent = self.create_agent(current_state)

    def root_instruction(self) -> str:
        return f"""You are an expert delegator that can delegate the user request to the
appropriate remote agents.

Discovery:
- You can use `list_remote_agents` to list the available remote agents you
can use to delegate the task.

Execution:
- For actionable tasks, you can use `create_task` to assign tasks to remote agents to perform.
Be sure to include the remote agent name when you respond to the user.

You can use `check_pending_task_states` to check the states of the pending
tasks.

Please rely on tools to address the request, and don't make up the response. If you are not sure, please ask the user for more details.
Focus on the most recent parts of the conversation primarily.

Agents:
{self.agents}
"""

    def _list_remote_agents(self):
        """List the available remote agents you can use to delegate the task."""
        if not self.remote_agent_connections:
            return []

        remote_agent_info = []
        for card in self.cards.values():
            remote_agent_info.append(
                {"name": card.name, "description": card.description}
            )
        return remote_agent_info

    def list_remote_agents(self):
        """List the available remote agents you can use to delegate the task."""
        return self._list_remote_agents()

    def send_task(self, agent_name: str, message: str):
        """Sends a task either streaming (if supported) or non-streaming.

        This will send a message to the remote agent named agent_name.

        Args:
          agent_name: The name of the agent to send the task to.
          message: The message to send to the agent for the task.
          tool_context: The tool context this method runs in.

        Yields:
          A dictionary of JSON data.
        """
        # Create a new event loop to run the async function
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self._send_task(agent_name, message))
        finally:
            loop.close()

    async def _send_task(self, agent_name: str, message: str):
        """Sends a task either streaming (if supported) or non-streaming.

        This will send a message to the remote agent named agent_name.

        Args:
          agent_name: The name of the agent to send the task to.
          message: The message to send to the agent for the task.
          tool_context: The tool context this method runs in.

        Yields:
          A dictionary of JSON data.
        """
        if agent_name not in self.remote_agent_connections:
            raise ValueError(f"Agent {agent_name} not found")
        client = self.remote_agent_connections[agent_name]
        if not client:
            raise ValueError(f"Client not available for {agent_name}")
        task: Task
        messageId = str(uuid.uuid4())
        metadata = {
            "message_id": messageId,
            "conversation_id": self.conversation_id,
            "project_id": self.project_id,
            "user_id": self.user_id,
        }
        request: TaskSendParams = TaskSendParams(
            id=messageId,
            sessionId=self.conversation_id,
            message=Message(
                role="user",
                parts=[TextPart(text=message)],
                metadata=metadata,
            ),
            acceptedOutputModes=["text", "text/plain", "image/png"],
            # pushNotification=None,
            metadata={
                "conversation_id": self.conversation_id,
                "project_id": self.project_id,
                "user_id": self.user_id,
            },
        )
        task = await client.send_task(request, self.task_callback)
        if task.status.state == TaskState.INPUT_REQUIRED:
            pass
        elif task.status.state == TaskState.CANCELED:
            # Open question, should we return some info for cancellation instead
            raise ValueError(f"Agent {agent_name} task {task.id} is cancelled")
        elif task.status.state == TaskState.FAILED:
            # Raise error for failure
            raise ValueError(f"Agent {agent_name} task {task.id} failed")

        response = []
        if task.status.message:
            # Assume the information is in the task message.
            response.extend(convert_parts(task.status.message.parts))
        if task.artifacts:
            for artifact in task.artifacts:
                response.extend(convert_parts(artifact.parts))
        return response

    async def invoke(self, query, sessionId) -> AIMessage:
        inputs = {"messages": [("user", query)]}
        config = {"configurable": {"thread_id": sessionId}}

        print(
            f"Streaming agent with query: {query}, current state: {self._agent.get_state(config)}"
        )
        await self._agent.ainvoke(inputs, config)
        return self.get_agent_response()

    async def stream(self, query) -> AsyncIterable[Event]:
        inputs = {"messages": [("user", query)]}
        config = {"configurable": {"thread_id": self.conversation_id}}

        print(
            f"Streaming agent with query: {query}, current state: {self._agent.get_state(config)}"
        )

        async for item in self._agent.astream(inputs, config, stream_mode="values"):
            message = item["messages"][-1]
            print(f"Message: {message}")
            if isinstance(message, AIMessage):
                if message.tool_calls and len(message.tool_calls) > 0:
                    for tool_call in message.tool_calls:
                        yield Event(
                            id=str(uuid.uuid4()),
                            actor="Host Agent",
                            content=Message(
                                role="agent",
                                parts=[
                                    TextPart(
                                        text=f"Invoked tool {tool_call['name']} with parameters \n```{json.dumps(tool_call['args'], indent=2)}```"
                                    )
                                ],
                                metadata={
                                    "conversation_id": self.conversation_id,
                                    "project_id": self.project_id,
                                    "user_id": self.user_id,
                                },
                            ),
                            timestamp=datetime.now(UTC).timestamp(),
                        )
            elif isinstance(message, ToolMessage):
                yield Event(
                    id=str(uuid.uuid4()),
                    actor="Host Agent",
                    content=Message(
                        role="agent",
                        parts=[
                            TextPart(
                                text=f"Received tool response:\n```{json.dumps(message.content, indent=2)}```"
                            )
                        ],
                        metadata={
                            "conversation_id": self.conversation_id,
                            "project_id": self.project_id,
                            "user_id": self.user_id,
                        },
                    ),
                    timestamp=datetime.now(UTC).timestamp(),
                )

        final_message = self.get_agent_response()
        print(f"Final message: {final_message}")
        yield Event(
            id=str(uuid.uuid4()),
            actor="Host Agent",
            content=Message(
                role="agent",
                parts=[
                    TextPart(
                        text=f"Final message from the agent:\n```{final_message.content}```"
                    )
                ],
                metadata={
                    "conversation_id": self.conversation_id,
                    "project_id": self.project_id,
                    "user_id": self.user_id,
                },
            ),
            timestamp=datetime.now(UTC).timestamp(),
        )

    def get_agent_response(self):
        config = {"configurable": {"thread_id": self.conversation_id}}
        state = self._agent.get_state(config)
        return state.values["messages"][-1]


def convert_parts(parts: list[Part]) -> list[str]:
    rval = []
    for p in parts:
        rval.append(convert_part(p))
    return rval


def convert_part(part: Part):
    if part.type == "text":
        return part.text
    elif part.type == "data":
        return part.data
