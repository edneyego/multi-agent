# LangGraph Dynamic Orchestrator (A2A + MCP)

POC minimalista que demonstra:

- Orquestração com LangGraph
- Descoberta de agentes via MCP (Agent Cards)
- Execução dinâmica de agentes A2A (ex.: WeatherAgent)
- Zero dependência de Google (usa APIs públicas gratuitas)

## Visão Geral

Fluxo:
1. Usuário envia uma consulta (ex.: "clima em São Paulo")
2. Orquestrador LangGraph chama MCP `find_agent_simple` para descobrir o agente
3. Cria uma tool dinâmica A2A para esse agente
4. Chama o agente via A2A e retorna a resposta final

## Como Rodar

Pré-requisitos: Python 3.11+, `uv` (opcional), `httpx`, `uvicorn`, `fastapi`, `langgraph`

1) Suba o MCP Server (SSE) com cards
```bash
uv run --env-file .env a2a-mcp --run mcp-server --transport sse
# Alternativa: python src/a2a_mcp/mcp/server.py (se exposto como script)
```

2) Suba o WeatherAgent (A2A)
```bash
./run_weather_agent.sh
# Card: http://localhost:10110/.well-known/agent.json
# RPC : http://localhost:10110
```

3) Suba o Orquestrador LangGraph
```bash
./run_orchestrator.sh
# Endpoint: POST http://localhost:10120/query  {"text":"clima em São Paulo"}
```

4) (Opcional) Teste o MCP Client
```bash
uv run --env-file .env src/a2a_mcp/mcp/client.py --resource list
uv run --env-file .env src/a2a_mcp/mcp/client.py --find_agent "clima"
uv run --env-file .env src/a2a_mcp/mcp/client.py --tool_name weather --city "São Paulo"
```

## Estrutura

- agent_cards/*.json  (cards servidos pelo MCP)
- src/orchestrator/graph.py (LangGraph orquestrando)
- src/orchestrator/dynamic_tools.py (fábrica de tools A2A dinâmicas)
- src/a2a_mcp/mcp/server.py (MCP server sem Google)
- src/a2a_mcp/mcp/client.py (MCP client sem Google)
- src/a2a_mcp/agents/weather_agent.py (Agente A2A de clima)
- run_weather_agent.sh, run_orchestrator.sh (scripts)

## Observações

- Sem GOOGLE_API_KEY, sem Places, sem embeddings proprietários.
- Seleção simples de agente por keywords via MCP `find_agent_simple`.
- Fácil de estender: adicione um card em agent_cards/ e suba um novo agente A2A.
