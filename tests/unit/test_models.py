"""
Testes unitários para modelos de domínio.
"""
import pytest
from datetime import datetime
from src.core.domain.models import (
    Message, Task, ConversationContext, 
    WeatherQuery, WeatherResponse, AgentResponse,
    AgentType, MessageType
)


class TestMessage:
    """Testes para modelo Message."""
    
    def test_message_creation(self):
        """Testa criação de mensagem."""
        message = Message(
            id="msg-001",
            content="Hello, World!",
            sender="test-agent"
        )
        
        assert message.id == "msg-001"
        assert message.content == "Hello, World!"
        assert message.sender == "test-agent"
        assert message.message_type == MessageType.TEXT
        assert isinstance(message.timestamp, datetime)
    
    def test_message_with_metadata(self):
        """Testa mensagem com metadados."""
        metadata = {"conversation_id": "conv-001", "priority": "high"}
        message = Message(
            id="msg-002",
            content="Test message",
            sender="agent",
            receiver="other-agent",
            metadata=metadata
        )
        
        assert message.metadata == metadata
        assert message.receiver == "other-agent"


class TestTask:
    """Testes para modelo Task."""
    
    def test_task_creation(self):
        """Testa criação de tarefa."""
        task = Task(
            id="task-001",
            content="Process weather query",
            agent_type=AgentType.ACTION
        )
        
        assert task.id == "task-001"
        assert task.content == "Process weather query"
        assert task.agent_type == AgentType.ACTION
        assert task.status == "pending"
        assert isinstance(task.created_at, datetime)


class TestWeatherQuery:
    """Testes para modelo WeatherQuery."""
    
    def test_weather_query_creation(self):
        """Testa criação de consulta meteorológica."""
        query = WeatherQuery(
            location="São Paulo",
            latitude=-23.5505,
            longitude=-46.6333
        )
        
        assert query.location == "São Paulo"
        assert query.latitude == -23.5505
        assert query.longitude == -46.6333
        assert "temperature_2m" in query.parameters