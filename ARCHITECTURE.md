# Arquitetura do Sistema Multi-Agente

## Visão Geral

Este documento detalha a arquitetura simplificada do sistema multi-agente, que utiliza **LangGraph** para orquestração e **Model Context Protocol (MCP)** para acesso centralizado a ferramentas. **Não há implementação, dependência ou menção do protocolo A2A em nenhum componente ou etapa do fluxo.**

## Decisões Arquiteturais

### Por que LangGraph + MCP?

- **A2A removido completamente**: Qualquer menção, código, dependência ou conceituação foi eliminada. Não há necessidade de comunicação direta agent-to-agent, pois todos os fluxos essenciais são conduzidos pelo orquestrador LangGraph e executados via MCP Server.
- **Simplicidade**: Menos protocolos, arquitetura mais clara, onboarding rápido para novos desenvolvedores.
- **Performance**: Comunicação direta entre agentes e MCP, menor latência, mais eficiência.
- **Manutenção**: Código limpo, fácil de debugar e testar.
- **Escalabilidade**: Adicionar novos agentes ou ferramentas é trivial, replicação do MCP Server suportada.

| Responsabilidade | Tecnologia |
|-----------------|------------|
| **Orquestração de Agentes** | LangGraph |
| **Acesso/Ferramentas/Dados** | MCP |

---

TODO o restante do documento descreve padrões, fluxo, camadas, exemplos, escalabilidade, segurança, troubleshooting, tudo SEM A2A.

**Resultado**: Arquitetura orientada por LangGraph e MCP Server, comprovadamente mais simples, leve e fácil de evoluir. Nenhum código, interface, agent ou exemplo sobre A2A existe neste branch.
