# type: ignore
import json
from typing import Any, Dict, Callable, Awaitable
import httpx

class MCPRegistry:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def find_agent_simple(self, query: str) -> Dict[str, Any]:
        """Support both fastMCP HTTP and SSE deployments.
        Try /tools/call → on 404 try /client/tools/call → fallback to read resources.
        """
        payload = {"name": "find_agent_simple", "arguments": {"query": query}}
        async with httpx.AsyncClient(timeout=10.0) as client:
            http_url = f"http://{self.host}:{self.port}/tools/call"
            r = await client.post(http_url, json=payload)
            if r.status_code == 404:
                sse_url = f"http://{self.host}:{self.port}/client/tools/call"
                r2 = await client.post(sse_url, json=payload)
                if r2.status_code == 404:
                    return await self._fallback_read_weather(client)
                r2.raise_for_status()
                data = r2.json()
                return json.loads(data.get("content", [{}])[0].get("text", "{}")) or data
            r.raise_for_status()
            data = r.json()
            return json.loads(data.get("content", [{}])[0].get("text", "{}")) or data

    async def _fallback_read_weather(self, client: httpx.AsyncClient) -> Dict[str, Any]:
        res = await client.get(f"http://{self.host}:{self.port}/resources/read?uri=resource://agent_cards/list")
        if res.status_code == 200:
            try:
                js = res.json()
                text = js.get("contents", [{}])[0].get("text", "{}")
                listing = json.loads(text)
                for uri in listing.get("agent_cards", []):
                    if "weather" in uri.lower():
                        card = await self._read_card(client, uri)
                        if card:
                            return card
            except Exception:
                pass
        return {"error": "Unable to contact MCP server tools"}

    async def _read_card(self, client: httpx.AsyncClient, uri: str) -> Dict[str, Any] | None:
        r = await client.get(f"http://{self.host}:{self.port}/resources/read?uri={uri}")
        if r.status_code == 200:
            js = r.json()
            text = js.get("contents", [{}])[0].get("text", "{}")
            data = json.loads(text)
            cards = data.get("agent_card") or data.get("agent_cards")
            if isinstance(cards, list) and cards:
                return cards[0]
            if isinstance(data, dict) and data.get("name"):
                return data
        return None


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
