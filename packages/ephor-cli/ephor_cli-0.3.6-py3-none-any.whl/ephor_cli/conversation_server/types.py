from typing import Union
from pydantic import BaseModel, Field, TypeAdapter
from typing import Literal, Annotated, Tuple

from google_a2a.common.types import (
    Message,
    Task,
    JSONRPCRequest,
    JSONRPCResponse,
    AgentCard,
)


class Event(BaseModel):
    id: str
    actor: str = ""
    # TODO: Extend to support internal concepts for models, like function calls.
    content: Message
    timestamp: float


class Conversation(BaseModel):
    conversation_id: str
    user_id: str
    project_id: str
    is_active: bool
    name: str = ""
    created_at: str = ""
    updated_at: str = ""
    agents: list[AgentCard] = Field(default_factory=list)
    tasks: list[Task] = Field(default_factory=list)
    messages: list[Message] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)
    pending_message_ids: list[str] = Field(default_factory=list)
    task_map: dict[str, str] = Field(default_factory=dict)
    trace_map: dict[str, str] = Field(default_factory=dict)


class SendMessageParams(BaseModel):
    user_id: str
    project_id: str
    conversation_id: str
    message: Message


class SendMessageRequest(JSONRPCRequest):
    method: Literal["message/send"] = "message/send"
    params: SendMessageParams


class ListMessageParams(BaseModel):
    user_id: str
    project_id: str
    conversation_id: str


class ListMessageRequest(JSONRPCRequest):
    method: Literal["message/list"] = "message/list"
    params: ListMessageParams


class ListMessageResponse(JSONRPCResponse):
    result: list[Message] | None = None


class MessageInfo(BaseModel):
    message_id: str
    conversation_id: str
    project_id: str
    user_id: str


class SendMessageResponse(JSONRPCResponse):
    result: Message | MessageInfo | None = None


class ListEventParams(BaseModel):
    user_id: str
    project_id: str
    conversation_id: str


class ListEventRequest(JSONRPCRequest):
    method: Literal["events/list"] = "events/list"
    params: ListEventParams


class ListEventResponse(JSONRPCResponse):
    result: list[Event] | None = None


class ListConversationParams(BaseModel):
    user_id: str
    project_id: str


class ListConversationRequest(JSONRPCRequest):
    method: Literal["conversation/list"] = "conversation/list"
    params: ListConversationParams


class ListConversationResponse(JSONRPCResponse):
    result: list[Conversation] | None = None


class PendingMessageParams(BaseModel):
    user_id: str
    project_id: str
    conversation_id: str


class PendingMessageRequest(JSONRPCRequest):
    method: Literal["message/pending"] = "message/pending"
    params: PendingMessageParams


class PendingMessageResponse(JSONRPCResponse):
    result: list[Tuple[str, str]] | None = None


class CreateConversationParams(BaseModel):
    user_id: str
    project_id: str


class CreateConversationRequest(JSONRPCRequest):
    method: Literal["conversation/create"] = "conversation/create"
    params: CreateConversationParams


class CreateConversationResponse(JSONRPCResponse):
    result: Conversation | None = None


class DeleteConversationParams(BaseModel):
    user_id: str
    project_id: str
    conversation_id: str


class DeleteConversationRequest(JSONRPCRequest):
    method: Literal["conversation/delete"] = "conversation/delete"
    params: DeleteConversationParams


class DeleteConversationResponse(JSONRPCResponse):
    result: bool | None = None
    error: str | None = None


class ListTaskParams(BaseModel):
    user_id: str
    project_id: str
    conversation_id: str


class ListTaskRequest(JSONRPCRequest):
    method: Literal["task/list"] = "task/list"
    params: ListTaskParams


class ListTaskResponse(JSONRPCResponse):
    result: list[Task] | None = None


class RegisterAgentParams(BaseModel):
    user_id: str
    project_id: str
    conversation_id: str
    url: str


class RegisterAgentRequest(JSONRPCRequest):
    method: Literal["agent/register"] = "agent/register"
    params: RegisterAgentParams


class RegisterAgentResponse(JSONRPCResponse):
    result: AgentCard | None = None
    error: str | None = None


class ListAgentParams(BaseModel):
    user_id: str
    project_id: str
    conversation_id: str


class ListAgentRequest(JSONRPCRequest):
    method: Literal["agent/list"] = "agent/list"
    params: ListAgentParams


class ListAgentResponse(JSONRPCResponse):
    result: list[AgentCard] | None = None


class DeregisterAgentParams(BaseModel):
    user_id: str
    project_id: str
    conversation_id: str
    url: str


class DeregisterAgentRequest(JSONRPCRequest):
    method: Literal["agent/deregister"] = "agent/deregister"
    params: DeregisterAgentParams


class DeregisterAgentResponse(JSONRPCResponse):
    result: bool | None = None
    error: str | None = None


AgentRequest = TypeAdapter(
    Annotated[
        Union[
            SendMessageRequest,
            ListConversationRequest,
        ],
        Field(discriminator="method"),
    ]
)


class AgentClientError(Exception):
    pass


class AgentClientHTTPError(AgentClientError):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP Error {status_code}: {message}")


class AgentClientJSONError(AgentClientError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"JSON Error: {message}")
