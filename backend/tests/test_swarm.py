import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from main import app
from app.api.deps import get_current_user

# Helper for auth override
def mock_get_current_user():
    user = MagicMock()
    user.username = "admin"
    user.is_superuser = True
    return user

@pytest.fixture
def client_authenticated():
    app.dependency_overrides[get_current_user] = mock_get_current_user
    with TestClient(app) as client:
        yield client
    app.dependency_overrides = {}

@patch("app.api.v1.swarm.docker_service")
def test_get_swarm_info(mock_service, client_authenticated):
    mock_service.get_swarm_info.return_value = {
        "active": True,
        "is_manager": True,
        "nodes": 3,
        "managers": 1,
        "cluster_id": "abc12345"
    }

    response = client_authenticated.get("/api/v1/swarm/info")
    assert response.status_code == 200
    assert response.json()["active"] is True
    assert response.json()["nodes"] == 3

@patch("app.api.v1.swarm.docker_service")
def test_init_swarm(mock_service, client_authenticated):
    mock_service.init_swarm.return_value = "node_id_123"

    response = client_authenticated.post("/api/v1/swarm/init")
    assert response.status_code == 200
    assert response.json()["node_id"] == "node_id_123"

@patch("app.api.v1.swarm.docker_service")
def test_get_stats(mock_service, client_authenticated):
    mock_service.get_system_stats.return_value = {
        "cpu_percent": 10.5,
        "memory": {"total": 8000000, "used": 4000000, "percent": 50},
        "containers": {"total": 5, "running": 3}
    }

    response = client_authenticated.get("/api/v1/swarm/stats")
    assert response.status_code == 200
    assert response.json()["cpu_percent"] == 10.5
