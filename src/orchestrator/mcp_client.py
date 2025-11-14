"""
Cliente MCP para comunicaÃ§Ã£o com MCP Server.

Usado por todos os agentes para acessar ferramentas.
NÃO utiliza protocolo A2A.
"""
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class MCPClient:
    """Cliente para comunicaÃ§Ã£o com MCP Server via protocolo MCP."""
    
    def __init__(self, mcp_command: str = "python", mcp_args: List[str] = None):
        if mcp_args is None:
            mcp_args = ["src/mcp_server/server.py"]
        
        self.server_params = StdioServerParameters(
            command=mcp_command,
            args=mcp_args
        )
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Chama uma ferramenta no MCP Server.
        
        Args:
            tool_name: Nome da ferramenta
            arguments: Argumentos da ferramenta
        
        Returns:
            Resultado da execuÃ§Ã£o da ferramenta
        """
        try:
            async with stdio_client(self.server_params) as (reader, writer):
                async with ClientSession(reader, writer) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)
                    return result
        except Exception as e:
            logger.error(f"Erro ao chamar ferramenta MCP {tool_name}: {e}")
            raise
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        Lista todas as ferramentas disponÃ­veis no MCP Server.
        
        Returns:
            Lista de ferramentas com metadados
        """
        try:
            async with stdio_client(self.server_params) as (reader, writer):
                async with ClientSession(reader, writer) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    return tools
        except Exception as e:
            logger.error(f"Erro ao listar ferramentas MCP: {e}")
            raise
