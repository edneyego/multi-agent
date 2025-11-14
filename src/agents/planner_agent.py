"""
Planner Agent - Agente especializado em planejamento de viagens.

Combina informaÃ§Ãµes de clima e destinos via MCP.
NÃO utiliza protocolo A2A.
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class PlannerAgent(BaseAgent):
    """Agente especializado em planejamento de viagens."""
    
    def __init__(self, mcp_host: str = "localhost", mcp_port: int = 8000):
        super().__init__(
            name="planner_agent",
            description="Especialista em planejamento de viagens completas",
            mcp_host=mcp_host,
            mcp_port=mcp_port
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "Planejar viagens",
            "Recomendar destinos com base no clima",
            "Combinar informaÃ§Ãµes de mÃºltiplas fontes"
        ]
    
    def _get_keywords(self) -> List[str]:
        return [
            "planejar", "planejamento", "sugerir", "recomendar",
            "roteiro", "itinerÃ¡rio", "organizar"
        ]
    
    async def execute(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executa planejamento de viagem.
        
        Combina dados de clima e destinos populares.
        """
        try:
            logger.info(f"PlannerAgent processando: {query}")
            
            # Obter destinos populares
            popular_destinations = await self.mcp_client.call_tool(
                "get_destinations_by_popularity",
                {"limit": 5}
            )
            
            # Para cada destino, obter clima (simplificado)
            destinations_with_weather = []
            
            if isinstance(popular_destinations, list) and popular_destinations:
                top_destination = popular_destinations[0].get("destination", "Paris")
                
                try:
                    weather = await self.mcp_client.call_tool(
                        "get_weather",
                        {"city": top_destination}
                    )
                    
                    destinations_with_weather.append({
                        "destination": top_destination,
                        "bookings": popular_destinations[0].get("booking_count", 0),
                        "weather": weather
                    })
                except:
                    # Se falhar ao obter clima, continuar sem ele
                    destinations_with_weather.append({
                        "destination": top_destination,
                        "bookings": popular_destinations[0].get("booking_count", 0),
                        "weather": "InformaÃ§Ã£o nÃ£o disponÃ­vel"
                    })
            
            return {
                "success": True,
                "agent": self.name,
                "data": {
                    "popular_destinations": popular_destinations,
                    "recommendations": destinations_with_weather
                }
            }
        
        except Exception as e:
            logger.error(f"Erro no PlannerAgent: {e}")
            return {
                "success": False,
                "agent": self.name,
                "error": str(e)
            }
