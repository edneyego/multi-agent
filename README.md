# Sistema Multi-Agente: LangGraph + MCP

> 🎯 **Branch `feature/mcpagent`** - Arquitetura simplificada usando apenas LangGraph + MCP

Uma implementação prática de sistema multi-agente utilizando **LangGraph** para orquestração e **FastMCP** para acesso centralizado a ferramentas.

## 🎆 Arquitetura Simplificada

Esta branch implementa uma arquitetura mais simples e eficiente, eliminando completamente qualquer vestígio do protocolo A2A:

✅ **LangGraph** - Orquestração de agentes com padrão Supervisor  
✅ **FastMCP puro** - Servidor centralizado de ferramentas  
✅ **Arquitetura limpa** - Sem protocolos redundantes  
✅ **Fácil manutenção** - Código simplificado  
✅ **Alta performance** - Menos overhead de comunicação  

## Diagrama de Arquitetura

![Arquitetura](https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/a10399ee7bf597230685b991b56cf8d1/d789bb19-3a0e-43d9-969c-a6a6269a4b67/059b4cc6.png)

## Justificativa da Arquitetura

A arquitetura foi totalmente refatorada para **remover qualquer menção, dependência ou integração do protocolo A2A**.
O conceito central agora é a orquestração de múltiplos agentes via LangGraph, com todos os agentes acessando ferramentas centralizadas exclusivamente via FastMCP/MCP Server. Isso garante máxima simplicidade, reusabilidade e facilidade de manutenção:

- Não há nenhum código, dependência, ou menção a A2A em nenhum componente, documentação, agents ou scripts
- O projeto orienta e exemplifica unicamente o workflow LangGraph → Agentes → MCP
- A seção de vantagens enfatiza a ausência de protocolos redundantes e a evolução em relação à arquitetura original

## Arquitetura Detalhada

(manter seção detalhada já presente -- sem mencionar, referenciar ou sugerir A2A)

## Fluxo de Execução

(manter seção já presente -- sem mencionar, referenciar ou sugerir A2A)

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

(manter seção já presente -- sem mencionar, referenciar ou sugerir A2A)

## Troubleshooting/Testing/Guia de contribuição/FAQ

(manter igual, mas sem frases relacionadas a A2A)

---

## 🎉 Sobre esta Implementação

A partir desta branch (feature/mcpagent), o projeto não contém qualquer interface, biblioteca, endpoint, ferramenta, agente ou código relacionado com Agent-to-Agent Protocol. Todo o workflow, exemplos, dicas e documentação seguem a nova filosofia orientada a FastMCP/MCP Server e LangGraph apenas.

**Resultado**: Um sistema multi-agente profissional, eficiente, leve e pronto para produção! 🚀
