# Arquivos de Implementação - Guia de Referência

## 📝 Visão Geral

Este documento lista todos os arquivos de referência fornecidos pelo assistente AI para completar a implementação da arquitetura **LangGraph + MCP**.

## 📁 Arquivos Fornecidos

### 1. Documentação e Planejamento

#### `refactoring-plan.md`
- **Tamanho**: ~25KB
- **Conteúdo**: Plano completo de refatoração
- **Inclui**:
  - Análise detalhada dos problemas
  - Nova arquitetura proposta
  - Estrutura de diretórios
  - Código completo de cada componente
  - Checklist de execução
  - Cronograma estimado (34 horas)
  - Exemplos de uso

#### `refatoracao.sh`
- **Tamanho**: ~8KB  
- **Conteúdo**: Script bash de automação
- **Função**: Automatiza toda a refatoração
- **Fases**:
  1. Backup do código existente
  2. Limpeza de arquivos A2A
  3. Criação da nova estrutura
  4. Geração de arquivos base

### 2. MCP Server

#### `mcp-server-main.py`
- **Destino**: `src/mcp_server/server.py`
- **Tamanho**: ~2KB
- **Conteúdo**: Servidor FastMCP completo
- **Recursos**:
  - Inicialização do servidor
  - Registro de ferramentas
  - Logging estruturado
  - Transporte stdio

```python
# Exemplo de uso
from fastmcp import FastMCP

mcp = FastMCP("Travel Agency MCP Server")

@mcp.tool()
def example_tool(param: str) -> dict:
    return {"result": param}

if __name__ == "__main__":
    mcp.run()
```

#### `weather-tools.py`
- **Destino**: `src/mcp_server/tools/weather_tools.py`
- **Tamanho**: ~6KB
- **Conteúdo**: Ferramentas MCP para clima
- **Ferramentas**:
  - `get_weather(city)` - Clima atual
  - `get_forecast(city, days)` - Previsão
  - `list_available_cities()` - Cidades disponíveis
- **API**: Open-Meteo (pública, sem chave)

```python
# Exemplo de chamada
result = await mcp_client.call_tool(
    "get_weather",
    {"city": "São Paulo"}
)
# {"city": "São Paulo", "temperature": 25, ...}
```

#### `database-tools.py`
- **Destino**: `src/mcp_server/tools/database_tools.py`
- **Tamanho**: ~8KB
- **Conteúdo**: Ferramentas MCP para banco de dados
- **Ferramentas**:
  - `query_travel_bookings(limit, destination, ...)` - Consultar reservas
  - `get_booking_stats()` - Estatísticas gerais
  - `get_destinations_by_popularity(limit)` - Destinos populares
  - `search_customer_bookings(customer_name)` - Buscar por cliente
- **Banco**: SQLite (`travel_agency.db`)

```python
# Exemplo de chamada
result = await mcp_client.call_tool(
    "query_travel_bookings",
    {"limit": 10, "destination": "Paris"}
)
# [{"id": 1, "customer_name": "...", ...}, ...]
```

### 3. Orquestrador LangGraph

#### `supervisor.py`
- **Destino**: `src/orchestrator/supervisor.py`
- **Tamanho**: ~10KB
- **Conteúdo**: Supervisor LangGraph completo
- **Recursos**:
  - Padrão Supervisor
  - Roteamento por keywords
  - Gerenciamento de estado
  - Tratamento de erros
  - Logging detalhado

```python
# Exemplo de uso
from orchestrator.supervisor import Supervisor

supervisor = Supervisor()
result = await supervisor.process("Como está o clima em São Paulo?")
# {"success": True, "data": {...}, "agent": "weather_agent"}
```

**Fluxo do Supervisor**:
```
1. select_agent_node
   │
   ├── Analisa query
   ├── Verifica keywords de cada agente
   └── Seleciona agente apropriado
   │
2. execute_agent_node  
   │
   ├── Executa agente selecionado
   ├── Agente chama ferramentas MCP
   └── Retorna resultado
   │
3. END
```

## 🔧 Como Usar os Arquivos

### Opção 1: Cópia Manual

1. **Baixar os arquivos** fornecidos pelo assistente
2. **Copiar conteúdo** para os destinos corretos:

```bash
# Copiar ferramentas MCP
cp weather-tools.py src/mcp_server/tools/weather_tools.py
cp database-tools.py src/mcp_server/tools/database_tools.py

# Copiar servidor MCP
cp mcp-server-main.py src/mcp_server/server.py

# Copiar supervisor
cp supervisor.py src/orchestrator/supervisor.py
```

3. **Atualizar imports** no servidor:

```python
# Em src/mcp_server/server.py
from .tools.weather_tools import register_weather_tools
from .tools.database_tools import register_database_tools

register_weather_tools(mcp)
register_database_tools(mcp)
```

### Opção 2: Implementação Gradual

1. **Começar com ferramentas simples**:
   - Implementar `weather_tools.py` primeiro
   - Testar isoladamente

2. **Adicionar ferramentas de banco**:
   - Implementar `database_tools.py`
   - Testar integração

3. **Implementar supervisor**:
   - Adicionar `supervisor.py`
   - Testar orquestração completa

## ✅ Checklist de Implementação

### MCP Server
- [ ] Copiar `weather_tools.py`
- [ ] Copiar `database_tools.py`
- [ ] Atualizar `server.py` com registro de ferramentas
- [ ] Testar servidor: `python src/mcp_server/server.py`
- [ ] Verificar logs: ferramentas registradas com sucesso

### Supervisor
- [ ] Copiar `supervisor.py`
- [ ] Verificar imports dos agentes
- [ ] Testar roteamento: query de clima
- [ ] Testar roteamento: query de viagens
- [ ] Testar roteamento: query de planejamento

### Testes de Integração
- [ ] Teste: WeatherAgent + MCP Server
- [ ] Teste: TravelAgent + MCP Server
- [ ] Teste: PlannerAgent + MCP Server
- [ ] Teste: Supervisor + Todos os agentes
- [ ] Teste: Query complexa (múltiplos agentes)

## 📚 Estrutura Final Esperada

```
src/
├── mcp_server/
│   ├── __init__.py                ✅
│   ├── server.py                  ⏳ Atualizar
│   └── tools/
│       ├── __init__.py            ✅
│       ├── weather_tools.py       ⏳ Copiar
│       └── database_tools.py      ⏳ Copiar
│
├── agents/
│   ├── __init__.py                ✅
│   ├── base_agent.py              ✅
│   ├── weather_agent.py           ✅
│   ├── travel_agent.py            ✅
│   └── planner_agent.py           ✅
│
└── orchestrator/
    ├── __init__.py                ✅
    ├── state.py                   ✅
    ├── mcp_client.py              ✅
    └── supervisor.py              ⏳ Copiar
```

## 🚀 Teste Rápido

### 1. Testar MCP Server

```bash
python src/mcp_server/server.py
# Deve exibir:
# 🚀 Iniciando Travel Agency MCP Server
# 📡 Protocolo: MCP (Model Context Protocol)
# ✅ Ferramentas de clima registradas
# ✅ Ferramentas de banco de dados registradas
```

### 2. Testar Agente Individual

```python
import asyncio
from src.agents.weather_agent import WeatherAgent

agent = WeatherAgent()
result = asyncio.run(
    agent.execute("Como está o clima em São Paulo?")
)
print(result)
```

### 3. Testar Supervisor Completo

```python
import asyncio
from src.orchestrator.supervisor import Supervisor

supervisor = Supervisor()

# Teste 1: Clima
result = asyncio.run(
    supervisor.process("Como está o clima em São Paulo?")
)
print("Clima:", result)

# Teste 2: Viagens
result = asyncio.run(
    supervisor.process("Quantas reservas temos no total?")
)
print("Viagens:", result)
```

## 📌 Links Úteis

- **Repositório**: https://github.com/edneyego/multi-agent
- **Branch**: feature/mcpagent
- **FastMCP**: https://github.com/jlowin/fastmcp
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **Open-Meteo API**: https://open-meteo.com/

## ❓ Suporte

Se encontrar problemas:

1. Verifique logs do MCP Server
2. Verifique logs dos agentes
3. Teste cada componente isoladamente
4. Consulte `REFACTORING_SUMMARY.md`
5. Consulte `refactoring-plan.md`

---

**Última atualização**: 14 de novembro de 2025  
**Status**: 🟡 Estrutura completa | Implementação de ferramentas pendente
