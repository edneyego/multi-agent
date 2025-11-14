"""
Classe base para todos os agentes especializados.

Todos os agentes herdam desta classe e sÃ£o clientes MCP.
NÃO utiliza protocolo A2A.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from orchestrator.mcp_client import MCPClient
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Classe base abstrata para agentes especializados."""
    
    def __init__(self, name: str, description: str, mcp_host: str = "localhost", mcp_port: int = 8000):
        """
        Inicializa o agente.
        
        Args:
            name: Nome Ãºnico do agente
            description: DescriÃ§Ã£o das capacidades
            mcp_host: Host do MCP Server (nÃ£o usado com stdio)
            mcp_port: Porta do MCP Server (nÃ£o usado com stdio)
        """
        self.name = name
        self.description = description
        self.mcp_client = MCPClient()
        logger.info(f"â Agente {name} inicializado")
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Retorna lista de capacidades do agente.
        
        Returns:
            Lista de strings descrevendo as capacidades
        """
        pass
    
    @abstractmethod
    async def execute(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executa a lÃ³gica principal do agente.
        
        Args:
            query: Query do usuÃ¡rio em linguagem natural
            context: Contexto adicional (opcional)
        
        Returns:
            Resultado da execuÃ§Ã£o contendo:
            - success: bool
            - data: Any
            - agent: str
            - error: str (opcional)
        """
        pass
    
    def matches_query(self, query: str) -> bool:
        """
        Verifica se este agente pode processar a query.
        
        Args:
            query: Query do usuÃ¡rio
        
        Returns:
            True se o agente pode processar, False caso contrÃ¡rio
        """
        keywords = self._get_keywords()
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in keywords)
    
    @abstractmethod
    def _get_keywords(self) -> List[str]:
        """
        Retorna palavras-chave que identificam este agente.
        
        Returns:
            Lista de palavras-chave em minÃºsculas
        """
        pass
