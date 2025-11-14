# Arquitetura do Sistema Multi-Agente

## Visão Geral

Este documento detalha a arquitetura simplificada do sistema multi-agente, que utiliza **LangGraph** para orquestração e **Model Context Protocol (MCP)** para acesso centralizado a ferramentas.

## Decisões Arquiteturais

### Por que LangGraph + MCP (sem A2A)?

#### Problema Original

A arquitetura anterior utilizava três tecnologias:
- **LangGraph**: Orquestração de workflows
- **MCP**: Acesso a ferramentas e dados
- **A2A**: Comunicação entre agentes

Esta abordagem criava **redundância** porque:

1. **A2A e MCP têm propósitos similares**: Ambos facilitam comunicação e acesso a capacidades
2. **Overhead desnecessário**: Múltiplos protocolos aumentam complexidade
3. **Manutenção complexa**: Mais código, mais pontos de falha
4. **Curva de aprendizado**: Desenvolvedores precisam entender 3 tecnologias

#### Solução: LangGraph + MCP

| Responsabilidade | Tecnologia | Justificativa |
|-----------------|------------|---------------|
| **Orquestração de Agentes** | LangGraph | Gerenciamento de estado, workflows complexos, padrão supervisor |
| **Acesso a Ferramentas** | MCP | Protocolo padrão, cliente-servidor, centralização de tools |
| **Comunicação entre Agentes** | MCP | Suficiente para comunicação interna, sem overhead |

### Benefícios da Arquitetura Simplificada

#### 1. Simplicidade
- **Menos protocolos**: 2 ao invés de 3
- **Arquitetura mais clara**: Fácil de entender e explicar
- **Onboarding rápido**: Novos desenvolvedores se adaptam mais rápido

#### 2. Performance
- **Menos overhead**: Comunicação direta via MCP
- **Latência reduzida**: Sem camadas extras de protocolos
- **Melhor throughput**: Sistema mais eficiente

#### 3. Manutenibilidade
- **Código limpo**: Menos abstrações desnecessárias
- **Debugging facilitado**: Menos pontos de falha
- **Testes mais simples**: Menos mocks e stubs necessários

#### 4. Escalabilidade
- **Adicionar agentes**: Simples, apenas implementar interface
- **Adicionar ferramentas**: Centralizado no MCP Server
- **Horizontal scaling**: MCP Server pode ser replicado

## Componentes da Arquitetura

### 1. Camada de Entrada

```
┌─────────────────────────────────────────────────────────────┐
│                    CANAIS DE ENTRADA                         │
│          Web │ API REST │ CLI │ Chat Interface              │
└─────────────────────────────────────────────────────────────┘
```

**Responsabilidade**: Receber queries do usuário

**Interfaces suportadas**:
- **CLI**: Interface de linha de comando para testes
- **API REST**: Endpoints HTTP para integração
- **Web Interface**: Dashboard web para interação
- **Chat Interface**: Integração com plataformas de mensagens

**Formato de entrada**:
```json
{
  "query": "Como está o clima em São Paulo?",
  "context": {},
  "metadata": {
    "user_id": "user123",
    "session_id": "session456"
  }
}
```

### 2. Orquestrador LangGraph

```
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
```

**Padrão**: Supervisor (LangGraph)

**Responsabilidades**:

1. **Análise de Intenção**
   - Usa LLM para entender o que o usuário quer
   - Classifica o tipo de query
   - Identifica entidades relevantes

2. **Seleção de Agente**
   - Mantém registro de agentes disponíveis
   - Avalia capacidades de cada agente
   - Seleciona o(s) agente(s) mais adequado(s)

3. **Gestão de Workflow**
   - Pode invocar múltiplos agentes em sequência
   - Gerencia dependências entre tarefas
   - Implementa retry logic e fallbacks

4. **Consolidação de Respostas**
   - Agrega resultados de múltiplos agentes
   - Formata resposta final para o usuário
   - Mantém contexto da conversação

**Estado do Grafo**:
```python
class OrchestratorState(BaseModel):
    query: str
    intent: Optional[str]
    selected_agent: Optional[str]
    agent_response: Optional[Dict[str, Any]]
    final_response: Optional[str]
    context: Dict[str, Any] = {}
    history: List[Dict[str, Any]] = []
```

**Fluxo do Grafo**:
```
INICIO → Análise de Intenção → Seleção de Agente → Execução → Consolidação → FIM
                                              │
                                              └─ (se necessário) → Selecionar Outro Agente
```

### 3. MCP Server (FastMCP)

```
┌──────────────────────────────────────────┐
│         MCP SERVER (FastMCP)             │
│  ┌────────────────────────────────────┐ │
│  │ FERRAMENTAS (Tools)                │ │
│  │ • get_weather                      │ │
│  │ • query_database                   │ │
│  │ • search_information               │ │
│  │ • calculate_finance                │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │ RECURSOS (Resources)               │ │
│  │ • agent_cards                      │ │
│  │ • system_status                    │ │
│  │ • database_schema                  │ │
│  └────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

**Protocolo**: Model Context Protocol (MCP)

**Implementação**: FastMCP (puro, sem FastAPI)

**Responsabilidades**:

1. **Expor Ferramentas (Tools)**
   - Cada ferramenta é uma função com signature bem definida
   - Documentada via MCP protocol
   - Invocável por qualquer cliente MCP

2. **Expor Recursos (Resources)**
   - URIs padronizados para acesso a dados
   - Metadados sobre o sistema
   - Informações de configuração

3. **Gerenciar Conexões**
   - Aceita múltiplos clientes MCP
   - Mantém sessões ativas
   - Controla autenticação/autorização

**Exemplo de Tool**:
```python
@mcp.tool(
    name='get_weather',
    description='Obtém informações meteorológicas'
)
def get_weather(city: str, country: str = 'BR') -> Dict[str, Any]:
    """Consulta clima via Open-Meteo API."""
    # Implementação
    return {
        'temperature': 25.5,
        'condition': 'parcialmente nublado',
        'humidity': 60
    }
```

**Exemplo de Resource**:
```python
@mcp.resource(
    uri='resource://system/status',
    name='Status do Sistema',
    mime_type='application/json'
)
def get_system_status() -> str:
    """Retorna status atual do sistema."""
    status = {
        'status': 'running',
        'agents': 4,
        'uptime': '2h 30m'
    }
    return json.dumps(status)
```

### 4. Agentes Especializados

```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Weather   │ │ Information │ │    Data     │ │   Finance   │
│    Agent    │ │    Agent    │ │    Agent    │ │    Agent    │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

Cada agente especializado:

**1. Tem domínio específico**
- Especializado em um tipo de tarefa
- Prompt otimizado para seu domínio
- Conhecimento específico

**2. Atua como cliente MCP**
```python
class WeatherAgent:
    def __init__(self, mcp_host, mcp_port):
        self.mcp_client = MCPClient(mcp_host, mcp_port)
    
    async def execute(self, query: str):
        # Conectar ao MCP Server
        result = await self.mcp_client.call_tool(
            'get_weather',
            {'city': 'São Paulo'}
        )
        return result
```

**3. Interface padronizada**
```python
class BaseAgent(ABC):
    @abstractmethod
    async def execute(self, query: str, context: Dict) -> Dict[str, Any]:
        """Executa tarefa do agente."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Retorna lista de capacidades."""
        pass
```

#### Weather Agent

**Domínio**: Meteorologia

**Capacidades**:
- Consultas de clima atual
- Previsões futuras
- Dados históricos
- Alertas meteorológicos

**Tools MCP utilizadas**:
- `get_weather`
- `get_forecast`

**Exemplos de queries**:
- "Como está o clima em São Paulo?"
- "Vai chover amanhã no Rio?"
- "Previsão para os próximos 7 dias"

#### Information Agent

**Domínio**: Busca e informação

**Capacidades**:
- RAG (Retrieval-Augmented Generation)
- Busca em base de conhecimento
- Respostas informacionais gerais
- Sumários de documentos

**Tools MCP utilizadas**:
- `search_information`
- `get_document`
- `summarize`

**Exemplos de queries**:
- "Explique o que é arquitetura hexagonal"
- "Busque informações sobre LangGraph"
- "Resuma este documento"

#### Data Agent

**Domínio**: Análise de dados

**Capacidades**:
- Consultas SQL
- Análise de datasets
- Geração de relatórios
- Visualizações de dados

**Tools MCP utilizadas**:
- `query_database`
- `get_database_schema`
- `analyze_data`

**Exemplos de queries**:
- "Quantas reservas temos no banco?"
- "Mostre as vendas do último mês"
- "Qual o destino mais popular?"

#### Finance Agent (Novo!)

**Domínio**: Finanças

**Capacidades**:
- Cálculos financeiros
- Conversão de moedas
- Análise de investimentos
- Cálculo de juros

**Tools MCP utilizadas**:
- `calculate_finance`
- `convert_currency`
- `get_exchange_rate`

**Exemplos de queries**:
- "Converta 1000 USD para BRL"
- "Calcule juros compostos"
- "Qual a taxa de câmbio do euro?"

### 5. Camada de Dados

```
┌──────────────────────────────────────────┐
│           FONTES DE DADOS                │
│  SQLite │ APIs │ Knowledge Base │ Files  │
└──────────────────────────────────────────┘
```

**Fontes de dados**:

1. **SQLite**: Banco de dados local
2. **External APIs**: APIs externas (Open-Meteo, etc.)
3. **Knowledge Base**: Base de conhecimento corporativo
4. **File System**: Arquivos locais e remotos

**Acesso**: Todas as fontes são acessadas exclusivamente via MCP Server

## Fluxo de Execução Detalhado

### Exemplo: "Como está o clima em São Paulo?"

```
1. 📝 ENTRADA
   Usuário (via CLI): "Como está o clima em São Paulo?"
   ↓

2. 🧠 ORQUESTRADOR (Análise)
   LangGraph Supervisor:
   - Analisa query com LLM
   - Identifica: tipo=clima, cidade="São Paulo"
   - Decisão: Usar Weather Agent
   ↓

3. 🤖 WEATHER AGENT (Execução)
   - Recebe tarefa do supervisor
   - Prepara parâmetros: {"city": "São Paulo", "country": "BR"}
   - Conecta ao MCP Server como cliente
   ↓

4. 🔧 MCP SERVER (Ferramenta)
   - Recebe requisição: call_tool('get_weather', params)
   - Executa função get_weather()
   - Chama Open-Meteo API
   - Retorna dados meteorológicos
   ↓

5. 🤖 WEATHER AGENT (Processamento)
   - Recebe dados do MCP
   - Formata resposta amigável
   - Retorna ao supervisor
   ↓

6. 🧠 ORQUESTRADOR (Consolidação)
   - Recebe resposta do Weather Agent
   - Gera resposta final para usuário
   ↓

7. 📝 SAÍDA
   "Em São Paulo está 25°C, parcialmente nublado com 60% de umidade."
```

### Exemplo Complexo: Query Multi-Agente

**Query**: "Qual foi o destino mais vendido e como está o clima lá?"

```
1. 📝 ENTRADA
   Query complexa envolvendo dados + clima
   ↓

2. 🧠 ORQUESTRADOR (Análise)
   - Identifica: precisa de 2 agentes
   - Plano: Data Agent → Weather Agent
   ↓

3. 🤖 DATA AGENT (Primeira Tarefa)
   - Consulta banco via MCP
   - Tool: query_database("SELECT destination...")
   - Resultado: "Paris"
   ↓

4. 🧠 ORQUESTRADOR (Intermediário)
   - Recebe "Paris" do Data Agent
   - Passa para Weather Agent
   ↓

5. 🤖 WEATHER AGENT (Segunda Tarefa)
   - Consulta clima de Paris via MCP
   - Tool: get_weather("Paris", "FR")
   - Resultado: dados meteorológicos
   ↓

6. 🧠 ORQUESTRADOR (Consolidação)
   - Combina resultados de ambos agentes
   - Gera resposta unificada
   ↓

7. 📝 SAÍDA
   "O destino mais vendido é Paris. Atualmente lá está 15°C e ensolarado."
```

## Padrões e Práticas

### 1. Comunicação Assíncrona

Todo o sistema usa `async/await` para operações I/O:

```python
async def process_query(query: str):
    # Análise (pode chamar LLM - I/O)
    intent = await analyze_intent(query)
    
    # Seleção de agente (rápido, local)
    agent = select_agent(intent)
    
    # Execução (pode chamar MCP - I/O)
    result = await agent.execute(query)
    
    return result
```

### 2. Retry Logic e Fallbacks

```python
async def call_tool_with_retry(
    tool_name: str, 
    params: dict,
    max_retries: int = 3
):
    for attempt in range(max_retries):
        try:
            return await mcp_client.call_tool(tool_name, params)
        except Exception as e:
            if attempt == max_retries - 1:
                # Fallback: retornar erro amigável
                return {"error": f"Ferramenta {tool_name} indisponível"}
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### 3. Context Management

```python
class ConversationContext:
    """Gerencia contexto da conversação."""
    
    def __init__(self):
        self.history: List[Dict] = []
        self.entities: Dict[str, Any] = {}
        self.user_prefs: Dict[str, Any] = {}
    
    def add_message(self, role: str, content: str):
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })
    
    def get_relevant_history(self, n: int = 5):
        """Retorna últimas n mensagens."""
        return self.history[-n:]
```

### 4. Error Handling

Todas as camadas implementam tratamento de erros adequado:

```python
try:
    result = await agent.execute(query)
except MCPConnectionError:
    # MCP Server inacessível
    return error_response("Servidor de ferramentas indisponível")
except AgentExecutionError as e:
    # Erro na execução do agente
    return error_response(f"Erro ao processar: {e.message}")
except Exception as e:
    # Erro genérico
    logger.error(f"Erro inesperado: {e}")
    return error_response("Erro interno do sistema")
```

### 5. Logging e Observabilidade

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def execute_with_logging(agent_name: str, query: str):
    start_time = datetime.now()
    
    logger.info(f"[{agent_name}] Iniciando execução: {query}")
    
    try:
        result = await agent.execute(query)
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(
            f"[{agent_name}] Concluído em {duration:.2f}s"
        )
        
        return result
    except Exception as e:
        logger.error(
            f"[{agent_name}] Erro: {e}",
            exc_info=True
        )
        raise
```

## Escalabilidade

### Escala Horizontal

**MCP Server**:
- Pode ser replicado em múltiplas instâncias
- Load balancer distribui requisições
- Sem estado (stateless) - facilita escalamento

**Agentes**:
- Cada agente pode rodar em processo separado
- Pool de agentes para alta demanda
- Paralelização de execução

### Escala Vertical

- LLMs podem usar GPUs mais potentes
- MCP Server pode ter mais memória/CPU
- Cache de resultados frequentes

### Otimizações

1. **Caching**: Resultados de queries comuns
2. **Batching**: Agrupar múltiplas requisições
3. **Streaming**: Respostas progressivas para queries longas
4. **Connection Pooling**: Reutilizar conexões MCP

## Segurança

### Autenticação

- MCP Server requer autenticação de clientes
- Tokens JWT para sessões
- Expiração e refresh de tokens

### Autorização

- Controle granular de acesso a ferramentas
- Rate limiting por usuário/agente
- Audit log de todas as operações

### Validação de Entrada

```python
from pydantic import BaseModel, validator

class QueryRequest(BaseModel):
    query: str
    
    @validator('query')
    def validate_query(cls, v):
        if len(v) > 1000:
            raise ValueError('Query muito longa')
        if not v.strip():
            raise ValueError('Query vazia')
        return v
```

## Conclusão

Esta arquitetura simplificada oferece:

✅ **Clareza**: Fácil de entender e explicar  
✅ **Eficiência**: Comunicação direta, menos overhead  
✅ **Escalabilidade**: Componentes independentes e escaláveis  
✅ **Manutenibilidade**: Código limpo, bem estruturado  
✅ **Extensibilidade**: Fácil adicionar novos agentes/ferramentas  

**Resultado**: Um sistema robusto, eficiente e pronto para produção! 🚀
