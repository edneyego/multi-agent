#!/bin/bash
# Script: refatorar_multiagent_struct.sh
# Finaliza migração do projeto para padrão LangGraph + MCP (sem A2A nem ADK/Google)
# Execute a partir da raiz do projeto

set -e

echo "== REMOVENDO DIRETÓRIO LEGADO: src/a2a_mcp =="
rm -rf src/a2a_mcp

echo "== CRIANDO ESTRUTURA PADRÃO =="
mkdir -p src/mcp/tools src/mcp/resources
mkdir -p src/agents
mkdir -p src/orchestrator

echo "== MOVENDO SERVER MCP =="
# Ajuste para onde está seu MCP server (se vier de backup/manual)
if [ -f server.py ]; then
    mv server.py src/mcp/server.py
fi
# Caso existam ferramentas/resources em arquivos próprios, mova manualmente (crie-os!)
# Exemplo:
# mv weather.py src/mcp/tools/weather.py

echo "== MIGRANDO AGENTES =="
# Ajuste se seus arquivos-agente têm nomes diferentes
for ag in weather_agent info_agent data_agent finance_agent planner_agent hotel_booking_agent car_rental_agent air_ticketing_agent orchestrator_agent
do
    if [ -f "$ag.py" ]; then
        mv "$ag.py" src/agents/"$ag.py"
    fi
done

echo "== MIGRANDO ORQUESTRADOR =="
# Ajuste conforme os nomes existentes no seu projeto
if [ -f main.py ]; then mv main.py src/orchestrator/main.py; fi
if [ -f supervisor.py ]; then mv supervisor.py src/orchestrator/supervisor.py; fi
if [ -f mcp_client.py ]; then mv mcp_client.py src/orchestrator/mcp_client.py; fi
if [ -f api.py ]; then mv api.py src/orchestrator/api.py; fi
if [ -f dynamic_tools.py ]; then mv dynamic_tools.py src/orchestrator/dynamic_tools.py; fi
if [ -f graph.py ]; then mv graph.py src/orchestrator/graph.py; fi

echo "== CRIANDO/ATUALIZANDO CLI =="
touch src/cli.py

echo "== REMOVENDO __pycache__ E .pyc =="
find . -name '__pycache__' -type d -exec rm -rf {} +
find . -name '*.pyc' -delete

echo "== AJUSTE TODOS OS IMPORTS (BUSCA) =="
echo "Revise manualmente todos os imports! Busque por 'a2a_mcp', 'google-adk', e paths antigos e troque por src correto, ex:"
echo "from mcp.tools.weather import ..."
echo "from agents.weather_agent import ..."
echo "from orchestrator.supervisor import ..."
echo ""
echo "Sugestão para revisão de código:"
echo "grep -Ri 'a2a_mcp' src/"
echo "grep -Ri 'adk' src/"
echo "grep -Ri 'google' src/"
echo ""
echo "==== ESTRUTURA PRONTA ===="
tree -L 3 src

echo
echo "Finalize testando e rodando:"
echo "python src/mcp/server.py"
echo "python src/orchestrator/main.py"
echo "python src/cli.py \"Como está o clima em São Paulo?\""
echo
echo "Depois commit/push normalmente!"
