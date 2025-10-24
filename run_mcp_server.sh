#!/usr/bin/env bash
set -euo pipefail

# Start MCP server for agent discovery and tools

ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  uv venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

export PYTHONPATH=$ROOT_DIR/src

# MCP Server configuration
MCP_HOST="localhost"
MCP_PORT=${MCP_PORT:-10100}

echo "Starting MCP Server on $MCP_HOST:$MCP_PORT"
echo "HTTP Facade will be available on $MCP_HOST:$((MCP_PORT + 1))"

#uv run --env-file .env python -m a2a_mcp --run mcp-server --host "$MCP_HOST" --port "$MCP_PORT" --transport sse

uv run --env-file .env a2a-mcp --run mcp-server --host "$MCP_HOST" --port "$MCP_PORT" --transport sse
