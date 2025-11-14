# Guia de Implementação - Sistema Multi-Agente

## Introdução

Este guia fornece instruções passo a passo para implementar e executar o sistema multi-agente com LangGraph + MCP.

## Pré-requisitos

### Software Necessário

- Python 3.13 ou superior
- pip ou uv
- Git
- Editor de código (VSCode, PyCharm, etc.)

### Conhecimento Recomendado

- Python assíncrono (async/await)
- Básico de LangChain/LangGraph
- Conceitos de APIs REST
- Familiaridade com linha de comando

## Passo 1: Setup do Ambiente

### 1.1 Clone o Repositório

```bash
git clone https://github.com/edneyego/multi-agent.git
cd multi-agent
git checkout feature/mcpagent
```

### 1.2 Crie Ambiente Virtual

```bash
# Usando venv
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Ou usando uv (recomendado)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
```

### 1.3 Instale Dependências

```bash
# Com pip
pip install -e .

# Ou com uv (mais rápido)
uv sync
```

Verifique a instalação:
```bash
python -c "import fastmcp; import langgraph; print('OK')"
```

## Passo 2: Configuração

### 2.1 Configure Variáveis de Ambiente

```bash
cp .env.example .env
```

Edite `.env` com suas configurações:

```bash
# LLM Configuration
LLM_PROVIDER=openai  # ou google, anthropic
LLM_API_KEY=your_api_key_here
LLM_MODEL=gpt-4o-mini  # ou gemini-1.5-flash, claude-3-sonnet

# MCP Server
MCP_HOST=127.0.0.1
MCP_PORT=8000
MCP_TRANSPORT=stdio  # ou streamable-http

# System
LOG_LEVEL=INFO
```

### 2.2 Obtenha Chave de API do LLM

**OpenAI**:
1. Acesse https://platform.openai.com/api-keys
2. Crie nova chave de API
3. Adicione ao `.env`: `LLM_API_KEY=sk-...`

**Google (Gemini)**:
1. Acesse https://makersuite.google.com/app/apikey
2. Crie nova chave de API
3. Adicione ao `.env`: `LLM_API_KEY=AI...`

**Anthropic (Claude)**:
1. Acesse https://console.anthropic.com/
2. Crie nova chave de API
3. Adicione ao `.env`: `LLM_API_KEY=sk-ant-...`

### 2.3 Verifique Banco de Dados

O banco SQLite já deve estar incluído. Verifique:

```bash
ls -lh travel_agency.db
# Deve mostrar o arquivo com ~100KB

# Teste o banco
sqlite3 travel_agency.db "SELECT COUNT(*) FROM travel_bookings;"
```

## Passo 3: Entendendo a Estrutura

### 3.1 Estrutura de Diretórios

```
src/
├── mcp/                    # MCP Server
│   ├── server.py           # Servidor principal
│   ├── tools/              # Ferramentas MCP
│   └── resources/          # Recursos MCP
│
├── agents/                # Agentes especializados
│   ├── weather_agent.py
│   ├── info_agent.py
│   ├── data_agent.py
│   └── finance_agent.py
│
├── orchestrator/          # Orquestrador LangGraph
│   ├── main.py
│   ├── supervisor.py
│   └── mcp_client.py
│
└── cli.py                 # Interface CLI
```

### 3.2 Componentes Principais

1. **MCP Server** (`src/mcp/server.py`)
   - Servidor FastMCP puro
   - Expõe ferramentas e recursos
   - Gerencia conexões de clientes

2. **Orquestrador** (`src/orchestrator/main.py`)
   - Supervisor LangGraph
   - Roteamento de queries
   - Gerenciamento de estado

3. **Agentes** (`src/agents/`)
   - Especializados por domínio
   - Clientes MCP
   - Lógica de execução

## Passo 4: Executando o Sistema

### 4.1 Método 1: Script Automatizado (Recomendado)

```bash
chmod +x run.sh
./run.sh
```

O script irá:
1. ✅ Iniciar MCP Server em background
2. ✅ Aguardar servidor estar pronto
3. ✅ Iniciar Orquestrador
4. ✅ Executar queries de teste

### 4.2 Método 2: Execução Manual

**Terminal 1 - MCP Server:**
```bash
python src/mcp/server.py
```

Você deve ver:
```
🚀 INICIANDO SISTEMA MULTI-AGENT COM FASTMCP PURO
📡 Protocolo: MCP (Model Context Protocol)
🔧 Implementação: FastMCP PURO (SEM FastAPI)
🚀 Transporte: stdio
🟢 Servidor FastMCP PURO iniciado - aguardando conexões...
```

**Terminal 2 - Orquestrador:**
```bash
python src/orchestrator/main.py
```

Você deve ver:
```
🎯 Orquestrador Multi-Agente iniciado
🤖 4 agentes registrados
📡 Conectado ao MCP Server: 127.0.0.1:8000
✅ Sistema pronto para receber queries
```

**Terminal 3 - Cliente:**
```bash
python src/cli.py "Como está o clima em São Paulo?"
```

### 4.3 Método 3: Modo Interativo

```bash
python src/cli.py --interactive
```

Você entrará em modo interativo:
```
💬 Sistema Multi-Agente - Modo Interativo
Digite sua query (ou 'sair' para encerrar)

> Como está o clima em São Paulo?
🤖 Processando...

✅ Resposta:
Em São Paulo está 25°C, parcialmente nublado com 60% de umidade.

> Quantas reservas temos no banco?
🤖 Processando...

✅ Resposta:
Existem 150 reservas de viagem no banco de dados.

> sair
👋 Até logo!
```

## Passo 5: Testando Funcionalidades

### 5.1 Teste do Weather Agent

```bash
python src/cli.py "Como está o clima em São Paulo?"
python src/cli.py "Qual a previsão do tempo para o Rio de Janeiro?"
python src/cli.py "Vai chover amanhã em Belo Horizonte?"
```

**Resposta esperada**:
```
🌤️ Clima em São Paulo:
- Temperatura: 25°C
- Condição: Parcialmente nublado
- Umidade: 60%
- Vento: 15 km/h
```

### 5.2 Teste do Data Agent

```bash
python src/cli.py "Quantas reservas temos no banco de dados?"
python src/cli.py "Qual o destino mais popular?"
python src/cli.py "Mostre as últimas 5 reservas"
```

**Resposta esperada**:
```
📊 Resultados da consulta:

Total de reservas: 150

Destino mais popular: Paris (23 reservas)

Últimas 5 reservas:
1. João Silva - Paris - 2024-03-15
2. Maria Santos - Nova York - 2024-03-14
3. Pedro Oliveira - Londres - 2024-03-13
...
```

### 5.3 Teste do Finance Agent

```bash
python src/cli.py "Converta 1000 USD para BRL"
python src/cli.py "Qual a taxa de câmbio do euro hoje?"
python src/cli.py "Calcule juros compostos de 10000 reais a 0.5% ao mês por 12 meses"
```

**Resposta esperada**:
```
💰 Conversão de moeda:

1000 USD = 5,000.00 BRL

Taxa de câmbio: 1 USD = 5.00 BRL
Data: 14/11/2025
```

### 5.4 Teste do Information Agent

```bash
python src/cli.py "Explique o que é arquitetura hexagonal"
python src/cli.py "O que é o protocolo MCP?"
python src/cli.py "Como funciona o LangGraph?"
```

**Resposta esperada**:
```
📖 Arquitetura Hexagonal:

Também conhecida como Ports and Adapters, é um padrão arquitetural que:

1. Separa o core da aplicação da infraestrutura
2. Define interfaces (portas) para comunicação
3. Implementa adaptadores para sistemas externos
4. Facilita testes e manutenção
...
```

### 5.5 Teste de Query Complexa (Multi-Agente)

```bash
python src/cli.py "Qual foi o destino mais vendido e como está o clima lá?"
```

**Resposta esperada**:
```
🔍 Analisando query complexa...

📊 Etapa 1: Consultando dados de vendas
✅ Destino mais vendido: Paris (23 reservas)

🌤️ Etapa 2: Consultando clima em Paris
✅ Clima atual:
- Temperatura: 15°C
- Condição: Ensolarado
- Umidade: 55%

🎉 Resposta final:
O destino mais vendido é Paris com 23 reservas.
Atualmente o clima em Paris está ensolarado, 15°C com 55% de umidade.
```

## Passo 6: Desenvolvimento

### 6.1 Adicionando um Novo Agente

#### 6.1.1 Criar Arquivo do Agente

```bash
touch src/agents/translation_agent.py
```

```python
# src/agents/translation_agent.py
from typing import Dict, Any
from orchestrator.mcp_client import MCPClient

class TranslationAgent:
    """Agente especializado em tradução de textos."""
    
    def __init__(self, mcp_host: str = "127.0.0.1", mcp_port: int = 8000):
        self.mcp_client = MCPClient(mcp_host, mcp_port)
        self.name = "translation_agent"
        self.description = "Especialista em tradução de textos"
    
    def get_capabilities(self) -> list[str]:
        """Retorna lista de capacidades do agente."""
        return [
            "traduzir texto",
            "detectar idioma",
            "transliterar",
            "sugerir sinônimos"
        ]
    
    async def execute(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Executa tradução."""
        try:
            # Extrair parâmetros da query
            # (aqui você pode usar um LLM para parsear)
            params = self._parse_query(query)
            
            # Chamar ferramenta MCP
            result = await self.mcp_client.call_tool(
                'translate_text',
                params
            )
            
            return {
                'success': True,
                'agent': self.name,
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'agent': self.name,
                'error': str(e)
            }
    
    def _parse_query(self, query: str) -> Dict[str, str]:
        """Extrai parâmetros da query."""
        # Implementação simplificada
        # Em produção, use um LLM para extrair parâmetros
        return {
            'text': query,
            'target_language': 'en'  # default
        }
```

#### 6.1.2 Criar Agent Card

```bash
touch agent_cards/translation_agent.json
```

```json
{
  "name": "translation_agent",
  "description": "Especialista em tradução de textos entre diversos idiomas",
  "version": "1.0.0",
  "capabilities": [
    "Tradução de textos",
    "Detecção de idioma",
    "Transliterarção",
    "Sugestão de sinônimos"
  ],
  "tools": [
    "translate_text",
    "detect_language",
    "transliterate"
  ],
  "keywords": [
    "traduzir",
    "tradução",
    "translate",
    "idioma",
    "language"
  ],
  "examples": [
    "Traduza 'olá mundo' para inglês",
    "Qual o idioma deste texto?",
    "Como se diz 'obrigado' em espanhol?"
  ]
}
```

#### 6.1.3 Registrar no Supervisor

```python
# src/orchestrator/supervisor.py
from agents.translation_agent import TranslationAgent

class Supervisor:
    def __init__(self):
        self.agents = {
            'weather_agent': WeatherAgent(),
            'info_agent': InformationAgent(),
            'data_agent': DataAgent(),
            'finance_agent': FinanceAgent(),
            'translation_agent': TranslationAgent(),  # Novo!
        }
```

#### 6.1.4 Adicionar Ferramenta MCP

```python
# src/mcp/tools/translation.py
@mcp.tool(
    name='translate_text',
    description='Traduz texto entre idiomas'
)
def translate_text(text: str, target_language: str, source_language: str = 'auto') -> Dict[str, Any]:
    """Traduz texto usando serviço de tradução."""
    try:
        # Aqui você pode usar Google Translate API, DeepL, etc.
        # Para este exemplo, simularemos
        
        # Em produção:
        # from googletrans import Translator
        # translator = Translator()
        # result = translator.translate(text, dest=target_language)
        
        return {
            'success': True,
            'original_text': text,
            'translated_text': f'[TRANSLATED to {target_language}] {text}',
            'source_language': source_language,
            'target_language': target_language
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

#### 6.1.5 Teste o Novo Agente

```bash
python src/cli.py "Traduza 'olá mundo' para inglês"
```

**Resposta esperada**:
```
🌐 Tradução:

Texto original: olá mundo
Idioma de origem: Português (pt)

Tradução: Hello world
Idioma de destino: Inglês (en)
```

### 6.2 Adicionando Nova Ferramenta MCP

Se você só quer adicionar uma ferramenta (sem agente novo):

```python
# src/mcp/server.py

@mcp.tool(
    name='calculate_distance',
    description='Calcula distância entre duas cidades'
)
def calculate_distance(city1: str, city2: str) -> Dict[str, Any]:
    """Calcula distância usando coordenadas."""
    # Implementação
    return {
        'distance_km': 500,
        'distance_miles': 310,
        'city1': city1,
        'city2': city2
    }
```

A ferramenta estará imediatamente disponível para todos os agentes!

## Passo 7: Debugging

### 7.1 Ativar Logs Detalhados

```bash
export LOG_LEVEL=DEBUG
python src/mcp/server.py
```

Você verá logs detalhados:
```
DEBUG - MCP Server received request: {"method": "tools/call", ...}
DEBUG - Executing tool: get_weather
DEBUG - Tool params: {"city": "São Paulo"}
DEBUG - Tool result: {"temperature": 25, ...}
```

### 7.2 Verificar Conexão MCP

```bash
# Teste se o MCP Server está rodando
ps aux | grep "mcp/server.py"

# Teste conectividade (se usar HTTP transport)
curl http://localhost:8000/health
```

### 7.3 Inspecionar Estado do Sistema

```python
# src/orchestrator/debug.py
import asyncio
from orchestrator.main import Orchestrator

async def debug_system():
    orch = Orchestrator()
    
    # Verificar agentes registrados
    print("Agentes:", list(orch.agents.keys()))
    
    # Verificar conexão MCP
    status = await orch.mcp_client.get_status()
    print("MCP Status:", status)
    
    # Listar ferramentas disponíveis
    tools = await orch.mcp_client.list_tools()
    print("Tools:", [t['name'] for t in tools])

if __name__ == '__main__':
    asyncio.run(debug_system())
```

```bash
python src/orchestrator/debug.py
```

### 7.4 Troubleshooting Comum

**Problema**: MCP Server não inicia
```bash
# Verificar se porta está em uso
lsof -i :8000

# Matar processo existente
kill -9 <PID>

# Ou mudar porta
export MCP_PORT=8001
```

**Problema**: Agente não responde
```bash
# Verificar logs
tail -f logs/orchestrator.log

# Testar ferramenta MCP diretamente
python -c "
import asyncio
from orchestrator.mcp_client import MCPClient

async def test():
    client = MCPClient()
    result = await client.call_tool('get_weather', {'city': 'SP'})
    print(result)

asyncio.run(test())
"
```

**Problema**: LLM API Key inválida
```bash
# Verificar se .env está configurado
cat .env | grep LLM_API_KEY

# Testar chave manualmente
python -c "
from openai import OpenAI
client = OpenAI(api_key='sua_chave_aqui')
response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[{'role': 'user', 'content': 'teste'}]
)
print(response.choices[0].message.content)
"
```

## Passo 8: Próximos Passos

### 8.1 Deploy em Produção

1. **Containerização**:
   ```bash
   docker build -t multi-agent .
   docker run -p 8000:8000 multi-agent
   ```

2. **Kubernetes**:
   - Deploy MCP Server como serviço
   - Deploy Orquestrador como deployment
   - Configure health checks

3. **Monitoramento**:
   - Prometheus para métricas
   - Grafana para dashboards
   - Sentry para error tracking

### 8.2 Melhorias

1. **Interface Web**:
   - Frontend React/Vue
   - WebSocket para respostas em tempo real
   - Dashboard de monitoramento

2. **Autenticação**:
   - JWT tokens
   - OAuth2/OpenID Connect
   - Rate limiting por usuário

3. **Cache**:
   - Redis para cache de respostas
   - Cache de resultados de ferramentas
   - Cache de embeddings

4. **Observabilidade**:
   - OpenTelemetry para tracing
   - Structured logging
   - APM (Application Performance Monitoring)

### 8.3 Expansão de Funcionalidades

1. **Novos Agentes**:
   - Email Agent (envio de emails)
   - Calendar Agent (agendamento)
   - Search Agent (busca web)
   - Image Agent (processamento de imagens)

2. **Novas Ferramentas**:
   - Integrações com CRMs
   - Integrações com ERPs
   - APIs de terceiros
   - Processamento de documentos

3. **Features Avançadas**:
   - Streaming de respostas
   - Multi-turn conversations
   - Context window management
   - Agent learning/feedback

## Recursos Adicionais

### Documentação

- [README.md](README.md) - Visão geral do projeto
- [ARCHITECTURE.md](ARCHITECTURE.md) - Detalhes da arquitetura
- [API.md](API.md) - Documentação da API (se existir)

### Links Úteis

- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **FastMCP**: https://github.com/jlowin/fastmcp
- **MCP Protocol**: https://modelcontextprotocol.io/
- **Open-Meteo API**: https://open-meteo.com/

### Comunidade

- **Issues**: https://github.com/edneyego/multi-agent/issues
- **Discussions**: https://github.com/edneyego/multi-agent/discussions
- **Discord**: [Link do Discord se existir]

## Conclusão

Parabéns! 🎉 Você agora tem um sistema multi-agente funcional rodando localmente.

**Próximos passos**:
1. ✅ Experimente diferentes queries
2. ✅ Adicione seu próprio agente
3. ✅ Customize ferramentas MCP
4. ✅ Contribua com o projeto

**Precisa de ajuda?** Abra uma issue no GitHub ou entre em contato!

---

**Happy Coding! 🚀**
