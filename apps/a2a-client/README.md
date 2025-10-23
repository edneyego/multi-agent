# A2A Client (JSON-RPC)

A minimal A2A JSON-RPC client to talk to the dynamic A2A server running at http://localhost:8000.

## Install

```bash
pip install httpx rich typer
```

## Usage

```bash
python a2a_client.py send --text "clima em São Paulo" --agent-id weather-01
python a2a_client.py send --text "calc 25 * 4 + 10" --agent-id calc-01
python a2a_client.py card
```
