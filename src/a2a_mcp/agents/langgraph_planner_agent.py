# type: ignore

import logging
import os

from collections.abc import AsyncIterable
from typing import Any, Literal

from a2a_mcp.common import prompts
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.types import TaskList
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field


memory = MemorySaver()
logger = logging.getLogger(__name__)


class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    question: str = Field(
        description='Input needed from the user to generate the plan'
    )
    content: TaskList = Field(
        description='List of tasks when the plan is generated'
    )


class LangGraphPlannerAgent(BaseAgent):
    """Planner Agent backed by LangGraph (no Google dependency)."""

    def __init__(self):
        logger.info('Initializing LanggraphPlannerAgent (no Google)')

        super().__init__(
            agent_name='PlannerAgent',
            description='Breakdown the user request into executable tasks',
            content_types=['text', 'text/plain'],
        )

        # Simple echo/planner placeholder without external LLM:
        # Keeps LangGraph wiring for compatibility; tools list is empty.
        # In a follow-up commit, this can be replaced by a local model provider if desired.
        self.model = None
        self.graph = None

    def invoke(self, query, sessionId) -> str:
        # Minimal deterministic planning fallback
        plan = self._simple_plan(query)
        return {
            'response_type': 'data',
            'is_task_complete': True,
            'require_user_input': False,
            'content': plan,
        }

    async def stream(
        self, query, sessionId, task_id
    ) -> AsyncIterable[dict[str, Any]]:
        logger.info(
            f'Running LanggraphPlannerAgent stream (no Google) for session {sessionId} {task_id} with input {query}'
        )
        yield {
            'response_type': 'text',
            'is_task_complete': False,
            'require_user_input': False,
            'content': 'Gerando plano (modo offline, sem LLM)...',
        }
        yield self.invoke(query, sessionId)

    def _simple_plan(self, query: str) -> dict[str, Any]:
        # Very naive task splitting as placeholder; customize as needed
        tasks = []
        q = (query or '').lower()
        if 'clima' in q or 'weather' in q:
            tasks.append({'task': 'Consultar clima', 'agent': 'WeatherAgent'})
        else:
            tasks.append({'task': 'Executar tarefa', 'agent': 'Orchestrator Agent'})
        return {'tasks': tasks}
