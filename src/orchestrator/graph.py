# type: ignore
import json
from typing import Any, Dict

from langgraph.graph import StateGraph, END
from pydantic import BaseModel

from orchestrator.dynamic_tools import MCPRegistry, A2AToolFactory


class OrchestratorState(BaseModel):
    text: str
    agent_card: Dict[str, Any] | None = None
    agent_output: Any | None = None


class Orchestrator:
    def __init__(self, mcp_host: str = "localhost", mcp_port: int = 10101):
        self.registry = MCPRegistry(mcp_host, mcp_port)
        self.tool_factory = A2AToolFactory()
        self.graph = self._build()

    def _build(self):
        g = StateGraph(OrchestratorState)

        async def find_agent_node(state: OrchestratorState):
            card = await self.registry.find_agent_simple(state.text)
            return {"agent_card": card}

        async def call_agent_node(state: OrchestratorState):
            tool = self.tool_factory.create_tool_for_card(state.agent_card)
            output = await tool(state.text)
            return {"agent_output": output}

        g.add_node("find_agent", find_agent_node)
        g.add_node("call_agent", call_agent_node)
        g.add_edge("find_agent", "call_agent")
        g.add_edge("call_agent", END)
        g.set_entry_point("find_agent")
        return g.compile()

    async def run(self, text: str):
        init = OrchestratorState(text=text)
        result = await self.graph.ainvoke(init)
        return result.agent_output
