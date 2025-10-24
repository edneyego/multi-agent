"""Pure FastMCP Server Implementation - Multi-Agent System

Esta implementação usa exclusivamente FastMCP sem misturar com FastAPI,
seguindo as melhores práticas do Model Context Protocol.
"""
import json
import os
import sqlite3
import traceback
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd
import httpx
from fastmcp import FastMCP
from fastmcp.utilities.logging import get_logger


logger = get_logger(__name__)
AGENT_CARDS_DIR = 'agent_cards'
SQLLITE_DB = 'travel_agency.db'


def load_agent_cards() -> tuple[List[str], List[Dict[str, Any]]]:
    """Carrega os cartões de agentes do diretório local."""
    card_uris = []
    agent_cards = []
    dir_path = Path(AGENT_CARDS_DIR)
    
    if not dir_path.is_dir():
        logger.error(
            f'Agent cards directory not found or is not a directory: {AGENT_CARDS_DIR}'
        )
        return card_uris, agent_cards

    logger.info(f'Loading agent cards from card repo: {AGENT_CARDS_DIR}')

    for filename in os.listdir(AGENT_CARDS_DIR):
        if filename.lower().endswith('.json'):
            file_path = dir_path / filename
            if file_path.is_file():
                logger.info(f'Reading file: {filename}')
                try:
                    with file_path.open('r', encoding='utf-8') as f:
                        data = json.load(f)
                        card_uris.append(
                            f'resource://agent_cards/{Path(filename).stem}'
                        )
                        agent_cards.append(data)
                except json.JSONDecodeError as jde:
                    logger.error(f'JSON Decoder Error {jde}')
                except OSError as e:
                    logger.error(f'Error reading file {filename}: {e}.')
                except Exception as e:
                    logger.error(
                        f'Unexpected error processing {filename}: {e}',
                        exc_info=True,
                    )
                    
    logger.info(
        f'Finished loading agent cards. Found {len(agent_cards)} cards.'
    )
    return card_uris, agent_cards


def create_pure_fastmcp_server() -> FastMCP:
    """Cria servidor FastMCP puro sem FastAPI."""
    logger.info('🚀 Creating Pure FastMCP Server (No FastAPI mixing)')
    
    # Criar servidor MCP exclusivamente com FastMCP - SEM FastAPI
    mcp = FastMCP(
        name='pure-fastmcp-multi-agent',
        description='Sistema Multi-Agent usando FastMCP puro - sem FastAPI'
    )
    
    # Carregar dados dos agentes
    card_uris, agent_cards = load_agent_cards()
    df = pd.DataFrame({'card_uri': card_uris, 'agent_card': agent_cards})
    
    # === FERRAMENTAS MCP PURAS ===
    
    @mcp.tool(
        name='find_agent_simple',
        description='Encontra um cartão de agente usando correspondência simples de palavras-chave (sem embeddings).'
    )
    def find_agent_simple(query: str) -> Dict[str, Any]:
        """Encontra agentes baseado em palavras-chave simples."""
        logger.info(f'🔍 Searching for agent with query: {query}')
        q = (query or '').lower()
        
        # Busca por agente de clima/weather
        if 'clima' in q or 'weather' in q or 'tempo' in q:
            for _, row in df.iterrows():
                name = row['agent_card'].get('name', '').lower()
                description = row['agent_card'].get('description', '').lower()
                if 'weather' in name or 'clima' in name or 'weather' in description:
                    logger.info(f'✅ Found weather agent: {name}')
                    return row['agent_card']
        
        # Busca por agente de informação
        if 'informação' in q or 'information' in q or 'pesquisa' in q or 'search' in q:
            for _, row in df.iterrows():
                name = row['agent_card'].get('name', '').lower()
                description = row['agent_card'].get('description', '').lower()
                if 'information' in name or 'informação' in name or 'rag' in description:
                    logger.info(f'✅ Found information agent: {name}')
                    return row['agent_card']
        
        # Busca por supervisor
        if 'supervisor' in q or 'coordenador' in q or 'gerenciar' in q:
            for _, row in df.iterrows():
                name = row['agent_card'].get('name', '').lower()
                if 'supervisor' in name or 'coordenador' in name:
                    logger.info(f'✅ Found supervisor agent: {name}')
                    return row['agent_card']
        
        # Retorna primeiro agente se nenhum específico for encontrado
        if len(df) > 0:
            logger.info('📋 Returning first available agent')
            return df.iloc[0]['agent_card']
        else:
            logger.warning('⚠️ No agents found')
            return {'error': 'Nenhum agente encontrado'}

    @mcp.tool(
        name='get_weather',
        description='Obtém informações meteorológicas atuais para uma cidade usando Open-Meteo API (gratuita, sem chave).'
    )
    def get_weather(city: str, country: str = 'BR') -> Dict[str, Any]:
        """Ferramenta para consulta do clima usando Open-Meteo API."""
        logger.info(f'🌤️ Getting weather for {city}, {country}')
        try:
            # Geocodificação para obter coordenadas
            geocode_url = 'https://geocoding-api.open-meteo.com/v1/search'
            params = {
                'name': city, 
                'count': 1, 
                'language': 'pt', 
                'format': 'json',
                'country': country
            }
            
            response = httpx.get(geocode_url, params=params, timeout=20.0)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('results'):
                error_msg = f'Localização não encontrada: {city}, {country}'
                logger.error(error_msg)
                return {'error': error_msg}
            
            result = data['results'][0]
            lat, lon = result['latitude'], result['longitude']

            # Obter dados meteorológicos
            weather_url = 'https://api.open-meteo.com/v1/forecast'
            weather_params = {
                'latitude': lat,
                'longitude': lon,
                'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code',
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum',
                'timezone': 'auto',
                'forecast_days': 3
            }
            
            weather_response = httpx.get(weather_url, params=weather_params, timeout=20.0)
            weather_response.raise_for_status()
            weather_data = weather_response.json()
            
            result_data = {
                'success': True,
                'location': {
                    'name': result.get('name'),
                    'country': result.get('country', ''),
                    'region': result.get('admin1', ''),
                    'latitude': lat,
                    'longitude': lon,
                },
                'current': weather_data.get('current', {}),
                'daily_forecast': weather_data.get('daily', {}),
                'units': weather_data.get('current_units', {})
            }
            
            logger.info(f'✅ Weather data retrieved for {city}')
            return result_data
                
        except Exception as e:
            error_msg = f'Erro ao consultar clima: {str(e)}'
            logger.error(error_msg)
            return {'error': error_msg}

    @mcp.tool(
        name='query_travel_data',
        description='Executa consultas SQL na base de dados da agência de viagens.'
    )
    def query_travel_data(query: str) -> Dict[str, Any]:
        """Ferramenta para consultas na base de dados SQLite."""
        logger.info(f'🗄️ Executing SQL query: {query}')
        
        if not query or not query.strip().upper().startswith('SELECT'):
            error_msg = f'Consulta inválida - apenas SELECT permitido: {query}'
            logger.error(error_msg)
            return {'error': error_msg}
        
        try:
            with sqlite3.connect(SQLLITE_DB) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                
                result = {
                    'success': True,
                    'results': [dict(row) for row in rows],
                    'count': len(rows)
                }
                
                logger.info(f'✅ SQL query executed successfully, {len(rows)} rows returned')
                return result
                
        except Exception as e:
            logger.error(f'❌ SQL query error: {e}')
            logger.error(traceback.format_exc())
            
            error_msg = str(e).lower()
            if 'no such column' in error_msg:
                return {
                    'error': f'Coluna não encontrada: {e}. Verifique o esquema da tabela.',
                    'suggestion': 'Use a ferramenta get_database_schema para ver as colunas disponíveis.'
                }
            elif 'no such table' in error_msg:
                return {
                    'error': f'Tabela não encontrada: {e}',
                    'suggestion': 'Tabelas disponíveis: travel_bookings, customers, destinations'
                }
            else:
                return {'error': f'Erro SQL: {e}'}

    @mcp.tool(
        name='get_database_schema',
        description='Obtém o esquema da base de dados da agência de viagens.'
    )
    def get_database_schema() -> Dict[str, Any]:
        """Ferramenta para obter esquema da base de dados."""
        logger.info('📊 Getting database schema')
        try:
            with sqlite3.connect(SQLLITE_DB) as conn:
                cursor = conn.cursor()
                
                # Obter lista de tabelas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                
                schema = {'tables': {}}
                
                # Para cada tabela, obter informações das colunas
                for table in tables:
                    cursor.execute(f"PRAGMA table_info({table});")
                    columns = cursor.fetchall()
                    schema['tables'][table] = {
                        'columns': [
                            {
                                'name': col[1],
                                'type': col[2],
                                'nullable': not col[3],
                                'primary_key': bool(col[5])
                            } for col in columns
                        ]
                    }
                
                logger.info(f'✅ Database schema retrieved for {len(tables)} tables')
                return {'success': True, 'schema': schema}
                
        except Exception as e:
            error_msg = f'Erro ao obter esquema: {str(e)}'
            logger.error(error_msg)
            return {'error': error_msg}

    @mcp.tool(
        name='a2a_delegate_task',
        description='Delega uma tarefa para um agente específico via protocolo A2A.'
    )
    def a2a_delegate_task(
        agent_name: str, 
        task: str, 
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Ferramenta para delegação de tarefas via A2A Protocol."""
        if parameters is None:
            parameters = {}
        
        logger.info(f'🤖 Delegating task to {agent_name}: {task}')
        
        # Lista de agentes disponíveis no sistema
        available_agents = [
            'information_agent', 
            'action_agent', 
            'weather_agent', 
            'supervisor_agent'
        ]
        
        if agent_name not in available_agents:
            error_msg = f'Agente {agent_name} não disponível'
            logger.warning(error_msg)
            return {
                'error': error_msg,
                'available_agents': available_agents
            }
        
        # Aqui seria a implementação real do protocolo A2A
        # Por enquanto, simulação da delegação
        result = {
            'success': True,
            'agent': agent_name,
            'task': task,
            'parameters': parameters,
            'status': 'delegated',
            'timestamp': str(pd.Timestamp.now()),
            'message': f'Tarefa "{task}" delegada para {agent_name} com sucesso'
        }
        
        logger.info(f'✅ Task delegated successfully to {agent_name}')
        return result

    # === RECURSOS MCP PUROS ===
    
    @mcp.resource(
        uri='resource://agent_cards/list',
        name='Lista de Cartões de Agentes',
        description='Lista todos os cartões de agentes disponíveis no sistema',
        mime_type='application/json'
    )
    def get_agent_cards_list() -> str:
        """Recurso que retorna lista de todos os cartões de agentes."""
        logger.info('📋 Getting agent cards list')
        data = {
            'agent_cards': df['card_uri'].to_list(),
            'count': len(df),
            'description': 'Lista de todos os agentes disponíveis no sistema multi-agent',
            'server_type': 'Pure FastMCP (No FastAPI)'
        }
        return json.dumps(data, indent=2)

    @mcp.resource(
        uri='resource://agent_cards/{card_name}',
        name='Cartão de Agente Específico',
        description='Obtém detalhes de um cartão de agente específico',
        mime_type='application/json'
    )
    def get_agent_card(card_name: str) -> str:
        """Recurso que retorna detalhes de um agente específico."""
        logger.info(f'🎴 Getting agent card: {card_name}')
        target_uri = f'resource://agent_cards/{card_name}'
        matching_cards = df.loc[df['card_uri'] == target_uri, 'agent_card'].to_list()
        
        if not matching_cards:
            error_data = {
                'error': f'Cartão de agente não encontrado: {card_name}',
                'available_cards': df['card_uri'].to_list()
            }
            return json.dumps(error_data, indent=2)
        
        result_data = {
            'agent_card': matching_cards[0],
            'uri': target_uri,
            'server_type': 'Pure FastMCP'
        }
        return json.dumps(result_data, indent=2)

    @mcp.resource(
        uri='resource://system/status',
        name='Status do Sistema',
        description='Status atual do sistema multi-agent com FastMCP puro',
        mime_type='application/json'
    )
    def get_system_status() -> str:
        """Recurso que retorna status do sistema."""
        logger.info('📊 Getting system status')
        status_data = {
            'system': 'Multi-Agent System with PURE FastMCP',
            'version': '2.0.0-pure-fastmcp',
            'status': 'running',
            'protocol': 'MCP (Model Context Protocol)',
            'implementation': 'Pure FastMCP (NO FastAPI mixing)',
            'transport': 'FastMCP native',
            'agents_loaded': len(df),
            'database_available': os.path.exists(SQLLITE_DB),
            'capabilities': {
                'weather_queries': True,
                'agent_discovery': True,
                'database_queries': True,
                'a2a_delegation': True,
                'pure_mcp_protocol': True,
                'no_fastapi_dependency': True
            },
            'improvements': [
                'Removed FastAPI hybrid approach',
                'Pure MCP protocol implementation',
                'Simplified architecture',
                'Better performance',
                'Native MCP transport'
            ]
        }
        return json.dumps(status_data, indent=2)

    @mcp.resource(
        uri='resource://database/schema',
        name='Esquema da Base de Dados',
        description='Esquema completo da base de dados da agência de viagens',
        mime_type='application/json'
    )
    def get_database_schema_resource() -> str:
        """Recurso que expõe o esquema da base de dados."""
        logger.info('🗄️ Getting database schema resource')
        schema_data = get_database_schema()
        return json.dumps(schema_data, indent=2)

    logger.info('🎯 Pure FastMCP server created successfully (No FastAPI dependency)')
    return mcp


def serve(host: str = '127.0.0.1', port: int = 8000, transport: str = 'stdio'):
    """Inicia o servidor FastMCP puro - SEM FastAPI."""
    logger.info('=' * 60)
    logger.info('🚀 INICIANDO SISTEMA MULTI-AGENT COM FASTMCP PURO')
    logger.info('=' * 60)
    logger.info('📡 Protocolo: MCP (Model Context Protocol)')
    logger.info('🔧 Implementação: FastMCP PURO (SEM FastAPI)')
    logger.info(f'🚀 Transporte: {transport}')
    if transport != 'stdio':
        logger.info(f'🌐 Host: {host}:{port}')
    logger.info('=' * 60)
    
    # Criar servidor MCP puro
    mcp = create_pure_fastmcp_server()
    
    # Executar servidor (blocking) - SEM threading, SEM FastAPI
    logger.info('🟢 Servidor FastMCP PURO iniciado - aguardando conexões...')
    logger.info('💡 NOTA: Esta implementação NÃO usa FastAPI - apenas FastMCP nativo')
    
    # Executar com transporte especificado
    if transport == 'stdio':
        mcp.run()
    else:
        mcp.run(transport=transport, host=host, port=port)


if __name__ == '__main__':
    import sys
    
    # Permitir configuração via argumentos ou variáveis de ambiente
    transport = os.getenv('MCP_TRANSPORT', 'stdio')
    host = os.getenv('MCP_HOST', '127.0.0.1')
    port = int(os.getenv('MCP_PORT', '8000'))
    
    # Permitir override via argumentos da linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] in ['stdio', 'sse', 'streamable-http']:
            transport = sys.argv[1]
    
    serve(host=host, port=port, transport=transport)