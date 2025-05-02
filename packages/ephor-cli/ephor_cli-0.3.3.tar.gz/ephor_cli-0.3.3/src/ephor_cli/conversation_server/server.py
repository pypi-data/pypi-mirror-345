import asyncio
import base64
import threading
import os
import uuid
from fastapi import APIRouter
from fastapi import Response
from google_a2a.common.types import Message, FilePart, FileContent
from ephor_cli.conversation_server.in_memory_manager import InMemoryFakeAgentManager
from ephor_cli.conversation_server.application_manager import ApplicationManager
from ephor_cli.conversation_server.adk_host_manager import (
    ADKHostManager,
    get_message_id,
)
from ephor_cli.conversation_server.types import (
    CreateConversationResponse,
    CreateConversationRequest,
    ListConversationResponse,
    SendMessageResponse,
    MessageInfo,
    ListMessageResponse,
    PendingMessageResponse,
    ListTaskResponse,
    RegisterAgentResponse,
    ListAgentResponse,
    GetEventResponse,
    SendMessageRequest,
    ListMessageRequest,
    GetEventRequest,
    ListConversationRequest,
    PendingMessageRequest,
    ListTaskRequest,
    RegisterAgentRequest,
    ListAgentRequest,
)
from pydantic import BaseModel
from fastapi.responses import JSONResponse


class APIKeyRequest(BaseModel):
    api_key: str


class ConversationServer:
    """ConversationServer is the backend to serve the agent interactions in the UI

    This defines the interface that is used by the Mesop system to interact with
    agents and provide details about the executions.
    """

    def __init__(self, router: APIRouter):
        agent_manager = os.environ.get("A2A_HOST", "ADK")
        self.manager: ApplicationManager

        if agent_manager.upper() == "ADK":
            self.manager = ADKHostManager()
        else:
            self.manager = InMemoryFakeAgentManager()
        self._file_cache = {}  # dict[str, FilePart] maps file id to message data
        self._message_to_cache = {}  # dict[str, str] maps message id to cache id

        # Add root health check endpoint
        router.add_api_route(
            "/",
            self._health_check,
            methods=["GET"],
            summary="Root health check endpoint",
            description="Returns a 200 OK status when the server is healthy",
        )
        router.add_api_route(
            "/health",
            self._health_check,
            methods=["GET"],
            summary="Health check endpoint",
            description="Returns a 200 OK status when the server is healthy",
        )
        router.add_api_route(
            "/conversation/create",
            self._create_conversation,
            methods=["POST"],
            response_model=CreateConversationResponse,
            summary="Create a new conversation",
            description="Creates a new conversation and returns the conversation details",
        )
        router.add_api_route(
            "/conversation/list",
            self._list_conversation,
            methods=["POST"],
            response_model=ListConversationResponse,
            summary="List all conversations",
            description="Returns a list of all available conversations",
        )
        router.add_api_route(
            "/message/send",
            self._send_message,
            methods=["POST"],
            response_model=SendMessageResponse,
            summary="Send a message",
            description="Sends a message to the specified conversation",
        )
        router.add_api_route(
            "/events/get",
            self._get_events,
            methods=["POST"],
            response_model=GetEventResponse,
            summary="Get events",
            description="Retrieves all events",
        )
        router.add_api_route(
            "/message/list",
            self._list_messages,
            methods=["POST"],
            response_model=ListMessageResponse,
            summary="List messages",
            description="Lists all messages for a specified conversation",
        )
        router.add_api_route(
            "/message/pending",
            self._pending_messages,
            methods=["POST"],
            response_model=PendingMessageResponse,
            summary="Get pending messages",
            description="Retrieves all pending messages",
        )
        router.add_api_route(
            "/task/list",
            self._list_tasks,
            methods=["POST"],
            response_model=ListTaskResponse,
            summary="List tasks",
            description="Lists all active tasks",
        )
        router.add_api_route(
            "/agent/register",
            self._register_agent,
            methods=["POST"],
            response_model=RegisterAgentResponse,
            summary="Register an agent",
            description="Registers a new agent with the specified URL",
        )
        router.add_api_route(
            "/agent/list",
            self._list_agents,
            methods=["POST"],
            response_model=ListAgentResponse,
            summary="List agents",
            description="Lists all registered agents",
        )
        router.add_api_route(
            "/message/file/{file_id}",
            self._files,
            methods=["GET"],
            summary="Get file content",
            description="Retrieves file content by file ID",
        )

    def _health_check(self):
        """Health check endpoint for ECS"""
        return JSONResponse(content={"status": "healthy"}, status_code=200)

    def _create_conversation(self, request: CreateConversationRequest = None):
        """Create a new conversation"""
        c = self.manager.create_conversation()
        return CreateConversationResponse(result=c)

    async def _send_message(self, request_data: SendMessageRequest):
        """Send a message to a conversation"""
        message = request_data.params
        message = self.manager.sanitize_message(message)
        t = threading.Thread(
            target=lambda: asyncio.run(self.manager.process_message(message))
        )
        t.start()
        return SendMessageResponse(
            result=MessageInfo(
                message_id=message.metadata["message_id"],
                conversation_id=(
                    message.metadata["conversation_id"]
                    if "conversation_id" in message.metadata
                    else ""
                ),
            )
        )

    async def _list_messages(self, request_data: ListMessageRequest):
        """List messages in a conversation"""
        conversation_id = request_data.params
        conversation = self.manager.get_conversation(conversation_id)
        if conversation:
            return ListMessageResponse(result=self.cache_content(conversation.messages))
        return ListMessageResponse(result=[])

    def cache_content(self, messages: list[Message]):
        rval = []
        for m in messages:
            message_id = get_message_id(m)
            if not message_id:
                rval.append(m)
                continue
            new_parts = []
            for i, part in enumerate(m.parts):
                if part.type != "file":
                    new_parts.append(part)
                    continue
                message_part_id = f"{message_id}:{i}"
                if message_part_id in self._message_to_cache:
                    cache_id = self._message_to_cache[message_part_id]
                else:
                    cache_id = str(uuid.uuid4())
                    self._message_to_cache[message_part_id] = cache_id
                # Replace the part data with a url reference
                new_parts.append(
                    FilePart(
                        file=FileContent(
                            mimeType=part.file.mimeType,
                            uri=f"/message/file/{cache_id}",
                        )
                    )
                )
                if cache_id not in self._file_cache:
                    self._file_cache[cache_id] = part
            m.parts = new_parts
            rval.append(m)
        return rval

    async def _pending_messages(self, request_data: PendingMessageRequest):
        """Get pending messages"""
        return PendingMessageResponse(result=self.manager.get_pending_messages())

    def _list_conversation(self, request_data: ListConversationRequest):
        """List all conversations"""
        return ListConversationResponse(result=self.manager.conversations)

    def _get_events(self, request_data: GetEventRequest):
        """Get all events"""
        return GetEventResponse(result=self.manager.events)

    def _list_tasks(self, request_data: ListTaskRequest):
        """List all tasks"""
        return ListTaskResponse(result=self.manager.tasks)

    async def _register_agent(self, request_data: RegisterAgentRequest):
        """Register a new agent"""
        url = request_data.params
        self.manager.register_agent(url)
        return RegisterAgentResponse()

    async def _list_agents(self, request_data: ListAgentRequest):
        """List all registered agents"""
        return ListAgentResponse(result=self.manager.agents)

    def _files(self, file_id: str):
        """Get file content by ID"""
        if file_id not in self._file_cache:
            raise Exception("file not found")
        part = self._file_cache[file_id]
        if "image" in part.file.mimeType:
            return Response(
                content=base64.b64decode(part.file.bytes), media_type=part.file.mimeType
            )
        return Response(content=part.file.bytes, media_type=part.file.mimeType)
