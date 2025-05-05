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
    ListEventResponse,
    SendMessageRequest,
    ListMessageRequest,
    ListEventRequest,
    ListConversationRequest,
    PendingMessageRequest,
    ListTaskRequest,
    RegisterAgentRequest,
    ListAgentRequest,
    DeleteConversationRequest,
    DeleteConversationResponse,
    DeregisterAgentRequest,
    DeregisterAgentResponse,
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
            "/conversation/delete",
            self._delete_conversation,
            methods=["POST"],
            response_model=DeleteConversationResponse,
            summary="Delete a conversation",
            description="Deletes an existing conversation and all associated data",
        )
        router.add_api_route(
            "/conversation/list",
            self._list_conversations,
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
            "/events/list",
            self._list_events,
            methods=["POST"],
            response_model=ListEventResponse,
            summary="List events",
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
            "/agent/deregister",
            self._deregister_agent,
            methods=["POST"],
            response_model=DeregisterAgentResponse,
            summary="Deregister an agent",
            description="Deregisters an agent from the specified conversation",
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
        c = self.manager.create_conversation(
            request.params.user_id, request.params.project_id
        )
        return CreateConversationResponse(result=c)

    def _delete_conversation(self, request: DeleteConversationRequest = None):
        """Delete an existing conversation"""
        try:
            result = self.manager.delete_conversation(
                request.params.conversation_id,
                request.params.project_id,
                request.params.user_id,
            )
            return DeleteConversationResponse(result=result)
        except Exception as e:
            return DeleteConversationResponse(
                result=False, error=f"Failed to delete conversation: {e}"
            )

    async def _send_message(self, request_data: SendMessageRequest):
        """Send a message to a conversation"""
        message = request_data.params.message
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
                project_id=(
                    message.metadata["project_id"]
                    if "project_id" in message.metadata
                    else ""
                ),
                user_id=(
                    message.metadata["user_id"] if "user_id" in message.metadata else ""
                ),
            )
        )

    async def _list_messages(self, request_data: ListMessageRequest):
        """List messages in a conversation"""
        return ListMessageResponse(
            result=self.cache_content(
                self.manager.list_messages(
                    request_data.params.user_id,
                    request_data.params.project_id,
                    request_data.params.conversation_id,
                )
            )
        )

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
        return PendingMessageResponse(
            result=self.manager.get_pending_messages(
                request_data.params.user_id,
                request_data.params.project_id,
                request_data.params.conversation_id,
            )
        )

    def _list_conversations(self, request_data: ListConversationRequest):
        """List all conversations"""
        return ListConversationResponse(
            result=self.manager.list_conversations(
                request_data.params.user_id, request_data.params.project_id
            )
        )

    def _list_events(self, request_data: ListEventRequest):
        """Get all events"""
        return ListEventResponse(
            result=self.manager.list_events(
                request_data.params.user_id,
                request_data.params.project_id,
                request_data.params.conversation_id,
            )
        )

    def _list_tasks(self, request_data: ListTaskRequest):
        """List all tasks"""
        return ListTaskResponse(
            result=self.manager.list_tasks(
                request_data.params.user_id,
                request_data.params.project_id,
                request_data.params.conversation_id,
            )
        )

    async def _register_agent(self, request_data: RegisterAgentRequest):
        """Register a new agent"""
        try:
            agent = self.manager.register_agent(
                request_data.params.url,
                request_data.params.conversation_id,
                request_data.params.project_id,
                request_data.params.user_id,
            )
            print("Registered agent", agent)
            return RegisterAgentResponse(result=agent)
        except Exception as e:
            return RegisterAgentResponse(error=f"Failed to register agent: {e}")

    async def _deregister_agent(self, request_data: DeregisterAgentRequest):
        """Deregister an agent from a conversation"""
        try:
            success = self.manager.deregister_agent(
                request_data.params.url,
                request_data.params.conversation_id,
                request_data.params.project_id,
                request_data.params.user_id,
            )
            return DeregisterAgentResponse(result=success)
        except Exception as e:
            return DeregisterAgentResponse(
                result=False, error=f"Failed to deregister agent: {e}"
            )

    async def _list_agents(self, request_data: ListAgentRequest):
        """List all registered agents"""
        return ListAgentResponse(
            result=self.manager.list_agents(
                request_data.params.user_id,
                request_data.params.project_id,
                request_data.params.conversation_id,
            )
        )

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
