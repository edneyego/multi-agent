import json
import uuid
import httpx
import typer
from rich import print

APP = typer.Typer(help="A2A JSON-RPC client")
BASE_URL = "http://localhost:8000"


@APP.command()
def card():
    """Fetch agent card from /.well-known/agent.json"""
    url = f"{BASE_URL}/.well-known/agent.json"
    r = httpx.get(url)
    print({"status": r.status_code, "card": r.json()})


@APP.command()
def send(text: str = typer.Option(..., help="text content"),
         agent_id: str = typer.Option("dynamic", help="subagent id")):
    """Send a JSON-RPC message to /a2a."""
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message",
        "params": {
            "message": {
                "content": {"type": "text", "text": text}
            },
            "metadata": {"agent_id": agent_id}
        }
    }
    url = f"{BASE_URL}/a2a"
    r = httpx.post(url, json=payload)
    try:
        print(r.json())
    except Exception:
        print(r.text)


if __name__ == "__main__":
    APP()
