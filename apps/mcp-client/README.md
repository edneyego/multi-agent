# MCP Client (fastMCP)

A minimal client that uses fastMCP to call tools on the Weather MCP server.

## Install

```bash
pip install fastmcp rich typer httpx
```

## Usage

Start the weather MCP server in another terminal:

```bash
python src/mcp_servers/weather_server.py
```

Then call tools:

```bash
python mcp_client.py weather --location "São Paulo"
python mcp_client.py decode --code 63
```
