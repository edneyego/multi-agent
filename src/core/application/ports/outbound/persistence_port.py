"""
Porta para persistência de dados.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from ....domain.models import Message, Task, ConversationContext


class PersistencePort(ABC):
    """Interface para persistência de dados."""
    
    @abstractmethod
    async def save_conversation(self, conversation: ConversationContext) -> None:
        """Salva uma conversação."""
        pass
    
    @abstractmethod
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """Recupera uma conversação."""
        pass
    
    @abstractmethod
    async def save_message(self, message: Message) -> None:
        """Salva uma mensagem."""
        pass
    
    @abstractmethod
    async def get_messages(self, conversation_id: str) -> List[Message]:
        """Recupera mensagens de uma conversação."""
        pass
    
    @abstractmethod
    async def save_task(self, task: Task) -> None:
        """Salva uma tarefa."""
        pass
    
    @abstractmethod
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Recupera uma tarefa."""
        pass
    
    @abstractmethod
    async def update_task(self, task: Task) -> None:
        """Atualiza uma tarefa."""
        pass