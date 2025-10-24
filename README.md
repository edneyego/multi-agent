# Multi-Agent System with Pure FastMCP, A2A Protocol

> 🎯 **Branch `pure-fastmcp`** - Implementação exclusivamente FastMCP (sem mistura com FastAPI)

Uma POC (Proof of Concept) demonstrando um sistema multi-agent utilizando **FastMCP puro**, Model Context Protocol (MCP) e Agent-to-Agent (A2A) protocol, implementado com arquitetura hexagonal em Python.

## 🎆 O que há de novo nesta branch?

Esta branch resolve o problema da implementação original que misturava FastAPI com FastMCP. Agora temos:

✅ **FastMCP 100% puro** - sem FastAPI  
✅ **Protocolo MCP nativo** - sem facades HTTP  
✅ **Arquitetura simplificada** - um servidor, um protocolo  
✅ **Performance melhorada** - menor overhead  
✅ **Facilita manutenção** - código mais limpo  

## Arquitetura

Este projeto implementa uma arquitetura hexagonal (Ports and Adapters) com os seguintes componentes principais:

### Sistema Multi-Agent com FastMCP Puro

```
FastMCP Server (PURO)
├── Tools (Ferramentas MCP)
│   ├── find_agent_simple      # Busca de agentes
│   ├── get_weather            # Clima via Open-Meteo
│   ├── query_travel_data      # Consultas SQL
│   ├── get_database_schema    # Esquema da BD
│   └── a2a_delegate_task      # Delegação A2A
├── Resources (Recursos MCP)
│   ├── agent_cards/list       # Lista de agentes
│   ├── agent_cards/{name}     # Agente específico
│   ├── system/status          # Status do sistema
│   └── database/schema        # Esquema da BD
└── Transporte MCP Nativo
    ├── STDIO (padrão)
    ├── HTTP Streamable
    └── SSE
```

### Agentes Disponíveis

- **Information Agent**: Agent RAG (Retrieval-Augmented Generation) para consultas informacionais
- **Action Agent**: Agent de ação com ferramentas específicas
- **Weather Agent**: Especializado em consultas meteorológicas
- **Supervisor Agent**: Coordenador que gerencia e delega tarefas entre os agentes

### Tecnologias

- **FastMCP PURO**: Implementação nativa do Model Context Protocol (sem FastAPI)
- **A2A Protocol**: Comunicação entre agentes
- **Open-Meteo API**: Serviço meteorológico gratuito
- **SQLite**: Base de dados para agência de viagens
- **Arquitetura Hexagonal**: Separação clara de responsabilidades

## Pré-requisitos

- Python 3.13+
- Dependências do projeto (veja `pyproject.toml`)

## Instalação e Execução

### 1. Clone e mude para a branch

```bash
git clone https://github.com/edneyego/multi-agent.git
cd multi-agent
git checkout pure-fastmcp
```

### 2. Instale as dependências

```bash
pip install -e .
# Ou usando uv:
uv sync
```

### 3. Execute o servidor FastMCP puro

#### Opção A: Script automático
```bash
chmod +x run_pure_fastmcp.sh
./run_pure_fastmcp.sh
```

#### Opção B: Execução direta

```bash
# STDIO (padrão)
python src/a2a_mcp/mcp/server.py

# HTTP Streamable
MCP_TRANSPORT=streamable-http python src/a2a_mcp/mcp/server.py

# Com argumentos
python src/a2a_mcp/mcp/server.py streamable-http
```

## Estrutura do Projeto

```
src/
├── a2a_mcp/               # Sistema A2A + MCP
│   ├── agents/             # Implementação dos agentes
│   ├── mcp/
│   │   └── server.py       # 🎆 SERVIDOR FASTMCP PURO
│   └── common/             # Utilitários comuns
└── orchestrator/          # Orquestrador do sistema

agent_cards/               # Cartões de configuração dos agentes
travel_agency.db           # Base de dados SQLite

PURE_FASTMCP_IMPLEMENTATION.md  # 📚 Documentação detalhada
run_pure_fastmcp.sh        # Script de execução
```

## APIs e Serviços Utilizados

### Open-Meteo API (Meteorologia)

- URL base: `https://api.open-meteo.com/v1/forecast`
- ✅ **Gratuita** - não requer chave de API
- Geocoding automático
- Documentação: https://open-meteo.com/

### Exemplo de Uso via Cliente MCP

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "city": "São Paulo",
      "country": "BR"
    }
  }
}
```

## Ferramentas MCP Disponíveis

| Ferramenta | Descrição | Parâmetros |
|------------|-------------|------------|
| `find_agent_simple` | Busca agentes por palavras-chave | `query: str` |
| `get_weather` | Consulta meteorológica | `city: str, country?: str` |
| `query_travel_data` | Consultas SQL | `query: str` |
| `get_database_schema` | Esquema da base de dados | - |
| `a2a_delegate_task` | Delegação A2A | `agent_name: str, task: str, parameters?: dict` |

## Recursos MCP Disponíveis

| URI | Descrição |
|-----|-------------|
| `resource://agent_cards/list` | Lista todos os agentes |
| `resource://agent_cards/{name}` | Detalhes de agente específico |
| `resource://system/status` | Status do sistema |
| `resource://database/schema` | Esquema completo da BD |

## Configuração

Variáveis de ambiente suportadas:

```bash
# Tipo de transporte MCP
export MCP_TRANSPORT=stdio          # stdio | sse | streamable-http

# Host e porta (para transportes não-stdio)
export MCP_HOST=127.0.0.1
export MCP_PORT=8000
```

## Testes

```bash
# Verificar se o servidor inicia corretamente
python src/a2a_mcp/mcp/server.py

# Testar com cliente MCP (exemplo usando mcp CLI)
mcp connect stdio python src/a2a_mcp/mcp/server.py
```

## 🔄 Diferenças da Implementação Original

| Aspecto | Implementação Anterior | Pure FastMCP |
|---------|----------------------|---------------|
| **Framework** | FastAPI + FastMCP | Apenas FastMCP |
| **Arquitetura** | Híbrida (2 servidores) | Unificada (1 servidor) |
| **Threading** | Multi-thread | Single-thread |
| **Protocolos** | HTTP + MCP | MCP nativo |
| **Complexidade** | Alta | Baixa |
| **Performance** | Overhead FastAPI | Otimizada |
| **Manutenção** | Complexa | Simples |

## Desenvolvimento

### Estrutura Hexagonal

O projeto segue a arquitetura hexagonal com clara separação entre:

- **Core**: Lógica de negócio independente
- **Ports**: Interfaces/contratos
- **Adapters**: Implementações específicas

### Adicionando Novas Ferramentas MCP

```python
@mcp.tool(
    name='minha_nova_ferramenta',
    description='Descrição da ferramenta'
)
def minha_nova_ferramenta(parametro: str) -> Dict[str, Any]:
    """Implementação da ferramenta."""
    return {'resultado': f'Processado: {parametro}'}
```

### Adicionando Novos Recursos MCP

```python
@mcp.resource(
    uri='resource://meu_recurso/{id}',
    mime_type='application/json'
)
def meu_recurso(id: str) -> str:
    """Recurso personalizado."""
    return json.dumps({'id': id, 'dados': '...'})
```

## Contribuição

1. Fork o repositório
2. Crie uma branch: `git checkout -b feature/MinhaFeature`
3. Commit: `git commit -m 'Add MinhaFeature'`
4. Push: `git push origin feature/MinhaFeature`
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Roadmap

- ✅ Implementação FastMCP pura
- ✅ Remoção da arquitetura híbrida
- ✅ Otimização de performance
- 🔄 Implementação completa do protocolo A2A
- 🔄 Interface web para interação
- 🔄 Métricas e observabilidade
- 🔄 Testes end-to-end
- 🔄 Deploy em produção

---

## 🎉 Sobre esta Implementação

Esta branch `pure-fastmcp` representa uma evolução significativa do projeto original, eliminando a complexidade desnecessária da arquitetura híbrida e fornecendo uma implementação limpa, eficiente e conforme às melhores práticas do Model Context Protocol.

**Resultado**: Um sistema multi-agent mais simples, mais rápido e mais fácil de manter! 🚀
