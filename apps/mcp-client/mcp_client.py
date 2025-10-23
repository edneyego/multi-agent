import asyncio
import json
import typer
from rich import print
import httpx

APP = typer.Typer(help="fastMCP client (calling HTTP endpoints of Weather MCP server)")
BASE_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"


async def geocode(location: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(GEOCODE_URL, params={"name": location, "count": 1, "language": "pt"})
        r.raise_for_status()
        data = r.json()
        if not data.get("results"):
            raise RuntimeError("Localização não encontrada")
        res = data["results"][0]
        return res["latitude"], res["longitude"], res.get("name"), res.get("country", "")


@APP.command()
def weather(location: str = typer.Option(...), days: int = typer.Option(1)):
    async def _run():
        lat, lon, name, country = await geocode(location)
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,wind_speed_10m,weather_code",
            "forecast_days": days,
            "timezone": "auto"
        }
        async with httpx.AsyncClient() as client:
            r = await client.get(BASE_URL, params=params)
            print({"location": f"{name}, {country}", "data": r.json()})
    asyncio.run(_run())


@APP.command()
def decode(code: int):
    codes = {0: "Céu limpo", 63: "Chuva moderada", 65: "Chuva forte"}
    print({"code": code, "desc": codes.get(code, "desconhecido")})


if __name__ == "__main__":
    APP()
