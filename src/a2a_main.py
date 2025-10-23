"""
Entry-point para iniciar o servidor A2A (dinâmico) junto com a API principal.
"""
import os
import asyncio
import uvicorn
from loguru import logger
from fastapi import FastAPI

from config.settings import settings
from infrastructure.adapters.inbound.a2a_server import build_asgi_app as build_a2a


def build_main_app() -> FastAPI:
    app = FastAPI(title="Multi-Agent System", version="1.1.0")

    @app.get("/")
    async def root():
        return {
            "system": "Multi-Agent System",
            "version": "1.1.0",
            "agents": ["information", "action", "supervisor", "a2a-dynamic"],
            "endpoints": ["/health", "/status", "/a2a", "/.well-known/agent.json"],
        }

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app


async def main():
    logger.add("logs/multi-agent.log", rotation="1 day", retention="7 days")

    host = settings.a2a_server_host
    port = settings.a2a_server_port

    # Constrói A2A app (Starlette) e monta via Uvicorn separadamente
    a2a_app = build_a2a(host, port)

    config = uvicorn.Config(app=a2a_app, host=host, port=port, log_level=settings.log_level.lower())
    server = uvicorn.Server(config)

    logger.info(f"Starting A2A server on {host}:{port}")
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
