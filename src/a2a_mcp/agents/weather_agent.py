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

        result_text = await self._weather_text(query)
        yield {
            'response_type': 'text',
            'is_task_complete': True,
            'require_user_input': False,
            'content': result_text,
        }

    def invoke(self, query: str, sessionId: str) -> str:
        # Non-streaming path (synchronous facade)
        import asyncio
        return asyncio.run(self._weather_text(query))

    async def _weather_text(self, query: str) -> str:
        city = self._extract_city(query) or 'São Paulo'
        try:
            async with httpx.AsyncClient() as client:
                geo = await client.get(self.geocode_url, params={
                    'name': city,
                    'count': 1,
                    'language': 'pt',
                    'format': 'json'
                })
                geo.raise_for_status()
                g = geo.json()
                if not g.get('results'):
                    return f"Localização não encontrada: {city}"
                res = g['results'][0]
                lat, lon = res['latitude'], res['longitude']

                weather = await client.get(self.base_url, params={
                    'latitude': lat,
                    'longitude': lon,
                    'current': 'temperature_2m,wind_speed_10m,weather_code',
                    'timezone': 'auto'
                })
                weather.raise_for_status()
                w = weather.json()
                cur = w.get('current', {})
                t = cur.get('temperature_2m')
                wind = cur.get('wind_speed_10m')
                code = cur.get('weather_code')
                name = res.get('name')
                country = res.get('country', '')
                return (
                    f"Clima em {name}, {country}: temp={t}°C, "
                    f"vento={wind} km/h, código={code}"
                )
        except Exception as e:
            logger.error(f'WeatherAgent error: {e}')
            return f'Erro ao obter clima: {e}'

    def _extract_city(self, text: str) -> str | None:
        # heurística simples: após 'em '
        t = (text or '').lower()
        marker = 'em '
        if marker in t:
            idx = t.index(marker)
            city = text[idx + len(marker):].strip()
            if city:
                return city
        return None
