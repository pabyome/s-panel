from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.services.system_monitor import SystemMonitor

def test_websocket_broadcast(client: TestClient):
    """
    Test that the WebSocket endpoint broadcasts system stats.
    We mock SystemMonitor.get_all_stats to return specific data and verify it's received.
    """
    mock_stats = {
        "cpu": {"percent": 10.5, "count": 4},
        "memory": {"percent": 50.0},
        "os_info": {"system": "TestOS"}
    }

    # Patch the get_all_stats method
    with patch("app.services.system_monitor.SystemMonitor.get_all_stats", return_value=mock_stats):
        with client.websocket_connect("/api/v1/monitor/ws") as websocket:
            # Receive the first message
            data = websocket.receive_json()

            # Verify the data matches our mock
            assert data == mock_stats
            assert data["cpu"]["percent"] == 10.5
            assert data["os_info"]["system"] == "TestOS"
