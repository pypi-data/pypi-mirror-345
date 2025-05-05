from abc import ABC, abstractmethod
from google_a2a.common.types import Message, Task, AgentCard

from ephor_cli.conversation_server.types import Conversation, Event


class ApplicationManager(ABC):

    @abstractmethod
    def create_conversation(self, user_id: str, project_id: str) -> Conversation:
        pass

    @abstractmethod
    def list_conversations(self, user_id: str, project_id: str) -> list[Conversation]:
        pass

    @abstractmethod
    def get_conversation(
        self, conversation_id: str, project_id: str, user_id: str
    ) -> Conversation:
        pass

    @abstractmethod
    def delete_conversation(
        self, conversation_id: str, project_id: str, user_id: str
    ) -> bool:
        pass

    @abstractmethod
    def register_agent(
        self, url: str, conversation_id: str, project_id: str, user_id: str
    ) -> AgentCard:
        pass

    @abstractmethod
    def deregister_agent(
        self, agent_id: str, conversation_id: str, project_id: str, user_id: str
    ) -> bool:
        pass

    @abstractmethod
    def list_agents(
        self, user_id: str, project_id: str, conversation_id: str
    ) -> list[AgentCard]:
        pass

    @abstractmethod
    def list_messages(
        self, user_id: str, project_id: str, conversation_id: str
    ) -> list[Message]:
        pass

    @abstractmethod
    def get_pending_messages(
        self, user_id: str, project_id: str, conversation_id: str
    ) -> list[str]:
        pass

    @abstractmethod
    def list_events(
        self, user_id: str, project_id: str, conversation_id: str
    ) -> list[Event]:
        pass

    @abstractmethod
    def list_tasks(
        self, user_id: str, project_id: str, conversation_id: str
    ) -> list[Task]:
        pass

    @abstractmethod
    def sanitize_message(self, message: Message) -> Message:
        pass

    @abstractmethod
    async def process_message(self, message: Message):
        pass
