"""
Exemplo de A2A Agent específico (WeatherAgent) exposto dentro do servidor dinâmico.
Este agente é instanciado sob demanda com agent_id="weather-<n>" e integra Open-Meteo.
"""
from __future__ import annotations

import httpx
from typing import Any
from loguru import logger


class WeatherAgent:
    def __init__(self, name: str = "weather-agent") -> None:
        self.name = name
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

    async def get_weather_text(self, location: str) -> str:
        try:
            async with httpx.AsyncClient() as client:
                geo = await client.get(self.geocoding_url, params={"name": location, "count": 1, "language": "pt"})
                geo.raise_for_status()
                data = geo.json()
                if not data.get("results"):
                    return f"Localização não encontrada: {location}"
                res = data["results"][0]
                lat, lon = res["latitude"], res["longitude"]
                w = await client.get(self.base_url, params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,wind_speed_10m,weather_code",
                    "timezone": "auto"
                })
                w.raise_for_status()
                wd = w.json()
                cur = wd.get("current", {})
                t = cur.get("temperature_2m")
                wind = cur.get("wind_speed_10m")
                code = cur.get("weather_code")
                return f"Clima em {res.get('name')}, {res.get('country', '')}: temp={t}°C, vento={wind} km/h, código={code}"
        except Exception as e:
            logger.error(f"Erro WeatherAgent: {e}")
            return f"Erro obtendo clima: {e}"

    async def handle(self, text: str) -> str:
        # Extrai uma localização simples do texto
        # Exemplos: "clima em São Paulo" / "weather Rio de Janeiro"
        tokens = text.split()
        if "em" in tokens:
            idx = tokens.index("em")
            location = " ".join(tokens[idx+1:]) or "São Paulo"
        else:
            location = "São Paulo"
        return await self.get_weather_text(location)
