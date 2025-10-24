#!/bin/bash

# Pure FastMCP Multi-Agent System Runner
# Este script executa o servidor MCP puro (sem FastAPI)

set -e

echo "🚀 Iniciando Multi-Agent System com FastMCP PURO"
echo "================================================"
echo "📡 Protocolo: MCP (Model Context Protocol)"
echo "🔧 Implementação: FastMCP puro (SEM FastAPI)"
echo "================================================"

# Verificar se estamos no diretório correto
if [ ! -f "src/a2a_mcp/mcp/server.py" ]; then
    echo "❌ Erro: Execute este script do diretório raiz do projeto"
    exit 1
fi

# Verificar se o Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Erro: Python3 não encontrado"
    exit 1
fi

# Verificar dependências
echo "📦 Verificando dependências..."
if ! python3 -c "import fastmcp" &> /dev/null; then
    echo "❌ Erro: fastmcp não instalado. Execute: pip install fastmcp"
    exit 1
fi

if ! python3 -c "import pandas" &> /dev/null; then
    echo "❌ Erro: pandas não instalado. Execute: pip install pandas"
    exit 1
fi

if ! python3 -c "import httpx" &> /dev/null; then
    echo "❌ Erro: httpx não instalado. Execute: pip install httpx"
    exit 1
fi

echo "✅ Dependências verificadas"

# Configurar variáveis de ambiente
export MCP_TRANSPORT=${MCP_TRANSPORT:-"stdio"}
export MCP_HOST=${MCP_HOST:-"127.0.0.1"}
export MCP_PORT=${MCP_PORT:-"8000"}

echo "🔧 Configuração:"
echo "   Transport: $MCP_TRANSPORT"
if [ "$MCP_TRANSPORT" != "stdio" ]; then
    echo "   Host: $MCP_HOST:$MCP_PORT"
fi

# Verificar se existem agent cards
if [ -d "agent_cards" ]; then
    CARD_COUNT=$(find agent_cards -name "*.json" | wc -l)
    echo "🎴 Agent cards encontrados: $CARD_COUNT"
else
    echo "⚠️  Diretório agent_cards não encontrado - criando estrutura básica"
    mkdir -p agent_cards
fi

# Verificar base de dados
if [ -f "travel_agency.db" ]; then
    echo "🗄️  Base de dados travel_agency.db encontrada"
else
    echo "⚠️  Base de dados travel_agency.db não encontrada"
fi

echo "================================================"
echo "🎯 Iniciando servidor FastMCP puro..."
echo "💡 NOTA: Esta implementação NÃO usa FastAPI"
echo "================================================"

# Executar servidor MCP puro
python3 src/a2a_mcp/mcp/server.py $MCP_TRANSPORT
