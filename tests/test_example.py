"""
Teste de exemplo para o sistema multi-agent.
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from src.main import MultiAgentSystem


@pytest.fixture
def system():
    """Fixture para sistema multi-agent."""
    return MultiAgentSystem()


@pytest.mark.asyncio
async def test_system_initialization(system):
    """Testa inicialização do sistema."""
    await system.initialize()
    assert system.app is not None
    assert system.app.title == "Multi-Agent System"


def test_health_endpoint():
    """Testa endpoint de health check."""
    system = MultiAgentSystem()
    asyncio.run(system.initialize())
    
    client = TestClient(system.app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["system"] == "multi-agent"


def test_root_endpoint():
    """Testa endpoint raiz."""
    system = MultiAgentSystem()
    asyncio.run(system.initialize())
    
    client = TestClient(system.app)
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["system"] == "Multi-Agent System"
    assert "agents" in data
    assert "protocols" in data


def test_query_endpoint():
    """Testa endpoint de consulta."""
    system = MultiAgentSystem()
    asyncio.run(system.initialize())
    
    client = TestClient(system.app)
    response = client.post("/query", json={"query": "Hello World"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "response" in data