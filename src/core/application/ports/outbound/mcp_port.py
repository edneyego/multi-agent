"""
Porta para comunicação via MCP (Model Context Protocol).
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class MCPPort(ABC):
    """Interface para comunicação MCP."""
    
    @abstractmethod
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Chama uma ferramenta via MCP."""
        pass
    
    @abstractmethod
    async def list_tools(self) -> List[Dict[str, Any]]:
        """Lista ferramentas disponíveis."""
        pass
    
    @abstractmethod
    async def get_resource(self, resource_uri: str) -> Optional[Dict[str, Any]]:
        """Obtém um recurso via MCP."""
        pass
    
    @abstractmethod
    async def search_resources(self, query: str) -> List[Dict[str, Any]]:
        """Pesquisa recursos via MCP."""
        pass