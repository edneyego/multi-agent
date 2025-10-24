# type: ignore

import json
import logging
import sys
import traceback
from pathlib import Path

import click
import httpx
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import (
    BasePushNotificationSender,
    InMemoryPushNotificationConfigStore,
    InMemoryTaskStore,
)
from a2a.types import AgentCard
from a2a_mcp.common import prompts
from a2a_mcp.common.agent_executor import GenericAgentExecutor
from a2a_mcp.common.utils import config_logging
from a2a_mcp.agents.adk_travel_agent import TravelAgent
from a2a_mcp.agents.orchestrator_agent import OrchestratorAgent
from a2a_mcp.agents.weather_agent import WeatherAgent


# Configure logging early
config_logging()
logger = logging.getLogger(__name__)


def _dump_agent_card(card_path: Path, raw_json: dict):
    try:
        logger.info(f"AgentCard raw JSON loaded from {card_path}:")
        logger.info(json.dumps(raw_json, indent=2, ensure_ascii=False))
    except Exception:
        logger.warning("Failed to pretty-print agent card JSON", exc_info=True)


def get_agent(agent_card: AgentCard):
    """Get the agent, given an agent card."""
    logger.info(f"Creating agent for card: {agent_card.name}")
    logger.debug(f"Agent capabilities: {getattr(agent_card, 'capabilities', None)}")
    logger.debug(f"Agent url: {getattr(agent_card, 'url', None)}")
    try:
        if agent_card.name == 'Orchestrator Agent':
            logger.info('Creating OrchestratorAgent')
            return OrchestratorAgent()
        elif agent_card.name == 'WeatherAgent':
            logger.info('Creating WeatherAgent')
            return WeatherAgent()
        elif agent_card.name == 'Air Ticketing Agent':
            logger.info('Creating Air Ticketing Agent')
            return TravelAgent(
                agent_name='AirTicketingAgent',
                description='Book air tickets given a criteria',
                instructions=prompts.AIRFARE_COT_INSTRUCTIONS,
            )
        elif agent_card.name == 'Hotel Booking Agent':
            logger.info('Creating Hotel Booking Agent')
            return TravelAgent(
                agent_name='HotelBookingAgent',
                description='Book hotels given a criteria',
                instructions=prompts.HOTELS_COT_INSTRUCTIONS,
            )
        elif agent_card.name == 'Car Rental Agent':
            logger.info('Creating Car Rental Agent')
            return TravelAgent(
                agent_name='CarRentalBookingAgent',
                description='Book rental cars given a criteria',
                instructions=prompts.CARS_COT_INSTRUCTIONS,
            )
        else:
            logger.error(f'Unknown agent type: {agent_card.name}')
            raise ValueError(f'Unknown agent type: {agent_card.name}')
    except Exception as e:
        logger.error(f'Error creating agent {agent_card.name}: {e}', exc_info=True)
        raise e


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=10101)
@click.option('--agent-card', 'agent_card', required=True)
def main(host, port, agent_card):
    """Starts an Agent server."""
    try:
        logger.info(f'Starting agent server with card: {agent_card}')
        
        if not agent_card:
            raise ValueError('Agent card is required')
            
        agent_card_path = Path(agent_card)
        if not agent_card_path.exists():
            raise FileNotFoundError(f"Agent card file not found: {agent_card}")
            
        with agent_card_path.open() as file:
            data = json.load(file)
        _dump_agent_card(agent_card_path, data)
        
        agent_card_obj = AgentCard(**data)
        logger.info(f'Loaded agent card: {agent_card_obj.name}')

        # Create HTTP client
        client = httpx.AsyncClient()
        
        # Create notification components
        push_notification_config_store = InMemoryPushNotificationConfigStore()
        push_notification_sender = BasePushNotificationSender(
            client, config_store=push_notification_config_store
        )

        # Create the agent
        agent = get_agent(agent_card_obj)
        logger.info(f'Successfully created agent: {type(agent).__name__}')

        # Create request handler
        request_handler = DefaultRequestHandler(
            agent_executor=GenericAgentExecutor(agent=agent),
            task_store=InMemoryTaskStore(),
            push_config_store=push_notification_config_store,
            push_sender=push_notification_sender,
        )
        logger.info('Request handler created successfully')

        # Create A2A server
        server = A2AStarletteApplication(
            agent_card=agent_card_obj, 
            http_handler=request_handler
        )
        logger.info('A2A server application created successfully')

        logger.info(f'Starting server on {host}:{port}')
        
        # Hook uvicorn access/error logs to DEBUG for deep diagnostics
        uvicorn_logger = logging.getLogger('uvicorn')
        uvicorn_access_logger = logging.getLogger('uvicorn.access')
        uvicorn_error_logger = logging.getLogger('uvicorn.error')
        uvicorn_logger.setLevel(logging.DEBUG)
        uvicorn_access_logger.setLevel(logging.DEBUG)
        uvicorn_error_logger.setLevel(logging.DEBUG)
        
        uvicorn.run(
            server.build(), 
            host=host, 
            port=port,
            log_level="debug",
            access_log=True
        )
        
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Error: Invalid JSON in agent card file '{agent_card}': {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f'An error occurred during server startup: {e}\n{traceback.format_exc()}')
        sys.exit(1)


if __name__ == '__main__':
    main()
