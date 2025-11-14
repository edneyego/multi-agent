# Sistema Multi-Agente: LangGraph + MCP

> ✅ **Versão 2.0** - Arquitetura simplificada usando **APENAS** LangGraph + MCP  
> ❌ **A2A completamente removido** - Sem código, dependências ou menções

Uma implementação profissional de sistema multi-agente utilizando **LangGraph** para orquestração e **FastMCP** para acesso centralizado a ferramentas.

## 🎯 Arquitetura

```
┌─────────────┐
│   Usuário   │
└──────┬──────┘
       │ Query
       ▼
┌─────────────────────────────────┐
│  Orquestrador (LangGraph)       │
│  - Padrão Supervisor            │
│  - Roteamento inteligente       │
│  - Gerenciamento de estado      │
└────────┬────────────────────────┘
         │
         ▼ Seleciona agente
┌─────────────────────────────────┐
│  Agentes Especializados         │
│  - WeatherAgent                 │
│  - TravelAgent                  │
│  - PlannerAgent                 │
└────────┬────────────────────────┘
         │
         ▼ Conecta via MCP
┌─────────────────────────────────┐
│  MCP Server (FastMCP)           │
│  - Ferramentas de clima         │
│  - Ferramentas de BD            │
│  - Ferramentas de viagem        │
└─────────────────────────────────┘
```

## 🚀 Status da Refatoração

✅ **Concluído**: Remoção completa do código A2A  
✅ **Concluído**: Implementação da estrutura base  
✅ **Concluído**: Agentes especializados (Weather, Travel, Planner)  
✅ **Concluído**: Cliente MCP  
⏳ **Em andamento**: Implementação do MCP Server e ferramentas  
⏳ **Em andamento**: Supervisor LangGraph completo  

## 📚 Estrutura do Projeto

```
src/
├── mcp_server/              # Servidor MCP centralizado
│   ├── server.py           # FastMCP server
│   └── tools/
│       ├── weather_tools.py   # Ferramentas clima
│       ├── database_tools.py  # Ferramentas BD  
│       └── travel_tools.py    # Ferramentas viagem
│
├── agents/                 # Agentes especializados
│   ├── base_agent.py      # ✅ Classe base
│   ├── weather_agent.py   # ✅ Agente clima
│   ├── travel_agent.py    # ✅ Agente viagens
│   └── planner_agent.py   # ✅ Agente planejador
│
├── orchestrator/          # Orquestrador LangGraph
│   ├── supervisor.py      # ⏳ Lógica do supervisor
│   ├── state.py           # ✅ Estado compartilhado
│   └── mcp_client.py      # ✅ Cliente MCP
│
└── cli.py                 # Interface CLI
```

## 🔧 Próximos Passos

### Para Desenvolvedores

1. **Implementar MCP Server completo**
   - ✅ Estrutura criada
   - ⏳ Implementar `weather_tools.py` (veja arquivo fornecido)
   - ⏳ Implementar `database_tools.py` (veja arquivo fornecido)
   - ⏳ Implementar `server.py` principal

2. **Implementar Supervisor LangGraph**
   - ✅ Estado definido (`state.py`)
   - ⏳ Implementar lógica completa (veja arquivo `supervisor.py` fornecido)

3. **Testar sistema completo**
   ```bash
   # Terminal 1: MCP Server
   python src/mcp_server/server.py
   
   # Terminal 2: Teste agentes
   python -c "import asyncio; from src.agents.weather_agent import WeatherAgent; asyncio.run(WeatherAgent().execute('clima em São Paulo'))"
   ```

## 🎯 Benefícios da Nova Arquitetura

| Aspecto | Antes (A2A + MCP) | Depois (LangGraph + MCP) |
|---------|-------------------|------------------------|
| **Protocolos** | 2 protocolos | 1 protocolo |
| **Complexidade** | Alta | Média |
| **Performance** | Boa | Excelente |
| **Manutenibilidade** | Difícil | Fácil |
| **Testabilidade** | Complexa | Simples |

## 📝 Arquivos de Referência

Os seguintes arquivos foram criados como referência para completar a implementação:

1. `refactoring-plan.md` - Plano completo de refatoração
2. `mcp-server-main.py` - Servidor MCP completo
3. `weather-tools.py` - Ferramentas de clima
4. `database-tools.py` - Ferramentas de banco de dados
5. `supervisor.py` - Supervisor LangGraph completo

Copie o conteúdo destes arquivos para as pastas corretas para completar a implementação.

## 👍 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-feature`
3. Commit suas mudanças: `git commit -m 'Add nova feature'`
4. Push para a branch: `git push origin feature/nova-feature`
5. Abra um Pull Request

---

**Desenvolvido com ❤️ usando LangGraph + MCP (SEM A2A!)**
