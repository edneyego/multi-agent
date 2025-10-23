"""
A2A Server: exposição de um agente A2A dinâmico (Google A2A) com criação de agentes sob demanda.
"""
from __future__ import annotations

import os
import uuid
from typing import Any, Dict, Optional

import uvicorn
from loguru import logger
from starlette.applications import Starlette
from starlette.routing import Mount

# Tentamos usar o SDK oficial python-a2a (ou a2a-sdk).
# O código abaixo tenta ser compatível com as variantes vistas nos tutoriais.
try:
    # Variante 1 (a2a-python SDK community)
    from a2a.server.apps import A2AStarletteApplication
    from a2a.server.request_handlers import DefaultRequestHandler
    from a2a.server.tasks import (
        InMemoryTaskStore,
        InMemoryPushNotificationConfigStore,
        BasePushNotificationSender,
    )
    from a2a.types import AgentCard, AgentCapabilities, AgentSkill
    A2A_AVAILABLE = True
except Exception:
    try:
        # Variante 2 (python-a2a - nomes podem diferir; ajuste se necessário)
        from python_a2a.server.apps import A2AStarletteApplication  # type: ignore
        from python_a2a.server.request_handlers import DefaultRequestHandler  # type: ignore
        from python_a2a.server.tasks import (  # type: ignore
            InMemoryTaskStore,
            InMemoryPushNotificationConfigStore,
            BasePushNotificationSender,
        )
        from python_a2a.types import AgentCard, AgentCapabilities, AgentSkill  # type: ignore
        A2A_AVAILABLE = True
    except Exception:
        A2A_AVAILABLE = False

if not A2A_AVAILABLE:
    raise RuntimeError(
        "A2A SDK não disponível. Instale um dos SDKs suportados, por exemplo: \n"
        "  pip install python-a2a  \n"
        "ou  pip install a2a-sdk\n"
    )

import httpx


class DynamicAgentExecutor:
    """
    Executor simples que delega tarefas a um agente LangGraph local, MCP ou tool externa.
    Aqui, simulamos a execução; na sua POC, conecte aos agentes reais (information/action).
    """

    def __init__(self, factory: "DynamicAgentFactory") -> None:
        self.factory = factory

    async def execute(self, context: Dict[str, Any], event_queue: Any) -> Dict[str, Any]:
        # Contexto mínimo: {"task": {"message": {"content": {"text": "..."}}}}
        task = context.get("task", {})
        message = task.get("message", {})
        content = message.get("content", {})
        text = content.get("text") if isinstance(content, dict) else None
        agent_id = task.get("agent_id") or "dynamic"

        logger.info(f"Executando task no agente {agent_id} com entrada: {text}")

        # Roteia para um agente dinâmico (ex: weather, info, mcp)
        agent = await self.factory.get_or_create_agent(agent_id)
        response_text = await agent.handle(text or "")

        # Exemplo de retorno A2A com artifact simples de texto
        return {
            "artifacts": [
                {
                    "parts": [
                        {"type": "text", "text": response_text},
                    ]
                }
            ],
            "status": {"state": "COMPLETED"},
        }


class DynamicAgent:
    """Agente simples de demonstração que decide comportamento pelo prefixo do texto."""

    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id

    async def handle(self, text: str) -> str:
        t = (text or "").lower()
        if t.startswith("clima") or "weather" in t:
            return "Consulta de clima recebida. Integre WeatherAdapter/MCP aqui para dados reais."
        if t.startswith("info") or "documentação" in t:
            return "Consulta informacional recebida. Integre InformationAgent (RAG) aqui."
        if t.startswith("calc") or any(op in t for op in ["+", "-", "*", "/"]):
            return "Cálculo solicitado. Integre MCP.calculate aqui."
        return f"Agente {self.agent_id} respondeu: '{text}'."


class DynamicAgentFactory:
    """Cria e gerencia instâncias de agentes dinâmicos sob demanda."""

    def __init__(self) -> None:
        self._agents: Dict[str, DynamicAgent] = {}

    async def get_or_create_agent(self, agent_id: str) -> DynamicAgent:
        if agent_id not in self._agents:
            self._agents[agent_id] = DynamicAgent(agent_id)
        return self._agents[agent_id]


def build_dynamic_agent_card(base_url: str) -> AgentCard:
    """Cria AgentCard com skill de criação dinâmica e streaming/push ativados."""
    return AgentCard(
        name="Dynamic A2A Agent",
        description="Agente A2A que cria subagentes dinamicamente (weather/info/mcp).",
        url=base_url.rstrip("/") + "/a2a",
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=True, push_notifications=True),
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[
            AgentSkill(
                id="dynamic_create",
                name="Create Dynamic Agent",
                description=(
                    "Cria (ou reutiliza) um subagente on-demand e executa a tarefa. "
                    "Use task.metadata.agent_id para endereçar o subagente."
                ),
                tags=["dynamic", "supervisor", "router"],
            )
        ],
    )


def build_asgi_app(host: str = "0.0.0.0", port: int = 8000) -> Starlette:
    """Monta a aplicação Starlette com o A2A app montado em /a2a e card em /.well-known/agent.json."""
    base_url = os.getenv("A2A_BASE_URL", f"http://{host}:{port}")

    factory = DynamicAgentFactory()
    executor = DynamicAgentExecutor(factory)

    httpx_client = httpx.AsyncClient()

    request_handler = DefaultRequestHandler(
        agent_executor=executor,  # nosso executor customizado
        task_store=InMemoryTaskStore(),
        push_config_store=InMemoryPushNotificationConfigStore(),
        push_sender=BasePushNotificationSender(httpx_client=httpx_client),
    )

    a2a_app = A2AStarletteApplication(
        agent_card=build_dynamic_agent_card(base_url),
        http_handler=request_handler,
    ).build(rpc_url="/a2a")

    app = Starlette(routes=[Mount("/", app=a2a_app)])
    return app


if __name__ == "__main__":
    host = os.getenv("A2A_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("A2A_SERVER_PORT", "8000"))
    uvicorn.run(build_asgi_app(host, port), host=host, port=port)
