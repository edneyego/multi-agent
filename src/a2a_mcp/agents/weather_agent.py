# type: ignore

import logging
from collections.abc import AsyncIterable
from typing import Any

import httpx
from a2a_mcp.common.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class WeatherAgent(BaseAgent):
    """Planner replacement that returns weather info without LLM/Google.

    Behaves as a task agent: given a text like 'clima em São Paulo', returns
    current weather from Open-Meteo.
    """

    def __init__(self):
        super().__init__(
            agent_name='WeatherAgent',
            description='Returns current weather for a given city (Open-Meteo)',
            content_types=['text', 'text/plain'],
        )
        self.base_url = 'https://api.open-meteo.com/v1/forecast'
        self.geocode_url = 'https://geocoding-api.open-meteo.com/v1/search'

    async def stream(
        self, query: str, sessionId: str, task_id: str
    ) -> AsyncIterable[dict[str, Any]]:
        """Stream implementation required by the A2A protocol."""
        logger.info(
            f'Running WeatherAgent stream for session {sessionId} {task_id} with input {query}'
        )
        # Emit a working message
        yield {
            'response_type': 'text',
            'is_task_complete': False,
            'require_user_input': False,
            'content': 'Consultando clima...'
        }

        try:
            result_text = await self._weather_text(query)
            yield {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': result_text,
            }
        except Exception as e:
            logger.error(f'Error in WeatherAgent stream: {e}')
            yield {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'Erro ao obter informações do clima: {str(e)}',
            }

    async def invoke(self, query: str, sessionId: str) -> str:
        """Non-streaming implementation for compatibility."""
        logger.info(f'Running WeatherAgent invoke for session {sessionId} with input {query}')
        try:
            return await self._weather_text(query)
        except Exception as e:
            logger.error(f'Error in WeatherAgent invoke: {e}')
            return f'Erro ao obter informações do clima: {str(e)}'

    async def _weather_text(self, query: str) -> str:
        """Get weather information for the given query."""
        city = self._extract_city(query) or 'São Paulo'
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get coordinates from city name
                geo_params = {
                    'name': city,
                    'count': 1,
                    'language': 'pt',
                    'format': 'json'
                }
                geo_response = await client.get(self.geocode_url, params=geo_params)
                geo_response.raise_for_status()
                geo_data = geo_response.json()
                
                if not geo_data.get('results'):
                    return f"Localização não encontrada: {city}"
                    
                location = geo_data['results'][0]
                lat, lon = location['latitude'], location['longitude']
                location_name = location.get('name', city)
                country = location.get('country', '')

                # Get weather data
                weather_params = {
                    'latitude': lat,
                    'longitude': lon,
                    'current': 'temperature_2m,wind_speed_10m,weather_code,relative_humidity_2m',
                    'timezone': 'auto'
                }
                weather_response = await client.get(self.base_url, params=weather_params)
                weather_response.raise_for_status()
                weather_data = weather_response.json()
                
                current = weather_data.get('current', {})
                temperature = current.get('temperature_2m')
                wind_speed = current.get('wind_speed_10m')
                humidity = current.get('relative_humidity_2m')
                weather_code = current.get('weather_code')
                
                # Format response
                result = f"Clima em {location_name}"
                if country:
                    result += f", {country}"
                result += ":\n"
                
                if temperature is not None:
                    result += f"🌡️ Temperatura: {temperature}°C\n"
                if humidity is not None:
                    result += f"💧 Umidade: {humidity}%\n"
                if wind_speed is not None:
                    result += f"💨 Vento: {wind_speed} km/h\n"
                if weather_code is not None:
                    result += f"📊 Código climático: {weather_code}"
                    
                return result.strip()
                
        except httpx.TimeoutException:
            logger.error('Timeout ao conectar com API do clima')
            return f'Timeout ao obter clima para {city}. Tente novamente.'
        except httpx.HTTPError as e:
            logger.error(f'HTTP error ao obter clima: {e}')
            return f'Erro de conexão ao obter clima para {city}: {str(e)}'
        except Exception as e:
            logger.error(f'Erro inesperado no WeatherAgent: {e}')
            return f'Erro inesperado ao obter clima para {city}: {str(e)}'

    def _extract_city(self, text: str) -> str | None:
        """Extract city name from query text."""
        if not text:
            return None
            
        text_lower = text.lower().strip()
        
        # Look for patterns like "clima em São Paulo" or "weather in London"
        markers = ['em ', 'in ', 'de ', 'for ', 'at ']
        
        for marker in markers:
            if marker in text_lower:
                idx = text_lower.index(marker)
                city = text[idx + len(marker):].strip()
                if city:
                    # Remove common suffixes
                    city = city.replace('?', '').replace('.', '').strip()
                    return city
        
        # Fallback: try to extract city from common patterns
        words = text.strip().split()
        if len(words) >= 2:
            # Take the last word(s) as potential city name
            potential_city = ' '.join(words[-2:]) if len(words) >= 2 else words[-1]
            potential_city = potential_city.replace('?', '').replace('.', '').strip()
            if potential_city and len(potential_city) > 2:
                return potential_city
                
        return None