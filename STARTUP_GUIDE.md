# Guia de Inicialização do Sistema Multi-Agent

Este guia descreve como inicializar corretamente o sistema multi-agent que demonstra as tecnologias MCP, A2A e LangGraph.

## Arquitetura do Sistema

O sistema consiste em 3 componentes principais:

1. **Servidor MCP** (porta 10100/10101): Registro de agentes e ferramentas
2. **WeatherAgent** (porta 10110): Agente especializado em clima via protocolo A2A
3. **Orquestrador** (porta 10120): API que coordena os agentes via LangGraph

## Pré-requisitos

- Python 3.13+
- `uv` (gerenciador de pacotes)
- Arquivo `.env` configurado (copie de `.env.example`)

## Inicialização Passo a Passo

### Passo 1: Configurar o ambiente

```bash
# Clone e entre no repositório
git clone https://github.com/edneyego/multi-agent.git
cd multi-agent
git checkout new_architecture

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env conforme necessário
```

### Passo 2: Inicializar o Servidor MCP (Terminal 1)

```bash
# Terminal 1 - MCP Server
sh run_mcp_server.sh
```

**Saída esperada:**
```
Starting MCP Server on localhost:10100
HTTP Facade will be available on localhost:10101
```

### Passo 3: Inicializar o WeatherAgent (Terminal 2)

```bash
# Terminal 2 - Weather Agent
sh run_weather_agent.sh
```

**Saída esperada:**
```
Starting WeatherAgent on localhost:10110
INFO:__main__:Starting agent server with card: .../weather_agent.json
INFO:__main__:Successfully created agent: WeatherAgent
INFO:     Uvicorn running on http://localhost:10110
```

### Passo 4: Inicializar o Orquestrador (Terminal 3)

```bash
# Terminal 3 - Orchestrator
sh run_orchestrator.sh
# ou diretamente:
uv run --env-file .env python -m orchestrator.api
```

**Saída esperada:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:10120
```

## Testando o Sistema

### Teste 1: Health Check

```bash
curl http://localhost:10120/health
```

**Resposta esperada:**
```json
{"status": "healthy"}
```

### Teste 2: Consulta de Clima

```bash
curl -X POST http://localhost:10120/query \
  -H "Content-Type: application/json" \
  -d '{"text":"clima em São Paulo"}'
```

**Resposta esperada:**
```json
{
  "ok": true,
  "result": {
    "jsonrpc": "2.0",
    "id": "1",
    "result": {
      "content": "🌡️ Temperatura: 22°C\n💧 Umidade: 65%\n💨 Vento: 10 km/h\n📊 Código climático: 1"
    }
  }
}
```

## Troubleshooting

### Problema: "Could not connect to MCP server"

**Solução:** Certifique-se de que o servidor MCP está rodando na porta 10101:
```bash
curl http://localhost:10101/mcp/tools/call -X POST \
  -H "Content-Type: application/json" \
  -d '{"name": "find_agent_simple", "arguments": {"query": "test"}}'
```

### Problema: "Could not connect to agent"

**Solução:** Verifique se o WeatherAgent está rodando:
```bash
curl http://localhost:10110/ -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": "1", "method": "message", "params": {"message": {"content": {"type": "text", "text": "test"}}}}'
```

### Problema: Erro de import ou dependências

**Solução:** Reinstale as dependências:
```bash
uv sync
uv pip install -r requirements.txt  # se existir
```

## Logs e Debug

Para debugging, você pode aumentar o nível de log:

```bash
# No .env
LOG_LEVEL=DEBUG
A2A_LOG_LEVEL=DEBUG
FASTMCP_LOG_LEVEL=DEBUG
```

## Estrutura de Portas

| Serviço | Porta | Protocolo | Descrição |
|---------|-------|-----------|----------|
| MCP Server | 10100 | SSE | Servidor MCP principal |
| MCP HTTP Facade | 10101 | HTTP | Interface HTTP para MCP |
| WeatherAgent | 10110 | A2A/JSON-RPC | Agente de clima |
| Orchestrator | 10120 | HTTP/REST | API do orquestrador |

## Funcionalidades Testadas

✅ **WeatherAgent**: Consulta clima usando Open-Meteo API
✅ **A2A Protocol**: Comunicação entre agentes via JSON-RPC
✅ **MCP Registry**: Descoberta dinâmica de agentes
✅ **LangGraph**: Orquestração de workflows multi-agent
✅ **Fallback graceful**: Sistema funciona mesmo sem MCP server

## Próximos Passos

Para expandir o sistema:

1. **Adicionar novos agentes**: Crie novos agent cards em `agent_cards/`
2. **Implementar ferramentas MCP**: Adicione tools em `src/a2a_mcp/mcp/server.py`
3. **Workflows complexos**: Expanda o grafo em `src/orchestrator/graph.py`
4. **Interface web**: Adicione frontend para interação visual

## Estrutura de Arquivos Importantes

```
src/
├── orchestrator/           # LangGraph orchestrator
│   ├── api.py             # FastAPI REST interface
│   ├── graph.py           # LangGraph workflow
│   └── dynamic_tools.py   # A2A integration
├── a2a_mcp/
│   ├── agents/            # A2A agents
│   │   ├── weather_agent.py
│   │   └── __main__.py    # Agent runner
│   └── mcp/               # MCP server
│       └── server.py      # MCP registry & tools
agent_cards/               # Agent metadata
└── weather_agent.json    # WeatherAgent configuration
```