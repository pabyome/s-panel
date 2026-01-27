import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app
import asyncio

# Use client fixture from conftest if possible, but for now explicit is fine too.
# But using conftest fixture ensures DB overrides are in place.

@pytest.fixture
def mock_system_monitor():
    with patch("app.services.system_monitor.SystemMonitor.get_all_stats") as mock:
        mock.return_value = {
            "cpu": {"percent": 50.0},
            "memory": {"percent": 60.0},
            "disk": {"percent": 70.0},
            "load_avg": {"1min": 1.0},
            "uptime": 1000,
            "os_info": {"system": "Linux"}
        }
        yield mock

@pytest.fixture
def mock_sleep():
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock:
        yield mock

def test_monitor_websocket(mock_system_monitor, mock_sleep, client):
    # Using 'client' fixture from conftest

    # Connect to the websocket
    # The URL needs to be correct. prefix="/api/v1/monitor"
    with client.websocket_connect("/api/v1/monitor/ws") as websocket:
        # Wait for the first message
        data = websocket.receive_json()

        # Verify the structure
        assert "cpu" in data
        assert data["cpu"]["percent"] == 50.0
        assert data["os_info"]["system"] == "Linux"

def test_monitor_websocket_multiple_clients(mock_system_monitor, mock_sleep, client):
    # Connect first client
    with client.websocket_connect("/api/v1/monitor/ws") as ws1:
        # Connect second client
        with client.websocket_connect("/api/v1/monitor/ws") as ws2:

            # Both should receive data
            data1 = ws1.receive_json()
            data2 = ws2.receive_json()

            assert data1["cpu"]["percent"] == 50.0
            assert data2["cpu"]["percent"] == 50.0

            # We can't easily test the loop repeating without actually waiting or complex mocking.
            # But verifying they both got the first message is good enough for "broadcast".
