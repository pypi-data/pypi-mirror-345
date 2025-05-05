import base64
import datetime
import json
import threading
import uuid
from typing import Dict, Optional

from google.genai import types
from google_a2a.common.types import (
    AgentCard,
    DataPart,
    FileContent,
    FilePart,
    Message,
    Part,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TextPart,
)

from ephor_cli.constant import DYNAMODB_TABLE_NAME
from ephor_cli.conversation_server.application_manager import ApplicationManager
from ephor_cli.conversation_server.ddb_manager import DDBManager
from ephor_cli.conversation_server.host_agent import HostAgent
from ephor_cli.conversation_server.remote_agent_connection import (
    TaskCallbackArg,
)
from ephor_cli.conversation_server.types import Conversation, Event
from ephor_cli.utils.agent_card import get_agent_card
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class ADKHostManager(ApplicationManager):
    """An implementation of memory based management with fake agent actions

    This implements the interface of the ApplicationManager to plug into
    the AgentServer. This acts as the service contract that the Mesop app
    uses to send messages to the agent and provide information for the frontend.
    """

    def __init__(self):
        self._artifact_chunks = {}
        self._host_agents: Dict[str, HostAgent] = {}
        self._db_service = DDBManager(table_name=DYNAMODB_TABLE_NAME)
        self._global_lock = threading.Lock()
        self._conversation_locks = {}

    def _get_conversation_lock(self, conversation_id: str) -> threading.Lock:
        """Get or create a lock for a specific conversation."""
        with self._global_lock:
            if conversation_id not in self._conversation_locks:
                self._conversation_locks[conversation_id] = threading.Lock()
            return self._conversation_locks[conversation_id]

    def _get_or_create_host_agent(
        self, conversation_id: str, project_id: str, user_id: str
    ) -> HostAgent:
        """Get or create a host agent for a specific conversation."""
        conversation = self.get_conversation(conversation_id, project_id, user_id)
        if not conversation:
            return None
        with self._global_lock:
            if conversation_id not in self._host_agents:
                self._host_agents[conversation_id] = HostAgent(
                    conversation_id=conversation_id,
                    project_id=project_id,
                    user_id=user_id,
                    remote_agent_addresses=[agent.url for agent in conversation.agents],
                    initial_state=[
                        convert_to_langchain_message(message)
                        for message in conversation.messages
                    ],
                    task_callback=self.task_callback,
                )
            return self._host_agents[conversation_id]

    def create_conversation(self, user_id: str, project_id: str) -> Conversation:
        c = Conversation(
            conversation_id=str(uuid.uuid4()),
            is_active=True,
            user_id=user_id,
            project_id=project_id,
            created_at=datetime.datetime.utcnow().isoformat(),
            updated_at=datetime.datetime.utcnow().isoformat(),
        )
        self._db_service.create_conversation(c)
        return c

    def list_conversations(self, user_id: str, project_id: str) -> list[Conversation]:
        """List all conversations for a user and project."""
        return self._db_service.list_conversations(user_id, project_id)

    def delete_conversation(
        self, conversation_id: str, project_id: str, user_id: str
    ) -> bool:
        """Delete a conversation."""
        # Clean up host agent and runner for this conversation
        with self._global_lock:
            if conversation_id in self._host_agents:
                del self._host_agents[conversation_id]
            if conversation_id in self._conversation_locks:
                del self._conversation_locks[conversation_id]

        return self._db_service.delete_conversation(
            conversation_id, project_id, user_id
        )

    def list_agents(
        self, user_id: str, project_id: str, conversation_id: str
    ) -> list[AgentCard]:
        """List all agents for a conversation."""
        conversation = self.get_conversation(conversation_id, project_id, user_id)
        return conversation.agents if conversation else []

    def list_messages(
        self, user_id: str, project_id: str, conversation_id: str
    ) -> list[Message]:
        """List all messages for a conversation."""
        conversation = self.get_conversation(conversation_id, project_id, user_id)
        return conversation.messages if conversation else []

    def list_events(
        self, user_id: str, project_id: str, conversation_id: str
    ) -> list[Event]:
        """List all events for a conversation."""
        conversation = self.get_conversation(conversation_id, project_id, user_id)
        return conversation.events if conversation else []

    def list_tasks(
        self, user_id: str, project_id: str, conversation_id: str
    ) -> list[Task]:
        """List all tasks for a conversation."""
        conversation = self.get_conversation(conversation_id, project_id, user_id)
        return conversation.tasks if conversation else []

    def sanitize_message(self, message: Message) -> Message:
        if not message.metadata:
            message.metadata = {}
        if "message_id" not in message.metadata:
            message.metadata.update({"message_id": str(uuid.uuid4())})
        conversation_id = get_conversation_id(message)
        project_id = get_project_id(message)
        user_id = get_user_id(message)
        conversation = self.get_conversation(conversation_id, project_id, user_id)
        if conversation and conversation.messages:
            # Get the last message
            last_message_id = get_message_id(conversation.messages[-1])
            if last_message_id:
                message.metadata.update({"last_message_id": last_message_id})
        return message

    async def process_message(self, message: Message):
        message_id = get_message_id(message)
        conversation_id = get_conversation_id(message)
        project_id = get_project_id(message)
        user_id = get_user_id(message)

        if not conversation_id or not project_id or not user_id:
            return

        host_agent = self._get_or_create_host_agent(
            conversation_id, project_id, user_id
        )

        # Add message to conversation
        self.add_message(user_id, project_id, conversation_id, message)

        # Add to pending messages
        self.add_pending_message(user_id, project_id, conversation_id, message_id)

        # Create user event
        event = Event(
            id=str(uuid.uuid4()),
            actor="User",
            content=message,
            timestamp=datetime.datetime.utcnow().timestamp(),
        )
        self.add_event(user_id, project_id, conversation_id, event)

        async for event in host_agent.stream(query=message.parts[0].text):
            print(f"Received event: {event}")
            self.add_event(user_id, project_id, conversation_id, event)

        response: AIMessage | None = host_agent.get_agent_response()
        if response:
            message = Message(
                role="agent",
                parts=[TextPart(text=response.content)],
                metadata={
                    "conversation_id": conversation_id,
                    "project_id": project_id,
                    "user_id": user_id,
                },
            )
            conversation = self.get_conversation(conversation_id, project_id, user_id)
            last_message_id = get_last_message_id(message)
            new_message_id = ""
            if (
                conversation
                and last_message_id
                and last_message_id in conversation.trace_map
            ):
                new_message_id = conversation.trace_map[last_message_id]
            else:
                new_message_id = str(uuid.uuid4())
                last_message_id = None
            response.metadata = {
                **message.metadata,
                **{"last_message_id": last_message_id, "message_id": new_message_id},
            }
            self.add_message(user_id, project_id, conversation_id, message)
            self.remove_pending_message(
                user_id, project_id, conversation_id, message_id
            )

    def add_task(
        self, user_id: str, project_id: str, conversation_id: str, task: Task
    ) -> bool:
        """Add a task to a conversation with locking mechanism.

        Args:
            user_id: The user ID
            project_id: The project ID
            conversation_id: The conversation ID
            task: The task to add

        Returns:
            True if successful, False otherwise
        """
        lock = self._get_conversation_lock(conversation_id)
        with lock:
            conversation = self.get_conversation(conversation_id, project_id, user_id)
            if not conversation:
                return False

            tasks = conversation.tasks.copy()
            # Check if task already exists
            if any(t.id == task.id for t in tasks):
                return False

            tasks.append(task)
            return self._db_service.update_conversation(
                user_id, project_id, conversation_id, {"tasks": tasks}
            )

    def update_task(
        self, user_id: str, project_id: str, conversation_id: str, task: Task
    ) -> bool:
        """Update a task in a conversation with locking mechanism.

        Args:
            user_id: The user ID
            project_id: The project ID
            conversation_id: The conversation ID
            task: The task to update

        Returns:
            True if successful, False otherwise
        """
        lock = self._get_conversation_lock(conversation_id)
        with lock:
            conversation = self.get_conversation(conversation_id, project_id, user_id)
            if not conversation:
                return False

            tasks = conversation.tasks.copy()
            for i, t in enumerate(tasks):
                if t.id == task.id:
                    tasks[i] = task
                    return self._db_service.update_conversation(
                        user_id, project_id, conversation_id, {"tasks": tasks}
                    )

            # Task not found
            return False

    def task_callback(self, task: TaskCallbackArg, agent_card: AgentCard):
        self.emit_event(task, agent_card)

        conversation_id = get_conversation_id(task)
        project_id = get_project_id(task)
        user_id = get_user_id(task)

        if not (conversation_id and project_id and user_id):
            return None

        if isinstance(task, TaskStatusUpdateEvent):
            current_task = self.add_or_get_task(task)
            current_task.status = task.status
            self.attach_message_to_task(task.status.message, current_task.id)
            self.insert_message_history(current_task, task.status.message)
            self.update_task(user_id, project_id, conversation_id, current_task)
            self.insert_id_trace(task.status.message)
            return current_task
        elif isinstance(task, TaskArtifactUpdateEvent):
            current_task = self.add_or_get_task(task)
            self.process_artifact_event(current_task, task)
            self.update_task(user_id, project_id, conversation_id, current_task)
            return current_task
        # Otherwise this is a Task, either new or updated
        elif not any(
            filter(
                lambda x: x.id == task.id,
                self.list_tasks(user_id, project_id, conversation_id),
            )
        ):
            self.attach_message_to_task(task.status.message, task.id)
            self.insert_id_trace(task.status.message)
            self.add_task(user_id, project_id, conversation_id, task)
            return task
        else:
            self.attach_message_to_task(task.status.message, task.id)
            self.insert_id_trace(task.status.message)
            self.update_task(user_id, project_id, conversation_id, task)
            return task

    def emit_event(self, task: TaskCallbackArg, agent_card: AgentCard):
        content = None
        conversation_id = get_conversation_id(task)
        project_id = get_project_id(task)
        user_id = get_user_id(task)

        if not (conversation_id and project_id and user_id):
            return

        metadata = {"conversation_id": conversation_id} if conversation_id else None
        if isinstance(task, TaskStatusUpdateEvent):
            if task.status.message:
                content = task.status.message
            else:
                content = Message(
                    parts=[TextPart(text=str(task.status.state))],
                    role="agent",
                    metadata=metadata,
                )
        elif isinstance(task, TaskArtifactUpdateEvent):
            content = Message(
                parts=task.artifact.parts,
                role="agent",
                metadata=metadata,
            )
        elif task.status and task.status.message:
            content = task.status.message
        elif task.artifacts:
            parts = []
            for a in task.artifacts:
                parts.extend(a.parts)
            content = Message(
                parts=parts,
                role="agent",
                metadata=metadata,
            )
        else:
            content = Message(
                parts=[TextPart(text=str(task.status.state))],
                role="agent",
                metadata=metadata,
            )

        event = Event(
            id=str(uuid.uuid4()),
            actor=agent_card.name,
            content=content,
            timestamp=datetime.datetime.utcnow().timestamp(),
        )
        self.add_event(user_id, project_id, conversation_id, event)

    def attach_message_to_task(self, message: Message | None, task_id: str):
        if message and message.metadata and "message_id" in message.metadata:
            conversation_id = get_conversation_id(message)
            project_id = get_project_id(message)
            user_id = get_user_id(message)

            if conversation_id and project_id and user_id:
                self.update_task_map(
                    user_id,
                    project_id,
                    conversation_id,
                    message.metadata["message_id"],
                    task_id,
                )

    def insert_id_trace(self, message: Message | None):
        if not message:
            return
        message_id = get_message_id(message)
        last_message_id = get_last_message_id(message)
        conversation_id = get_conversation_id(message)
        project_id = get_project_id(message)
        user_id = get_user_id(message)
        lock = self._get_conversation_lock(conversation_id)
        with lock:
            conversation = self.get_conversation(conversation_id, project_id, user_id)
            if not conversation:
                return False
            trace_map = dict(conversation.trace_map)
            trace_map[last_message_id] = message_id
            return self._db_service.update_conversation(
                user_id, project_id, conversation_id, {"trace_map": trace_map}
            )

    def insert_message_history(self, task: Task, message: Message | None):
        if not message:
            return
        if task.history is None:
            task.history = []
        message_id = get_message_id(message)
        if not message_id:
            return
        if get_message_id(task.status.message) not in [
            get_message_id(x) for x in task.history
        ]:
            task.history.append(task.status.message)
        else:
            print(
                "Message id already in history",
                get_message_id(task.status.message),
                task.history,
            )

    def add_or_get_task(self, task: TaskCallbackArg):
        conversation_id = get_conversation_id(task)
        project_id = get_project_id(task)
        user_id = get_user_id(task)

        if not (conversation_id and project_id and user_id):
            # Create a temporary task not associated with conversation
            return Task(
                id=task.id,
                status=TaskStatus(state=TaskState.SUBMITTED),
                metadata=task.metadata,
                artifacts=[],
            )

        tasks = self.list_tasks(user_id, project_id, conversation_id)
        current_task = next(filter(lambda x: x.id == task.id, tasks), None)

        if not current_task:
            current_task = Task(
                id=task.id,
                status=TaskStatus(state=TaskState.SUBMITTED),
                metadata=task.metadata,
                artifacts=[],
                sessionId=conversation_id,
            )
            self.add_task(user_id, project_id, conversation_id, current_task)

        return current_task

    def process_artifact_event(
        self, current_task: Task, task_update_event: TaskArtifactUpdateEvent
    ):
        artifact = task_update_event.artifact
        if not artifact.append:
            # received the first chunk or entire payload for an artifact
            if artifact.lastChunk is None or artifact.lastChunk:
                # lastChunk bit is missing or is set to true, so this is the entire payload
                # add this to artifacts
                if not current_task.artifacts:
                    current_task.artifacts = []
                current_task.artifacts.append(artifact)
            else:
                # this is a chunk of an artifact, stash it in temp store for assemling
                if not task_update_event.id in self._artifact_chunks:
                    self._artifact_chunks[task_update_event.id] = {}
                self._artifact_chunks[task_update_event.id][artifact.index] = artifact
        else:
            # we received an append chunk, add to the existing temp artifact
            if (
                task_update_event.id in self._artifact_chunks
                and artifact.index in self._artifact_chunks[task_update_event.id]
            ):
                current_temp_artifact = self._artifact_chunks[task_update_event.id][
                    artifact.index
                ]
                # Handle if current_temp_artifact exists
                current_temp_artifact.parts.extend(artifact.parts)
                if artifact.lastChunk:
                    if not current_task.artifacts:
                        current_task.artifacts = []
                    current_task.artifacts.append(current_temp_artifact)
                    del self._artifact_chunks[task_update_event.id][artifact.index]

    def add_event(
        self, user_id: str, project_id: str, conversation_id: str, event: Event
    ) -> bool:
        """Add an event to a conversation with locking mechanism.

        Args:
            user_id: The user ID
            project_id: The project ID
            conversation_id: The conversation ID
            event: The event to add

        Returns:
            True if successful, False otherwise
        """
        lock = self._get_conversation_lock(conversation_id)
        with lock:
            conversation = self.get_conversation(conversation_id, project_id, user_id)
            if not conversation:
                return False

            events = conversation.events.copy()
            events.append(event)
            print(f"Adding event: {event}")
            return self._db_service.update_conversation(
                user_id, project_id, conversation_id, {"events": events}
            )

    def add_message(
        self, user_id: str, project_id: str, conversation_id: str, message: Message
    ) -> bool:
        """Add a message to a conversation with locking mechanism.

        Args:
            user_id: The user ID
            project_id: The project ID
            conversation_id: The conversation ID
            message: The message to add

        Returns:
            True if successful, False otherwise
        """
        lock = self._get_conversation_lock(conversation_id)
        with lock:
            conversation = self.get_conversation(conversation_id, project_id, user_id)
            if not conversation:
                return False

            messages = conversation.messages.copy()
            messages.append(message)
            return self._db_service.update_conversation(
                user_id, project_id, conversation_id, {"messages": messages}
            )

    def add_pending_message(
        self, user_id: str, project_id: str, conversation_id: str, message_id: str
    ) -> bool:
        """Add a pending message ID to a conversation with locking mechanism.

        Args:
            user_id: The user ID
            project_id: The project ID
            conversation_id: The conversation ID
            message_id: The ID of the pending message

        Returns:
            True if successful, False otherwise
        """
        lock = self._get_conversation_lock(conversation_id)
        with lock:
            conversation = self.get_conversation(conversation_id, project_id, user_id)
            if not conversation:
                return False

            pending_message_ids = conversation.pending_message_ids.copy()
            if message_id not in pending_message_ids:
                pending_message_ids.append(message_id)
                return self._db_service.update_conversation(
                    user_id,
                    project_id,
                    conversation_id,
                    {"pending_message_ids": pending_message_ids},
                )
            return True

    def remove_pending_message(
        self, user_id: str, project_id: str, conversation_id: str, message_id: str
    ) -> bool:
        """Remove a pending message ID from a conversation with locking mechanism.

        Args:
            user_id: The user ID
            project_id: The project ID
            conversation_id: The conversation ID
            message_id: The ID of the pending message to remove

        Returns:
            True if successful, False otherwise
        """
        lock = self._get_conversation_lock(conversation_id)
        with lock:
            conversation = self.get_conversation(conversation_id, project_id, user_id)
            if not conversation:
                return False

            pending_message_ids = conversation.pending_message_ids.copy()
            if message_id in pending_message_ids:
                pending_message_ids.remove(message_id)
                return self._db_service.update_conversation(
                    user_id,
                    project_id,
                    conversation_id,
                    {"pending_message_ids": pending_message_ids},
                )
            return True

    def add_agent(
        self, user_id: str, project_id: str, conversation_id: str, agent: AgentCard
    ) -> bool:
        """Add an agent to a conversation with locking mechanism.

        Args:
            user_id: The user ID
            project_id: The project ID
            conversation_id: The conversation ID
            agent: The agent to add

        Returns:
            True if successful, False otherwise
        """
        lock = self._get_conversation_lock(conversation_id)
        with lock:
            conversation = self.get_conversation(conversation_id, project_id, user_id)
            if not conversation:
                return False
            agents = conversation.agents.copy()

            # Check if agent already exists
            if any(a.url == agent.url for a in agents):
                raise ValueError("Agent already exists")

            agents.append(agent)
            success = self._db_service.update_conversation(
                user_id, project_id, conversation_id, {"agents": agents}
            )

            # If successfully added to DB, register with the conversation's host agent
            if success:
                host_agent = self._get_or_create_host_agent(
                    conversation_id, project_id, user_id
                )
                host_agent.register_agent_card(agent)

            return success

    def update_task_map(
        self,
        user_id: str,
        project_id: str,
        conversation_id: str,
        message_id: str,
        task_id: str,
    ) -> bool:
        """Update the task map for a conversation with locking mechanism.

        Args:
            user_id: The user ID
            project_id: The project ID
            conversation_id: The conversation ID
            message_id: The message ID to map
            task_id: The task ID to map to

        Returns:
            True if successful, False otherwise
        """
        lock = self._get_conversation_lock(conversation_id)
        with lock:
            conversation = self.get_conversation(conversation_id, project_id, user_id)
            if not conversation:
                return False

            task_map = dict(conversation.task_map)
            task_map[message_id] = task_id
            return self._db_service.update_conversation(
                user_id, project_id, conversation_id, {"task_map": task_map}
            )

    def get_conversation(
        self,
        conversation_id: Optional[str],
        project_id: Optional[str],
        user_id: Optional[str],
    ) -> Optional[Conversation]:
        if not conversation_id or not project_id or not user_id:
            return None
        return self._db_service.get_conversation(conversation_id, project_id, user_id)

    def get_pending_messages(
        self, user_id: str, project_id: str, conversation_id: str
    ) -> list[tuple[str, str]]:
        """Get pending message IDs and their status for a conversation.

        Returns:
            List of tuples (message_id, status_text)
        """
        conversation = self.get_conversation(conversation_id, project_id, user_id)
        if not conversation:
            return []

        rval = []
        for message_id in conversation.pending_message_ids:
            if message_id in conversation.task_map:
                task_id = conversation.task_map[message_id]
                task = next(filter(lambda x: x.id == task_id, conversation.tasks), None)
                if not task:
                    rval.append((message_id, ""))
                elif task.history and task.history[-1].parts:
                    if len(task.history) == 1:
                        rval.append((message_id, "Working..."))
                    else:
                        part = task.history[-1].parts[0]
                        rval.append(
                            (
                                message_id,
                                part.text if part.type == "text" else "Working...",
                            )
                        )
            else:
                rval.append((message_id, ""))
        return rval

    def register_agent(
        self, url: str, conversation_id: str, project_id: str, user_id: str
    ) -> AgentCard:
        """Register an agent with a conversation."""
        agent_data = get_agent_card(url)
        if not agent_data.url:
            agent_data.url = url

        # Add agent to conversation
        self.add_agent(user_id, project_id, conversation_id, agent_data)
        return agent_data

    def deregister_agent(
        self, url: str, conversation_id: str, project_id: str, user_id: str
    ) -> bool:
        """Deregister an agent from a conversation.

        Args:
            agent_id: The ID of the agent to deregister
            conversation_id: The ID of the conversation
            project_id: The ID of the project
            user_id: The ID of the user

        Returns:
            True if agent was deregistered, False otherwise
        """
        lock = self._get_conversation_lock(conversation_id)
        with lock:
            conversation = self.get_conversation(conversation_id, project_id, user_id)
            if not conversation:
                return False

            # Find the agent to remove
            agents = conversation.agents.copy()
            original_count = len(agents)

            # Remove the agent with matching ID
            agents = [agent for agent in agents if agent.url != url]

            # Check if any agent was removed
            if len(agents) == original_count:
                return False

            # Update the conversation with the modified agents list
            success = self._db_service.update_conversation(
                user_id, project_id, conversation_id, {"agents": agents}
            )

            # If successfully updated in DB, reinitialize the host agent
            if success:
                # Recreate the host agent with the updated agent list
                host_agent = self._get_or_create_host_agent(
                    conversation_id, project_id, user_id
                )

                # Clear all registered agents
                host_agent.agent_cards = []

                # Re-register remaining agents
                for agent in agents:
                    host_agent.register_agent_card(agent)
            return success

    @property
    def app_name(self) -> str:
        return "ephor"

    def adk_content_from_message(self, message: Message) -> types.Content:
        parts: list[types.Part] = []
        for part in message.parts:
            if part.type == "text":
                parts.append(types.Part.from_text(text=part.text))
            elif part.type == "data":
                json_string = json.dumps(part.data)
                parts.append(types.Part.from_text(text=json_string))
            elif part.type == "file":
                if part.uri:
                    parts.append(
                        types.Part.from_uri(file_uri=part.uri, mime_type=part.mimeType)
                    )
                # elif content_part.bytes:
                #     parts.append(
                #         types.Part.from_bytes(
                #             data=part.bytes.encode("utf-8"), mime_type=part.mimeType
                #         )
                #     )
                else:
                    raise ValueError("Unsupported message type")
        return types.Content(parts=parts, role=message.role)

    def adk_content_to_message(
        self, content: types.Content, conversation_id: str
    ) -> Message:
        parts: list[Part] = []
        if not content.parts:
            return Message(
                parts=[],
                role=content.role if content.role == "user" else "agent",
                metadata={"conversation_id": conversation_id},
            )
        for part in content.parts:
            if part.text:
                # try parse as data
                try:
                    data = json.loads(part.text)
                    parts.append(DataPart(data=data))
                except:
                    parts.append(TextPart(text=part.text))
            elif part.inline_data:
                parts.append(
                    FilePart(
                        data=part.inline_data.decode("utf-8"),
                        mimeType=part.inline_data.mime_type,
                    )
                )
            elif part.file_data:
                parts.append(
                    FilePart(
                        file=FileContent(
                            uri=part.file_data.file_uri,
                            mimeType=part.file_data.mime_type,
                        )
                    )
                )
            # These aren't managed by the A2A message structure, these are internal
            # details of ADK, we will simply flatten these to json representations.
            elif part.video_metadata:
                parts.append(DataPart(data=part.video_metadata.model_dump()))
            elif part.thought:
                parts.append(TextPart(text="thought"))
            elif part.executable_code:
                parts.append(DataPart(data=part.executable_code.model_dump()))
            elif part.function_call:
                parts.append(DataPart(data=part.function_call.model_dump()))
            elif part.function_response:
                parts.extend(self._handle_function_response(part, conversation_id))
            else:
                raise ValueError("Unexpected content, unknown type")
        return Message(
            role=content.role if content.role == "user" else "agent",
            parts=parts,
            metadata={"conversation_id": conversation_id},
        )

    def _handle_function_response(
        self, part: types.Part, conversation_id: str
    ) -> list[Part]:
        parts = []
        try:
            for p in part.function_response.response["result"]:
                if isinstance(p, str):
                    parts.append(TextPart(text=p))
                elif isinstance(p, dict):
                    if "type" in p and p["type"] == "file":
                        parts.append(FilePart(**p))
                    else:
                        parts.append(DataPart(data=p))
                elif isinstance(p, DataPart):
                    if "artifact-file-id" in p.data:
                        file_part = self._artifact_service.load_artifact(
                            user_id=self.user_id,
                            session_id=conversation_id,
                            app_name=self.app_name,
                            filename=p.data["artifact-file-id"],
                        )
                        file_data = file_part.inline_data
                        base64_data = base64.b64encode(file_data.data).decode("utf-8")
                        parts.append(
                            FilePart(
                                file=FileContent(
                                    bytes=base64_data,
                                    mimeType=file_data.mime_type,
                                    name="artifact_file",
                                )
                            )
                        )
                    else:
                        parts.append(DataPart(data=p.data))
                else:
                    parts.append(TextPart(text=json.dumps(p)))
        except Exception as e:
            print("Couldn't convert to messages:", e)
            parts.append(DataPart(data=part.function_response.model_dump()))
        return parts


def get_message_id(m: Message | None) -> str | None:
    if not m or not m.metadata or "message_id" not in m.metadata:
        return None
    return m.metadata["message_id"]


def get_last_message_id(m: Message | None) -> str | None:
    if not m or not m.metadata or "last_message_id" not in m.metadata:
        return None
    return m.metadata["last_message_id"]


def get_conversation_id(
    m: Task | TaskStatusUpdateEvent | TaskArtifactUpdateEvent | Message | None,
) -> str | None:
    if m and hasattr(m, "metadata") and m.metadata and "conversation_id" in m.metadata:
        return m.metadata["conversation_id"]
    return None


def get_project_id(
    m: Task | TaskStatusUpdateEvent | TaskArtifactUpdateEvent | Message | None,
) -> str | None:
    if m and hasattr(m, "metadata") and m.metadata and "project_id" in m.metadata:
        return m.metadata["project_id"]
    return None


def get_user_id(
    m: Task | TaskStatusUpdateEvent | TaskArtifactUpdateEvent | Message | None,
) -> str | None:
    if m and hasattr(m, "metadata") and m.metadata and "user_id" in m.metadata:
        return m.metadata["user_id"]
    return None


def task_still_open(task: Task | None) -> bool:
    if not task:
        return False
    return task.status.state in [
        TaskState.SUBMITTED,
        TaskState.WORKING,
        TaskState.INPUT_REQUIRED,
    ]


def convert_to_langchain_message(message: Message) -> BaseMessage:
    role = message.role if message.role == "user" else "assistant"
    if role == "user":
        return HumanMessage(content=message.parts[0].text)
    else:
        return AIMessage(content=message.parts[0].text)


def convert_to_adk_message(message: BaseMessage) -> Message:
    return Message(
        parts=[TextPart(text=message.content)],
        role=message.role if message.role == "user" else "agent",
    )
