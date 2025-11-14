# Sistema Multi-Agente: LangGraph + MCP

> 🎯 **Branch `feature/mcpagent`** - Arquitetura simplificada usando apenas LangGraph + MCP

Uma implementação prática de sistema multi-agente utilizando **LangGraph** para orquestração e **FastMCP** para acesso centralizado a ferramentas, **sem utilizar o protocolo A2A**.

## 🎆 Arquitetura Simplificada

Esta branch implementa uma arquitetura mais simples e eficiente, removendo a complexidade do protocolo A2A:

✅ **LangGraph** - Orquestração de agentes com padrão Supervisor  
✅ **FastMCP puro** - Servidor centralizado de ferramentas  
✅ **Arquitetura limpa** - Sem protocolos redundantes  
✅ **Fácil manutenção** - Código simplificado  
✅ **Alta performance** - Menos overhead de comunicação  

## Diagrama de Arquitetura

![Arquitetura](https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/a10399ee7bf597230685b991b56cf8d1/d789bb19-3a0e-43d9-969c-a6a6269a4b67/059b4cc6.png)

## Arquitetura Detalhada

```
┌─────────────────────────────────────────────────────────────┐
│                    CANAIS DE ENTRADA                         │
│          Web │ API REST │ CLI │ Chat Interface              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              ORQUESTRADOR LANGGRAPH                          │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  Supervisor Agent (Padrão Supervisor)               │   │
│  │  • Analisa intenção do usuário                      │   │
│  │  • Seleciona agente especializado                   │   │
│  │  • Gerencia fluxo de conversação                    │   │
│  │  • Consolida respostas                              │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │              │              │              │
           ▼              ▼              ▼              ▼
  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
  │   Weather   │ │ Information │ │    Data     │ │   Finance   │
  │    Agent    │ │    Agent    │ │    Agent    │ │    Agent    │
  │             │ │             │ │             │ │             │
  │ • Clima     │ │ • RAG       │ │ • Análise   │ │ • Cálculos  │
  │ • Previsão  │ │ • Busca     │ │ • SQL       │ │ • Conversão │
  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
           ▲              ▲              ▲              ▲
           │              │              │              │
           └──────────────┴──────────────┴──────────────┘
                              │
                              ▼
           ┌──────────────────────────────────────────┐
           │         MCP SERVER (FastMCP)             │
           │  ┌────────────────────────────────────┐ │
           │  │ FERRAMENTAS (Tools)                │ │
           │  │ • get_weather                      │ │
           │  │ • query_database                   │ │
           │  │ • search_information               │ │
           │  │ • calculate_finance                │ │
           │  │ • process_data                     │ │
           │  └────────────────────────────────────┘ │
           │  ┌────────────────────────────────────┐ │
           │  │ RECURSOS (Resources)               │ │
           │  │ • agent_cards                      │ │
           │  │ • system_status                    │ │
           │  │ • database_schema                  │ │
           │  └────────────────────────────────────┘ │
           └──────────────────────────────────────────┘
                              │
                              ▼
           ┌──────────────────────────────────────────┐
           │           FONTES DE DADOS                │
           │  SQLite │ APIs │ Knowledge Base │ Files  │
           └──────────────────────────────────────────┘
```

### Componentes Principais

#### 1. Orquestrador LangGraph (Supervisor)

- **Responsabilidade**: Gerencia todo o fluxo de interação
- **Padrão**: Supervisor do LangGraph
- **Funções**:
  - Analisa a intenção do usuário
  - Seleciona o agente especializado apropriado
  - Mantém contexto da conversação
  - Pode invocar múltiplos agentes em sequência
  - Consolida respostas de diferentes agentes

#### 2. MCP Server (FastMCP Puro)

- **Responsabilidade**: Centraliza acesso a ferramentas e recursos
- **Implementação**: FastMCP sem FastAPI
- **Vantagens**:
  - Ferramentas implementadas uma única vez
  - Todos os agentes acessam as mesmas ferramentas
  - Facilita manutenção e atualização
  - Protocolo MCP nativo para comunicação

#### 3. Agentes Especializados

**Weather Agent**
- Consultas meteorológicas
- Previsões do tempo
- Dados climáticos históricos

**Information Agent**
- RAG (Retrieval-Augmented Generation)
- Busca em conhecimento corporativo
- Respostas informacionais

**Data Agent**
- Análise de dados
- Consultas SQL
- Processamento de datasets

**Finance Agent** (Novo!)
- Cálculos financeiros
- Conversão de moedas
- Análises de investimento

## Pré-requisitos

- Python 3.13+
- pip ou uv para gerenciamento de dependências

## Instalação e Execução

### 1. Clone e configure

```bash
git clone https://github.com/edneyego/multi-agent.git
cd multi-agent
git checkout feature/mcpagent
```

### 2. Instale as dependências

```bash
# Usando pip
pip install -e .

# Ou usando uv (recomendado)
uv sync
```

### 3. Configure variáveis de ambiente

```bash
cp .env.example .env
# Edite .env com suas configurações
```

Variáveis importantes:
```bash
# Chave de API do LLM (OpenAI, Google, Anthropic)
LLM_API_KEY=your_api_key_here

# Modelo a ser usado
LLM_MODEL=gpt-4o-mini
# ou
LLM_MODEL=gemini-1.5-flash

# MCP Server
MCP_HOST=127.0.0.1
MCP_PORT=8000
```

### 4. Execute o sistema

#### Opção A: Execução completa (recomendado)

```bash
chmod +x run.sh
./run.sh
```

Este script irá:
1. Iniciar o MCP Server em background
2. Aguardar servidor estar pronto
3. Iniciar o Orquestrador
4. Processar queries de teste

#### Opção B: Execução manual

**Terminal 1 - MCP Server:**
```bash
python src/mcp/server.py
```

**Terminal 2 - Orquestrador:**
```bash
python src/orchestrator/main.py
```

#### Opção C: Execução individual

**Apenas MCP Server:**
```bash
chmod +x run_mcp_server.sh
./run_mcp_server.sh
```

**Apenas Orquestrador:**
```bash
chmod +x run_orchestrator.sh
./run_orchestrator.sh
```

### 5. Teste o sistema

```bash
# Via CLI
python src/cli.py "Como está o clima em São Paulo?"

# Via Python
python
>>> from orchestrator.main import Orchestrator
>>> import asyncio
>>> orch = Orchestrator()
>>> result = asyncio.run(orch.run("Como está o clima em São Paulo?"))
>>> print(result)
```

## Estrutura do Projeto

```
.
├── src/
│   ├── mcp/
│   │   ├── server.py           # MCP Server (FastMCP puro)
│   │   ├── tools/              # Ferramentas MCP
│   │   │   ├── weather.py      # Tool de clima
│   │   │   ├── database.py     # Tool de banco de dados
│   │   │   ├── information.py  # Tool de informação
│   │   │   └── finance.py      # Tool de finanças (novo!)
│   │   └── resources/          # Recursos MCP
│   │       ├── agent_cards.py
│   │       └── system.py
│   │
│   ├── agents/
│   │   ├── weather_agent.py    # Agente de clima
│   │   ├── info_agent.py       # Agente de informação
│   │   ├── data_agent.py       # Agente de dados
│   │   └── finance_agent.py    # Agente financeiro (novo!)
│   │
│   ├── orchestrator/
│   │   ├── main.py             # Orquestrador principal
│   │   ├── supervisor.py       # Supervisor LangGraph
│   │   └── mcp_client.py       # Cliente MCP para agentes
│   │
│   └── cli.py                  # Interface CLI
│
├── agent_cards/                # Configurações dos agentes
│   ├── weather_agent.json
│   ├── information_agent.json
│   ├── data_agent.json
│   └── finance_agent.json      # Novo!
│
├── data/
│   └── travel_agency.db        # Banco de dados SQLite
│
├── run.sh                      # Script principal
├── run_mcp_server.sh          # Script MCP Server
├── run_orchestrator.sh        # Script Orquestrador
├── pyproject.toml             # Dependências
└── README.md                  # Este arquivo
```

## Ferramentas MCP Disponíveis

| Ferramenta | Descrição | Agente Principal |
|------------|-----------|------------------|
| `get_weather` | Consulta clima via Open-Meteo API | Weather Agent |
| `query_database` | Executa consultas SQL | Data Agent |
| `get_database_schema` | Retorna esquema do banco | Data Agent |
| `search_information` | Busca em base de conhecimento | Information Agent |
| `calculate_finance` | Cálculos financeiros | Finance Agent |
| `convert_currency` | Conversão de moedas | Finance Agent |

## Recursos MCP Disponíveis

| URI | Descrição |
|-----|-----------||
| `resource://agent_cards/list` | Lista todos os agentes |
| `resource://agent_cards/{name}` | Detalhes de agente específico |
| `resource://system/status` | Status do sistema |
| `resource://database/schema` | Esquema da base de dados |

## Exemplos de Uso

### Consulta Meteorológica

```python
from orchestrator.main import Orchestrator
import asyncio

orchestrator = Orchestrator()
result = asyncio.run(orchestrator.run(
    "Qual a previsão do tempo para Rio de Janeiro?"
))
print(result)
```

### Análise de Dados

```python
result = asyncio.run(orchestrator.run(
    "Quantas reservas de viagem temos no banco de dados?"
))
print(result)
```

### Cálculo Financeiro (Novo!)

```python
result = asyncio.run(orchestrator.run(
    "Converta 1000 USD para BRL"
))
print(result)
```

### Busca de Informação

```python
result = asyncio.run(orchestrator.run(
    "Explique o que é arquitetura hexagonal"
))
print(result)
```

## Fluxo de Execução

1. **Recepção**: Usuário envia query através de canal (CLI, API, Web)
2. **Análise**: Orquestrador analisa intenção usando LLM
3. **Seleção**: Supervisor seleciona agente(s) apropriado(s)
4. **Execução**: 
   - Agente recebe tarefa do supervisor
   - Agente conecta ao MCP Server como cliente
   - Agente invoca ferramentas necessárias via MCP
   - MCP Server executa ferramentas e retorna resultados
5. **Consolidação**: Supervisor consolida respostas
6. **Resposta**: Resultado final é retornado ao usuário

## Vantagens desta Arquitetura

### ✅ Simplicidade
- Remove complexidade desnecessária do A2A
- Arquitetura mais fácil de entender
- Menos código para manter

### ✅ Eficiência
- Menos overhead de comunicação
- Protocolo direto entre agentes e MCP Server
- Melhor performance geral

### ✅ Escalabilidade
- Adicionar novos agentes é simples
- Ferramentas MCP são reutilizáveis
- Fácil expandir funcionalidades

### ✅ Manutenibilidade
- Código mais limpo e organizado
- Ferramentas centralizadas no MCP Server
- Debugging facilitado

### ✅ Flexibilidade
- LangGraph permite workflows complexos
- Supervisor pode invocar múltiplos agentes
- Suporte a roteamento condicional

## Comparação: Antes vs Depois

| Aspecto | Arquitetura Anterior | Nova Arquitetura |
|---------|---------------------|------------------|
| **Protocolos** | LangGraph + MCP + A2A | LangGraph + MCP |
| **Complexidade** | Alta | Média |
| **Performance** | Boa | Excelente |
| **Manutenção** | Complexa | Simples |
| **Agentes** | 3 agentes | 4 agentes |
| **Ferramentas** | Distribuídas | Centralizadas (MCP) |
| **Comunicação** | A2A + MCP | Apenas MCP |
| **Overhead** | Múltiplos protocolos | Protocolo único |

## Desenvolvimento

### Adicionando um Novo Agente

1. **Criar arquivo do agente:**
```python
# src/agents/my_agent.py
from orchestrator.mcp_client import MCPClient

class MyAgent:
    def __init__(self, mcp_host="localhost", mcp_port=8000):
        self.mcp_client = MCPClient(mcp_host, mcp_port)
    
    async def execute(self, query: str):
        # Lógica do agente
        result = await self.mcp_client.call_tool(
            "tool_name", 
            {"param": "value"}
        )
        return result
```

2. **Criar agent card:**
```json
{
  "name": "my_agent",
  "description": "Descrição do agente",
  "capabilities": ["capability1", "capability2"],
  "tools": ["tool1", "tool2"]
}
```

3. **Registrar no supervisor:**
```python
# src/orchestrator/supervisor.py
from agents.my_agent import MyAgent

# Adicionar à lista de agentes
agents = {
    "my_agent": MyAgent()
}
```

### Adicionando uma Nova Ferramenta MCP

```python
# src/mcp/tools/my_tool.py
from fastmcp import FastMCP

@mcp.tool(
    name='my_new_tool',
    description='Descrição da ferramenta'
)
def my_new_tool(param1: str, param2: int) -> dict:
    """Implementação da ferramenta."""
    result = process_data(param1, param2)
    return {
        'success': True,
        'result': result
    }
```

## Testes

```bash
# Executar todos os testes
pytest

# Testes específicos
pytest tests/test_mcp_server.py
pytest tests/test_orchestrator.py
pytest tests/test_agents.py

# Com coverage
pytest --cov=src --cov-report=html
```

## Troubleshooting

### MCP Server não inicia
```bash
# Verificar se porta está em uso
lsof -i :8000

# Mudar porta
export MCP_PORT=8001
python src/mcp/server.py
```

### Orquestrador não conecta ao MCP
```bash
# Verificar conectividade
curl http://localhost:8000/health

# Verificar logs
tail -f logs/mcp_server.log
```

### Agente não responde
```bash
# Verificar logs do agente
tail -f logs/orchestrator.log

# Testar ferramenta MCP diretamente
python -m mcp test_tool get_weather '{"city": "São Paulo"}'
```

## Contribuição

1. Fork o repositório
2. Crie uma branch: `git checkout -b feature/minha-feature`
3. Commit: `git commit -m 'Add minha feature'`
4. Push: `git push origin feature/minha-feature`
5. Abra um Pull Request

## Licença

MIT License - veja o arquivo LICENSE para detalhes.

## Roadmap

- ✅ Implementação LangGraph + MCP
- ✅ Remoção do protocolo A2A
- ✅ Adição do Finance Agent
- ✅ Arquitetura simplificada
- 🔄 Interface web para interação
- 🔄 Métricas e observabilidade
- 🔄 Testes end-to-end completos
- 🔄 Deploy containerizado (Docker)
- 🔄 CI/CD pipeline
- 🔄 Documentação API completa

---

## 🎉 Sobre esta Implementação

Esta branch `feature/mcpagent` representa uma **evolução significativa** da arquitetura original, eliminando a redundância entre A2A e MCP, e criando um sistema mais:

- **Simples**: Menos protocolos, menos complexidade
- **Rápido**: Comunicação direta via MCP
- **Limpo**: Código mais organizado e maintível
- **Poderoso**: Mantém toda a funcionalidade necessária

**Resultado**: Um sistema multi-agente profissional, eficiente e pronto para produção! 🚀
