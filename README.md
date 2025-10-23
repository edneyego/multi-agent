# Multi-Agent System with LangGraph, MCP and A2A Protocol

Uma POC (Proof of Concept) demonstrando um sistema multi-agent utilizando LangGraph, Model Context Protocol (MCP) via fastMCP e Agent-to-Agent (A2A) protocol, implementado com arquitetura hexagonal em Python.

## Arquitetura

Este projeto implementa uma arquitetura hexagonal (Ports and Adapters) com os seguintes componentes principais:

### Agentes
- **Information Agent**: Agent RAG (Retrieval-Augmented Generation) para consultas informacionais
- **Action Agent**: Agent de ação com duas ferramentas:
  - Weather API para consulta do clima
  - Ferramenta personalizada via MCP
- **Supervisor Agent**: Coordenador que gerencia e delega tarefas entre os agentes

### Tecnologias
- **LangGraph**: Orquestração de workflows multi-agent
- **fastMCP**: Implementação do Model Context Protocol
- **A2A Protocol**: Comunicação entre agentes
- **Redis**: Persistência de dados
- **Arquitetura Hexagonal**: Separação clara de responsabilidades

## Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Redis
- Chave de API para LLM (OpenAI, Anthropic, etc.)

## Instalação e Execução

### 1. Clone o repositório
```bash
git clone https://github.com/edneyego/multi-agent.git
cd multi-agent
```

### 2. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite .env com suas configurações
```

### 3. Execute com Docker Compose
```bash
docker-compose up -d
```

### 4. Execute manualmente (desenvolvimento)
```bash
# Instale as dependências
pip install -r requirements.txt

# Inicie o Redis
docker run -d -p 6379:6379 redis:alpine

# Execute o sistema
python src/main.py
```

## Estrutura do Projeto

```
src/
├── core/                    # Domínio e lógica de negócio
│   ├── domain/              # Modelos de domínio
│   └── application/         # Casos de uso e portas
├── infrastructure/          # Adaptadores para sistemas externos
│   └── adapters/
│       ├── inbound/         # Adaptadores de entrada (A2A)
│       └── outbound/        # Adaptadores de saída (Redis, APIs)
├── agents/                  # Implementação dos agentes LangGraph
├── mcp_servers/             # Servidores MCP
└── config/                  # Configurações
```

## APIs e Serviços Utilizados

### Weather API
Este projeto utiliza a Open-Meteo API (gratuita) para consultas meteorológicas:
- URL base: `https://api.open-meteo.com/v1/forecast`
- Não requer chave de API
- Documentação: https://open-meteo.com/

### Exemplo de Uso
```json
{
  "query": "Como está o clima em São Paulo?",
  "agent": "action"
}
```

## Componentes Principais

### Information Agent (RAG)
Agent especializado em consultas informacionais usando técnicas de RAG.

### Action Agent
Agent com duas ferramentas:
1. **Weather Tool**: Consulta condições meteorológicas
2. **Custom MCP Tool**: Ferramenta personalizada via fastMCP

### Supervisor Agent
Coordenador central que:
- Analisa consultas do usuário
- Decide qual agent usar
- Gerencia o fluxo de conversação
- Implementa o protocolo A2A

## Testes

```bash
# Testes unitários
pytest tests/unit/

# Testes de integração
pytest tests/integration/

# Todos os testes
pytest
```

## Desenvolvimento

### Estrutura Hexagonal

O projeto segue a arquitetura hexagonal com clara separação entre:
- **Core**: Lógica de negócio independente
- **Ports**: Interfaces/contratos
- **Adapters**: Implementações específicas

### Adicionando Novos Agentes

1. Crie o agente em `src/agents/`
2. Implemente as portas necessárias em `src/core/application/ports/`
3. Crie os adaptadores em `src/infrastructure/adapters/`
4. Configure no supervisor

## Configuração

As configurações principais estão em `src/config/settings.py` e podem ser sobrescritas via variáveis de ambiente.

## Contribuição

1. Fork o repositório
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Roadmap

- [ ] Implementação completa do protocolo A2A
- [ ] Interface web para interação
- [ ] Métricas e observabilidade
- [ ] Testes end-to-end
- [ ] Documentação da API
- [ ] Deploy em produção