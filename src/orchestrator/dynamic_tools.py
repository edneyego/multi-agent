# type: ignore
import json
from typing import Any, Dict, Callable, Awaitable
import httpx

class MCPRegistry:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def find_agent_simple(self, query: str) -> Dict[str, Any]:
        # Use the renamed HTTP facade endpoints (/mcp/tools/call)
        url = f"http://{self.host}:{self.port}/mcp/tools/call"
        payload = {"name": "find_agent_simple", "arguments": {"query": query}}
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            return json.loads(data.get("content", [{}])[0].get("text", "{}")) or data


class A2AToolFactory:
    def create_tool_for_card(self, agent_card: Dict[str, Any]) -> Callable[[str], Awaitable[Any]]:
        base_url = (agent_card.get("url") or "").strip()
        if not (base_url.startswith("http://") or base_url.startswith("https://")):
            raise ValueError(f"Invalid agent card url: {base_url}")
        rpc_url = base_url.rstrip("/") 

        async def tool_call(user_text: str):
            payload = {
                "jsonrpc": "2.0",
                "id": "1",
                "method": "message",
                "params": {
                    "message": {"content": {"type": "text", "text": user_text}}
                },
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(rpc_url, json=payload)
                r.raise_for_status()
                return r.json()

        return tool_call
