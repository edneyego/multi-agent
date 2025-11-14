"""
Estado compartilhado do orquestrador LangGraph.

NÃO utiliza protocolo A2A - apenas LangGraph + MCP.
"""
from typing import TypedDict, Any, List, Optional

class OrchestratorState(TypedDict):
    """Estado compartilhado no grafo LangGraph."""
    query: str
    selected_agent: Optional[str]
    agent_result: Optional[Any]
    messages: List[str]
    error: Optional[str]
