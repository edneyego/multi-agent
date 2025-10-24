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
            try:
                card = await self.registry.find_agent_simple(state.text)
                return {"agent_card": card}
            except Exception as e:
                print(f"Error finding agent: {e}")
                return {"agent_card": None}

        async def call_agent_node(state: OrchestratorState):
            try:
                if state.agent_card is None:
                    return {"agent_output": {"error": "No agent found for this query"}}
                
                tool = self.tool_factory.create_tool_for_card(state.agent_card)
                output = await tool(state.text)
                return {"agent_output": output}
            except Exception as e:
                print(f"Error calling agent: {e}")
                return {"agent_output": {"error": f"Error calling agent: {str(e)}"}}

        g.add_node("find_agent", find_agent_node)
        g.add_node("call_agent", call_agent_node)
        g.add_edge("find_agent", "call_agent")
        g.add_edge("call_agent", END)
        g.set_entry_point("find_agent")
        return g.compile()

    async def run(self, text: str):
        try:
            init = OrchestratorState(text=text)
            result = await self.graph.ainvoke(init)
            
            # LangGraph returns a dictionary, not an object with attributes
            # Access the agent_output key from the result dictionary
            return result.get("agent_output", {"error": "No output from agent"})
        except Exception as e:
            print(f"Error in orchestrator run: {e}")
            return {"error": f"Orchestrator error: {str(e)}"}