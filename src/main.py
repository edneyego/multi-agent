"""
Ponto de entrada principal do sistema multi-agent.
"""
import asyncio
import uvicorn
from loguru import logger
from fastapi import FastAPI

from config.settings import settings


class MultiAgentSystem:
    """Sistema multi-agent principal."""
    
    def __init__(self):
        self.app = None
        
    async def initialize(self):
        """Inicializa o sistema."""
        try:
            logger.info("Initializing Multi-Agent System...")
            
            # Cria aplicação FastAPI
            self.app = FastAPI(
                title="Multi-Agent System",
                description="Sistema multi-agent com LangGraph, MCP e A2A",
                version="1.0.0"
            )
            
            # Configura rotas básicas
            self._setup_routes()
            
            logger.success("Multi-Agent System initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize system: {e}")
            raise
    
    def _setup_routes(self):
        """Configura rotas da aplicação."""
        
        @self.app.get("/")
        async def root():
            """Endpoint raiz."""
            return {
                "system": "Multi-Agent System",
                "version": "1.0.0",
                "agents": ["information", "action", "supervisor"],
                "protocols": ["A2A", "MCP", "LangGraph"],
                "status": "active"
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "system": "multi-agent",
                "version": "1.0.0"
            }
        
        @self.app.get("/status")
        async def system_status():
            """Status detalhado do sistema."""
            return {
                "system": "Multi-Agent System",
                "components": {
                    "information_agent": "active",
                    "action_agent": "active", 
                    "supervisor_agent": "active",
                    "redis": "connected",
                    "mcp_servers": "available"
                },
                "protocols": ["A2A", "MCP", "LangGraph"]
            }
        
        @self.app.post("/query")
        async def process_query(request: dict):
            """Processa consulta direta."""
            query = request.get("query", "")
            
            if not query:
                return {"error": "Query is required"}
            
            # Por enquanto, retorna resposta simulada
            return {
                "success": True,
                "response": f"Processando consulta: {query}",
                "agent_used": "supervisor",
                "status": "completed"
            }
    
    async def start_server(self):
        """Inicia o servidor."""
        config = uvicorn.Config(
            self.app,
            host=settings.a2a_server_host,
            port=settings.a2a_server_port,
            log_level=settings.log_level.lower()
        )
        
        server = uvicorn.Server(config)
        await server.serve()


async def main():
    """Função principal."""
    # Configura logging
    logger.add("logs/multi-agent.log", rotation="1 day", retention="7 days")
    
    system = MultiAgentSystem()
    
    try:
        await system.initialize()
        logger.info(f"Starting server on {settings.a2a_server_host}:{settings.a2a_server_port}")
        await system.start_server()
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"System error: {e}")


if __name__ == "__main__":
    asyncio.run(main())