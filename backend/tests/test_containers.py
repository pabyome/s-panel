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

@patch("app.api.v1.containers.docker_service")
def test_list_containers(mock_service, client_authenticated):
    mock_service.list_containers.return_value = [
        {
            "id": "123",
            "short_id": "12",
            "name": "test_container",
            "image": "nginx:latest",
            "status": "running",
            "state": {"Status": "running"},
            "ports": {"80/tcp": [{"HostPort": "8080"}]},
            "created": "2023-01-01"
        }
    ]

    response = client_authenticated.get("/api/v1/containers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "test_container"

@patch("app.api.v1.containers.docker_service")
def test_perform_action(mock_service, client_authenticated):
    mock_service.perform_action.return_value = {
        "id": "123",
        "short_id": "12",
        "name": "test_container",
        "image": "nginx:latest",
        "status": "exited",
        "state": {"Status": "exited"},
        "ports": {},
        "created": "2023-01-01"
    }

    response = client_authenticated.post("/api/v1/containers/123/stop")
    assert response.status_code == 200
    assert response.json()["status"] == "exited"
    mock_service.perform_action.assert_called_with("123", "stop")

@patch("app.api.v1.containers.docker_service")
def test_perform_action_remove(mock_service, client_authenticated):
    mock_service.perform_action.return_value = None

    response = client_authenticated.post("/api/v1/containers/123/remove")
    assert response.status_code == 200
    assert response.json()["message"] == "Container removed"

@patch("app.api.v1.containers.docker_service")
def test_get_logs(mock_service, client_authenticated):
    mock_service.get_logs.return_value = "Log line 1\nLog line 2"

    response = client_authenticated.get("/api/v1/containers/123/logs")
    assert response.status_code == 200
    assert response.json()["logs"] == "Log line 1\nLog line 2"

@patch("app.api.v1.containers.docker_service")
def test_run_container(mock_service, client_authenticated):
    mock_service.run_container.return_value = {
        "id": "123",
        "short_id": "12",
        "name": "new_container",
        "image": "nginx:latest",
        "status": "running",
        "state": {"Status": "running"},
        "ports": {},
        "created": "2023-01-01"
    }

    data = {
        "image": "nginx:latest",
        "name": "new_container",
        "ports": [{"container_port": 80, "host_port": 8080}],
        "restart_policy": "always"
    }

    response = client_authenticated.post("/api/v1/containers/run", json=data)
    assert response.status_code == 200
    assert response.json()["name"] == "new_container"
    mock_service.run_container.assert_called_once()
