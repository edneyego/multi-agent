#!/usr/bin/env bash
set -euo pipefail

# Example runner adapted for WeatherAgent (no Google API key required)
# Usage examples:
#  1) Start MCP server (if needed for registry/tools)
#  2) Start WeatherAgent A2A server
#  3) Query via A2A client

ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  uv venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

export PYTHONPATH=$ROOT_DIR/src

# Ports
A2A_HOST="localhost"
A2A_PORT=${A2A_PORT:-10110}

AGENT_CARD="$ROOT_DIR/agent_cards/weather_agent.json"

echo "Starting WeatherAgent on $A2A_HOST:$A2A_PORT with card $AGENT_CARD"
uv run --env-file .env src/a2a_mcp/agents/ --agent-card "$AGENT_CARD" --port "$A2A_PORT"
