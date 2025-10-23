# type:ignore
import asyncio
import json

from contextlib import asynccontextmanager

import click

from fastmcp.utilities.logging import get_logger
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult, ReadResourceResult


logger = get_logger(__name__)


@asynccontextmanager
async def init_session(host, port, transport):
    if transport == 'sse':
        url = f'http://{host}:{port}/sse'
        async with sse_client(url) as (read_stream, write_stream):
            async with ClientSession(
                read_stream=read_stream, write_stream=write_stream
            ) as session:
                logger.debug('SSE ClientSession created, initializing...')
                await session.initialize()
                logger.info('SSE ClientSession initialized successfully.')
                yield session
    elif transport == 'stdio':
        stdio_params = StdioServerParameters(
            command='uv',
            args=['run', 'a2a-mcp'],
        )
        async with stdio_client(stdio_params) as (read_stream, write_stream):
            async with ClientSession(
                read_stream=read_stream,
                write_stream=write_stream,
            ) as session:
                logger.debug('STDIO ClientSession created, initializing...')
                await session.initialize()
                logger.info('STDIO ClientSession initialized successfully.')
                yield session
    else:
        logger.error(f'Unsupported transport type: {transport}')
        raise ValueError(
            f"Unsupported transport type: {transport}. Must be 'sse' or 'stdio'."
        )


async def find_agent_simple(session: ClientSession, query) -> CallToolResult:
    logger.info(f"Calling 'find_agent_simple' with query: '{query[:50]}...'")
    return await session.call_tool(
        name='find_agent_simple',
        arguments={'query': query},
    )


async def read_cards(session: ClientSession) -> ReadResourceResult:
    logger.info('Reading resource list of agent cards')
    return await session.read_resource('resource://agent_cards/list')


async def get_card(session: ClientSession, name: str) -> ReadResourceResult:
    logger.info(f'Reading agent card: {name}')
    return await session.read_resource(f'resource://agent_cards/{name}')


async def get_weather(session: ClientSession, city: str) -> CallToolResult:
    logger.info(f"Calling 'get_weather' tool for city: {city}")
    return await session.call_tool(name='get_weather', arguments={'city': city})


async def query_db(session: ClientSession) -> CallToolResult:
    logger.info("Calling 'query_travel_data' tool")
    return await session.call_tool(
        name='query_travel_data',
        arguments={
            'query': "SELECT id, name, city, hotel_type, room_type, price_per_night FROM hotels WHERE city='London'",
        },
    )


async def main(host, port, transport, query, resource, tool, city):
    logger.info('Starting Client to connect to MCP (no Google)')
    async with init_session(host, port, transport) as session:
        if query:
            result = await find_agent_simple(session, query)
            data = json.loads(result.content[0].text)
            logger.info(json.dumps(data, indent=2))
        if resource:
            if resource == 'list':
                result = await read_cards(session)
            else:
                result = await get_card(session, resource)
            data = json.loads(result.contents[0].text)
            logger.info(json.dumps(data, indent=2))
        if tool:
            if tool == 'weather':
                result = await get_weather(session, city or 'São Paulo')
                data = json.loads(result.content[0].text)
                logger.info(json.dumps(data, indent=2))
            if tool == 'query_db':
                result = await query_db(session)
                data = json.loads(result.content[0].text)
                logger.info(json.dumps(data, indent=2))


@click.command()
@click.option('--host', default='localhost', help='MCP Host')
@click.option('--port', default='10100', help='MCP Port')
@click.option('--transport', default='sse', help='MCP Transport (sse|stdio)')
@click.option('--find_agent', help='Query to find an agent (simple matcher)')
@click.option('--resource', help="Agent card resource name (use 'list' or a card name)")
@click.option('--tool_name', type=click.Choice(['weather', 'query_db']), help='Tool to execute')
@click.option('--city', default='São Paulo', help='City for weather tool')
def cli(host, port, transport, find_agent, resource, tool_name, city):
    asyncio.run(main(host, port, transport, find_agent, resource, tool_name, city))


if __name__ == '__main__':
    cli()
