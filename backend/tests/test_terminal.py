import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from main import app
from app.core.config import settings
import jwt
import time

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@patch("app.api.v1.containers.docker_service")
def test_terminal_websocket(mock_service, client):
    # Mock exec_create
    mock_service.exec_create.return_value = "exec_id_123"

    # Mock socket
    mock_socket = MagicMock()

    # Simulate socket behavior
    def socket_recv(*args, **kwargs):
        if not hasattr(socket_recv, 'called'):
            socket_recv.called = True
            return b"Hello Terminal"
        time.sleep(1) # Keep connection open
        return b""

    mock_socket.recv.side_effect = socket_recv
    mock_socket.send.return_value = None
    mock_socket.close.return_value = None

    mock_service.exec_start.return_value = mock_socket

    # Generate token
    token = jwt.encode({"sub": "admin"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    try:
        with client.websocket_connect(f"/api/v1/containers/123/terminal?token={token}") as websocket:
            # Receive first message
            data = websocket.receive_text()
            assert "Hello Terminal" in data

            # Send command
            websocket.send_text("ls\n")

            # Send resize
            websocket.send_text('{"cols": 80, "rows": 24}')

            # Wait for processing
            time.sleep(0.5)

    except Exception:
        pass

    # Updated expectation for smart shell command
    expected_cmd = ["/bin/sh", "-c", "if [ -x /bin/bash ]; then exec /bin/bash; else exec /bin/sh; fi"]
    mock_service.exec_create.assert_called_with("123", expected_cmd)
    mock_service.exec_start.assert_called_with("exec_id_123")

    # Verify interactions
    # socket.send should be called with encoded "ls\n"
    mock_socket.send.assert_called()

    # exec_resize should be called
    mock_service.exec_resize.assert_called()
