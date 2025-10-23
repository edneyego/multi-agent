#!/usr/bin/env bash
set -euo pipefail

# Orchestrator runner (LangGraph) - minimal HTTP API
# Starts FastAPI app exposing /query which routes via MCP and calls A2A agent dynamically

ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
export PYTHONPATH=$ROOT_DIR/src

uv run --env-file .env python -m orchestrator.api
