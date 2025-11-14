"""
Weather Agent - Agente especializado em informaÃ§Ãµes climÃ¡ticas.

Utiliza ferramentas MCP para obter dados climÃ¡ticos.
NÃO utiliza protocolo A2A.
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
import re
import logging

logger = logging.getLogger(__name__)

class WeatherAgent(BaseAgent):
    """Agente especializado em clima e previsÃ£o do tempo."""
    
    def __init__(self, mcp_host: str = "localhost", mcp_port: int = 8000):
        super().__init__(
            name="weather_agent",
            description="Especialista em clima e previsÃ£o do tempo",
            mcp_host=mcp_host,
            mcp_port=mcp_port
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "Obter clima atual",
            "Obter previsÃ£o do tempo",
            "Comparar clima entre cidades",
            "Listar cidades disponÃ­veis"
        ]
    
    def _get_keywords(self) -> List[str]:
        return ["clima", "weather", "tempo", "temperatura", "previsÃ£o", "chuva", "sol"]
    
    async def execute(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executa query relacionada ao clima.
        
        Extrai a cidade da query e chama ferramenta MCP apropriada.
        """
        try:
            logger.info(f"WeatherAgent processando: {query}")
            
            # Extrair cidade da query
            city = self._extract_city(query)
            
            if not city:
                return {
                    "success": False,
                    "agent": self.name,
                    "error": "NÃ£o foi possÃ­vel identificar a cidade na query"
                }
            
            # Determinar se Ã© previsÃ£o ou clima atual
            if any(word in query.lower() for word in ["previsÃ£o", "prÃ³ximos", "amanhÃ£"]):
                # Chamar ferramenta de previsÃ£o
                result = await self.mcp_client.call_tool(
                    "get_forecast",
                    {"city": city, "days": 3}
                )
            else:
                # Chamar ferramenta de clima atual
                result = await self.mcp_client.call_tool(
                    "get_weather",
                    {"city": city}
                )
            
            return {
                "success": True,
                "agent": self.name,
                "data": result,
                "query_city": city
            }
        
        except Exception as e:
            logger.error(f"Erro no WeatherAgent: {e}")
            return {
                "success": False,
                "agent": self.name,
                "error": str(e)
            }
    
    def _extract_city(self, query: str) -> str:
        """
        Extrai nome da cidade da query.
        
        EstratÃ©gia simples: busca palavras capitalizadas.
        Em produÃ§Ã£o, usar NER ou LLM.
        """
        # PadrÃµes comuns
        patterns = [
            r"em ([A-ZÃ][a-zÃ¡Ã©Ã­Ã³ÃºÃ§Ã£Ãµ]+(?:\s+[A-ZÃ][a-zÃ¡Ã©Ã­Ã³ÃºÃ§Ã£Ãµ]+)?)",
            r"de ([A-ZÃ][a-zÃ¡Ã©Ã­Ã³ÃºÃ§Ã£Ãµ]+(?:\s+[A-ZÃ][a-zÃ¡Ã©Ã­Ã³ÃºÃ§Ã£Ãµ]+)?)",
            r"para ([A-ZÃ][a-zÃ¡Ã©Ã­Ã³ÃºÃ§Ã£Ãµ]+(?:\s+[A-ZÃ][a-zÃ¡Ã©Ã­Ã³ÃºÃ§Ã£Ãµ]+)?)",
            r"in ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1)
        
        # Fallback: primeira palavra capitalizada
        words = query.split()
        for word in words:
            if word and word[0].isupper():
                return word
        
        return "SÃ£o Paulo"  # Default
