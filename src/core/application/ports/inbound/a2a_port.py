"""
Porta de entrada para protocolo A2A.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from ....domain.models import Message, AgentResponse


class A2APort(ABC):
    """Interface para comunicação A2A."""
    
    @abstractmethod
    async def process_message(self, message: Message) -> AgentResponse:
        """Processa uma mensagem A2A."""
        pass
    
    @abstractmethod
    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """Retorna as capacidades do agente."""
        pass
    
    @abstractmethod
    async def handle_handoff(self, source_agent: str, target_agent: str, context: Dict[str, Any]) -> AgentResponse:
        """Gerencia transferência entre agentes."""
        pass