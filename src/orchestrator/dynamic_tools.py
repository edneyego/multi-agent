# type: ignore
import json
from typing import Any, Dict, Callable, Awaitable
import httpx

class MCPRegistry:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def find_agent_simple(self, query: str) -> Dict[str, Any]:
        url = f"http://{self.host}:{self.port}/tools/call"
        payload = {"name": "find_agent_simple", "arguments": {"query": query}}
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            # fastMCP returns content array with text
            return json.loads(data["content"][0]["text"]) if "content" in data else data


class A2AToolFactory:
    def create_tool_for_card(self, agent_card: Dict[str, Any]) -> Callable[[str], Awaitable[Any]]:
        rpc_url = agent_card.get("url", "").rstrip("/") + "/a2a"

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
