"""
Porta para serviços meteorológicos.
"""
from abc import ABC, abstractmethod
from typing import Optional
from ....domain.models import WeatherQuery, WeatherResponse


class WeatherPort(ABC):
    """Interface para serviços de clima."""
    
    @abstractmethod
    async def get_current_weather(self, query: WeatherQuery) -> WeatherResponse:
        """Obtém clima atual para uma localização."""
        pass
    
    @abstractmethod
    async def get_weather_forecast(self, query: WeatherQuery, days: int = 7) -> WeatherResponse:
        """Obtém previsão do tempo."""
        pass
    
    @abstractmethod
    async def geocode_location(self, location: str) -> tuple[float, float]:
        """Converte endereço em coordenadas."""
        pass