# type: ignore
import json
import os
import sqlite3
import traceback

from pathlib import Path

import numpy as np
import pandas as pd
import httpx

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger


logger = get_logger(__name__)
AGENT_CARDS_DIR = 'agent_cards'
SQLLITE_DB = 'travel_agency.db'


def load_agent_cards():
    """Loads agent card data from JSON files within a specified directory.

    Returns:
        (card_uris, agent_cards): lists with resource URIs and agent card dicts
    """
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
                        f'An unexpected error occurred processing {filename}: {e}',
                        exc_info=True,
                    )
    logger.info(
        f'Finished loading agent cards. Found {len(agent_cards)} cards.'
    )
    return card_uris, agent_cards


def serve(host, port, transport):  # noqa: PLR0915
    """Initializes and runs the Agent Cards MCP server (no Google dependencies).

    Args:
        host: The hostname or IP address to bind the server to.
        port: The port number to bind the server to.
        transport: The transport mechanism for the MCP server (e.g., 'stdio', 'sse').
    """
    logger.info('Starting Agent Cards MCP Server (no Google)')
    mcp = FastMCP('agent-cards', host=host, port=port)

    card_uris, agent_cards = load_agent_cards()
    df = pd.DataFrame({'card_uri': card_uris, 'agent_card': agent_cards})

    @mcp.tool(
        name='find_agent_simple',
        description='Naive keyword match to find an agent card (no embeddings).',
    )
    def find_agent_simple(query: str) -> dict:
        q = (query or '').lower()
        if 'clima' in q or 'weather' in q:
            # Prefer any card with name containing 'Weather'
            for i, row in df.iterrows():
                name = row['agent_card'].get('name', '').lower()
                if 'weather' in name:
                    return row['agent_card']
        # fallback: first card
        return df.iloc[0]['agent_card'] if len(df) else {}

    @mcp.tool(
        name='get_weather',
        description='Get current weather for a city using Open-Meteo (no API key).',
    )
    def get_weather(city: str) -> dict:
        try:
            # Geocoding
            geocode_url = 'https://geocoding-api.open-meteo.com/v1/search'
            params = {'name': city, 'count': 1, 'language': 'pt', 'format': 'json'}
            r = httpx.get(geocode_url, params=params, timeout=20.0)
            r.raise_for_status()
            data = r.json()
            if not data.get('results'):
                return {'error': f'Localização não encontrada: {city}'}
            res = data['results'][0]
            lat, lon = res['latitude'], res['longitude']

            # Weather
            weather_url = 'https://api.open-meteo.com/v1/forecast'
            wparams = {
                'latitude': lat,
                'longitude': lon,
                'current': 'temperature_2m,wind_speed_10m,weather_code',
                'timezone': 'auto',
            }
            wr = httpx.get(weather_url, params=wparams, timeout=20.0)
            wr.raise_for_status()
            wd = wr.json()
            return {
                'location': {
                    'name': res.get('name'),
                    'country': res.get('country', ''),
                    'latitude': lat,
                    'longitude': lon,
                },
                'current': wd.get('current', {}),
            }
        except Exception as e:
            return {'error': str(e)}

    @mcp.tool()
    def query_travel_data(query: str) -> dict:
        """ Runs a SELECT query against the SQLite travel database. """
        logger.info(f'Query sqllite : {query}')

        if not query or not query.strip().upper().startswith('SELECT'):
            raise ValueError(f'In correct query {query}')

        try:
            with sqlite3.connect(SQLLITE_DB) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                result = {'results': [dict(row) for row in rows]}
                return json.dumps(result)
        except Exception as e:
            logger.error(f'Exception running query {e}')
            logger.error(traceback.format_exc())
            if 'no such column' in str(e).lower():
                return {
                    'error': f'Please check your query, {e}. Use the table schema to regenerate the query'
                }
            return {'error': f'{e}'}

    @mcp.resource('resource://agent_cards/list', mime_type='application/json')
    def get_agent_cards() -> dict:
        resources = {}
        logger.info('Starting read resources')
        resources['agent_cards'] = df['card_uri'].to_list()
        return resources

    @mcp.resource(
        'resource://agent_cards/{card_name}', mime_type='application/json'
    )
    def get_agent_card(card_name: str) -> dict:
        resources = {}
        logger.info(
            f'Starting read resource resource://agent_cards/{card_name}'
        )
        resources['agent_card'] = (
            df.loc[
                df['card_uri'] == f'resource://agent_cards/{card_name}',
                'agent_card',
            ]
        ).to_list()

        return resources

    logger.info(
        f'Agent cards MCP Server at {host}:{port} and transport {transport} (no Google)'
    )
    mcp.run(transport=transport)
