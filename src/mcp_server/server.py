"""
MCP Server - Servidor FastMCP centralizado de ferramentas

Este servidor expõe ferramentas via protocolo MCP que são consumidas
por todos os agentes especializados. Não há comunicação A2A.
"""

from fastmcp import FastMCP
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar servidor MCP
mcp = FastMCP(
    "Travel Agency MCP Server",
    description="Servidor centralizado de ferramentas para sistema multi-agente"
)

# TODO: Registrar ferramentas de diferentes domínios
# from .tools.weather_tools import register_weather_tools
# from .tools.database_tools import register_database_tools
# from .tools.travel_tools import register_travel_tools

# register_weather_tools(mcp)
# register_database_tools(mcp)
# register_travel_tools(mcp)

logger.info("❌ ATENÇÃO: Ferramentas MCP ainda não implementadas")
logger.info("📝 Copie o conteúdo dos arquivos fornecidos:")
logger.info("   - weather-tools.py -> src/mcp_server/tools/weather_tools.py")
logger.info("   - database-tools.py -> src/mcp_server/tools/database_tools.py")

def main():
    """Inicia o MCP Server."""
    logger.info("🚀 Iniciando Travel Agency MCP Server")
    logger.info("📡 Protocolo: MCP (Model Context Protocol)")
    logger.info("🔧 Implementação: FastMCP puro (SEM A2A)")
    logger.info("🚀 Transporte: stdio")
    
    # Iniciar servidor
    mcp.run()

if __name__ == "__main__":
    main()
