"""
Servidor MCP para serviços meteorológicos.
"""
from fastmcp import FastMCP
from typing import Dict, Any
import httpx
import asyncio
from loguru import logger

# Cria instância do servidor MCP
mcp = FastMCP("Weather MCP Server")


@mcp.tool
async def get_weather(location: str, units: str = "metric") -> Dict[str, Any]:
    """
    Obtém informações meteorológicas para uma localização.
    
    Args:
        location: Nome da localização (cidade, país)
        units: Unidades de medida (metric, imperial)
    
    Returns:
        Dicionário com informações meteorológicas
    """
    try:
        # Primeiro, geocodifica a localização
        geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        
        async with httpx.AsyncClient() as client:
            # Geocodificação
            geocoding_params = {
                "name": location,
                "count": 1,
                "language": "pt",
                "format": "json"
            }
            
            geocoding_response = await client.get(geocoding_url, params=geocoding_params)
            geocoding_data = geocoding_response.json()
            
            if not geocoding_data.get("results"):
                return {"error": f"Localização não encontrada: {location}"}
            
            # Obtém coordenadas
            result = geocoding_data["results"][0]
            lat = result["latitude"]
            lon = result["longitude"]
            
            # Consulta meteorológica
            weather_url = "https://api.open-meteo.com/v1/forecast"
            weather_params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                "daily": "temperature_2m_max,temperature_2m_min,weather_code",
                "timezone": "auto",
                "forecast_days": 3
            }
            
            weather_response = await client.get(weather_url, params=weather_params)
            weather_data = weather_response.json()
            
            return {
                "location": {
                    "name": result["name"],
                    "country": result.get("country", ""),
                    "latitude": lat,
                    "longitude": lon
                },
                "current": weather_data.get("current", {}),
                "daily_forecast": weather_data.get("daily", {}),
                "units": weather_data.get("current_units", {}),
                "timezone": weather_data.get("timezone", "")
            }
            
    except Exception as e:
        logger.error(f"Erro na consulta meteorológica: {e}")
        return {"error": f"Erro ao obter clima: {str(e)}"}


@mcp.tool
def decode_weather_code(code: int) -> str:
    """
    Decodifica código meteorológico WMO.
    
    Args:
        code: Código meteorológico WMO
        
    Returns:
        Descrição do clima em português
    """
    weather_codes = {
        0: "Céu limpo",
        1: "Principalmente claro",
        2: "Parcialmente nublado", 
        3: "Nublado",
        45: "Neblina",
        48: "Neblina com geada depositada",
        51: "Garoa: Intensidade leve",
        53: "Garoa: Intensidade moderada",
        55: "Garoa: Intensidade densa",
        61: "Chuva: Intensidade leve",
        63: "Chuva: Intensidade moderada",
        65: "Chuva: Intensidade forte",
        71: "Queda de neve: Intensidade leve",
        73: "Queda de neve: Intensidade moderada",
        75: "Queda de neve: Intensidade forte",
        80: "Pancadas de chuva: Leve",
        81: "Pancadas de chuva: Moderada",
        82: "Pancadas de chuva: Violenta",
        95: "Tempestade: Leve ou moderada",
        96: "Tempestade com granizo leve",
        99: "Tempestade com granizo forte"
    }
    
    return weather_codes.get(code, f"Código desconhecido: {code}")


if __name__ == "__main__":
    mcp.run()