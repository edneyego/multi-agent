# type: ignore
import json
from typing import Any, Dict, Callable, Awaitable
import httpx
import logging

logger = logging.getLogger(__name__)

class MCPRegistry:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def find_agent_simple(self, query: str) -> Dict[str, Any]:
        # Use the renamed HTTP facade endpoints (/mcp/tools/call)
        url = f"http://{self.host}:{self.port}/mcp/tools/call"
        payload = {"name": "find_agent_simple", "arguments": {"query": query}}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(url, json=payload)
                r.raise_for_status()
                data = r.json()
                content = data.get("content", [{}])
                if content and len(content) > 0:
                    text_data = content[0].get("text", "{}")
                    return json.loads(text_data) if text_data else {}
                return {}
        except httpx.ConnectError:
            logger.error(f"Could not connect to MCP server at {url}. Is the MCP server running?")
            # Fallback: return WeatherAgent card directly for weather queries
            if any(word in query.lower() for word in ['clima', 'weather', 'tempo']):
                return {
                    "name": "WeatherAgent",
                    "version": "1.0.0",
                    "description": "Task agent that checks current weather for a given city using Open-Meteo (no API key)",
                    "url": "http://localhost:10110/",
                    "capabilities": {
                        "streaming": True,
                        "pushNotifications": True,
                        "stateTransitionHistory": False
                    },
                    "defaultInputModes": ["text", "text/plain"],
                    "defaultOutputModes": ["text", "text/plain"],
                    "skills": [{
                        "id": "weather_query",
                        "name": "Query Weather",
                        "description": "Returns current weather for a city. Input text like: 'clima em São Paulo'",
                        "tags": ["weather", "open-meteo", "public-api"],
                        "examples": ["clima em São Paulo", "weather in London"]
                    }]
                }
            else:
                raise Exception("MCP server not available and no fallback agent for this query type")
        except Exception as e:
            logger.error(f"Error calling MCP server: {e}")
            raise


class A2AToolFactory:
    def create_tool_for_card(self, agent_card: Dict[str, Any]) -> Callable[[str], Awaitable[Any]]:
        base_url = (agent_card.get("url") or "").strip()
        if not (base_url.startswith("http://") or base_url.startswith("https://")):
            raise ValueError(f"Invalid agent card url: {base_url}")
        rpc_url = base_url.rstrip("/") 

        async def tool_call(user_text: str):
            # Use A2A SDK's expected method and params shape
            payload = {
                "jsonrpc": "2.0",
                "id": "1",
                "method": "send_message",
                "params": {
                    "message": {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_text}
                        ]
                    },
                    "stream": False
                },
            }
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    r = await client.post(rpc_url, json=payload)
                    r.raise_for_status()
                    result = r.json()
                    logger.info(f"Agent response: {result}")
                    return result
            except httpx.ConnectError:
                logger.error(f"Could not connect to agent at {rpc_url}. Is the agent running?")
                return {"error": f"Could not connect to agent at {rpc_url}. Please ensure the agent is running."}
            except Exception as e:
                logger.error(f"Error calling agent: {e}")
                return {"error": f"Error calling agent: {str(e)}"}

        return tool_call
