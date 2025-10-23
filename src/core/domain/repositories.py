"""
Interfaces (ports) para repositórios de dados.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from .models import Message, Task, ConversationContext


class MessageRepository(ABC):
    """Interface para repositório de mensagens."""
    
    @abstractmethod
    async def save_message(self, message: Message) -> None:
        """Salva uma mensagem."""
        pass
    
    @abstractmethod
    async def get_message(self, message_id: str) -> Optional[Message]:
        """Recupera uma mensagem pelo ID."""
        pass
    
    @abstractmethod
    async def get_messages_by_conversation(self, conversation_id: str) -> List[Message]:
        """Recupera mensagens por conversação."""
        pass


class TaskRepository(ABC):
    """Interface para repositório de tarefas."""
    
    @abstractmethod
    async def save_task(self, task: Task) -> None:
        """Salva uma tarefa."""
        pass
    
    @abstractmethod
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Recupera uma tarefa pelo ID."""
        pass
    
    @abstractmethod
    async def update_task_status(self, task_id: str, status: str, result: Optional[str] = None) -> None:
        """Atualiza o status de uma tarefa."""
        pass
    
    @abstractmethod
    async def get_pending_tasks(self) -> List[Task]:
        """Recupera tarefas pendentes."""
        pass


class ConversationRepository(ABC):
    """Interface para repositório de conversações."""
    
    @abstractmethod
    async def save_conversation(self, conversation: ConversationContext) -> None:
        """Salva uma conversação."""
        pass
    
    @abstractmethod
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """Recupera uma conversação pelo ID."""
        pass
    
    @abstractmethod
    async def update_conversation(self, conversation: ConversationContext) -> None:
        """Atualiza uma conversação."""
        pass
    
    @abstractmethod
    async def delete_conversation(self, conversation_id: str) -> None:
        """Remove uma conversação."""
        pass


class CacheRepository(ABC):
    """Interface para repositório de cache."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Recupera um valor do cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: str, expire: Optional[int] = None) -> None:
        """Define um valor no cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove uma chave do cache."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Verifica se uma chave existe no cache."""
        pass