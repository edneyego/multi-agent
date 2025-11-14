"""
Travel Agent - Agente especializado em reservas e informaÃ§Ãµes de viagem.

Utiliza ferramentas MCP para acessar banco de dados.
NÃO utiliza protocolo A2A.
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class TravelAgent(BaseAgent):
    """Agente especializado em reservas de viagem e destinos."""
    
    def __init__(self, mcp_host: str = "localhost", mcp_port: int = 8000):
        super().__init__(
            name="travel_agent",
            description="Especialista em reservas de viagem e destinos",
            mcp_host=mcp_host,
            mcp_port=mcp_port
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "Consultar reservas",
            "Obter estatÃ­sticas",
            "Buscar destinos populares",
            "Pesquisar reservas por cliente"
        ]
    
    def _get_keywords(self) -> List[str]:
        return [
            "reserva", "viagem", "destino", "booking", "hotel", "voo",
            "turismo", "pacote", "estatÃ­stica", "popular", "cliente"
        ]
    
    async def execute(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executa query relacionada a viagens.
        
        Determina tipo de consulta e chama ferramenta MCP apropriada.
        """
        try:
            logger.info(f"TravelAgent processando: {query}")
            
            query_lower = query.lower()
            
            # Determinar tipo de consulta
            if any(word in query_lower for word in ["estatÃ­stica", "total", "quantas", "nÃºmero"]):
                # EstatÃ­sticas gerais
                result = await self.mcp_client.call_tool("get_booking_stats", {})
                query_type = "statistics"
            
            elif any(word in query_lower for word in ["popular", "mais", "top"]):
                # Destinos populares
                result = await self.mcp_client.call_tool(
                    "get_destinations_by_popularity",
                    {"limit": 10}
                )
                query_type = "popular_destinations"
            
            elif any(word in query_lower for word in ["cliente", "nome", "pessoa"]):
                # Buscar por cliente
                customer_name = self._extract_customer_name(query)
                result = await self.mcp_client.call_tool(
                    "search_customer_bookings",
                    {"customer_name": customer_name}
                )
                query_type = "customer_search"
            
            else:
                # Consulta geral de reservas
                result = await self.mcp_client.call_tool(
                    "query_travel_bookings",
                    {"limit": 10}
                )
                query_type = "general_query"
            
            return {
                "success": True,
                "agent": self.name,
                "data": result,
                "query_type": query_type
            }
        
        except Exception as e:
            logger.error(f"Erro no TravelAgent: {e}")
            return {
                "success": False,
                "agent": self.name,
                "error": str(e)
            }
    
    def _extract_customer_name(self, query: str) -> str:
        """
        Extrai nome do cliente da query.
        
        EstratÃ©gia simplificada.
        """
        # Em produÃ§Ã£o, usar NER
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() in ["cliente", "nome", "pessoa"] and i + 1 < len(words):
                return " ".join(words[i+1:i+3])  # PrÃ³ximas 2 palavras
        return ""
