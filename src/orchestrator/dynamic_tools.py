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
            # First try the strict schema required by your A2A SDK (requires messageId and parts)
            payload_send = {
                "jsonrpc": "2.0",
                "id": "1",
                "method": "message/send",
                "params": {
                    "message": {
                        "messageId": "client-1",
                        "role": "user",
                        "parts": [
                            {"type": "text", "text": user_text}
                        ]
                    },
                    "stream": False
                },
            }

            last_error = None
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    try:
                        logger.info(f"Trying A2A call to {rpc_url} with method={payload_send['method']}")
                        r = await client.post(rpc_url, json=payload_send)
                        r.raise_for_status()
                        result = r.json()
                        # If JSON-RPC error present, decide whether to fallback
                        if isinstance(result, dict) and result.get("error"):
                            code = result["error"].get("code")
                            # -32601: Method not found -> try next payload
                            # -32602: Invalid params -> try next payload
                            if code in (-32601, -32602):
                                last_error = result
                                logger.warning(f"A2A error code {code} for {payload_send['method']}, trying fallback if available...")
                        logger.info(f"Agent response: {result}")
                        return result
                    except httpx.HTTPStatusError as he:
                        last_error = {"error": {"code": he.response.status_code, "message": he.response.text}}
                        logger.error(f"HTTP error calling agent: {last_error}")
            except httpx.ConnectError:
                logger.error(f"Could not connect to agent at {rpc_url}. Is the agent running?")
                return {"error": f"Could not connect to agent at {rpc_url}. Please ensure the agent is running."}
            except Exception as e:
                logger.error(f"Error calling agent: {e}")
                return {"error": f"Error calling agent: {str(e)}"}
            # If reached here, both attempts failed
            return last_error or {"error": "Unknown error calling agent"}

        return tool_call
