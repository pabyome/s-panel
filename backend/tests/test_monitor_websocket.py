from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

def test_websocket_monitor():
    # Mock the system monitor to avoid real system calls and control the data
    with patch("app.services.system_monitor.SystemMonitor.get_all_stats") as mock_stats:
        mock_stats.return_value = {"cpu": {"percent": 10.5}, "memory": {"percent": 20.0}}

        with client.websocket_connect("/api/v1/monitor/ws") as websocket:
            # Receive first message
            data = websocket.receive_json()
            assert data == {"cpu": {"percent": 10.5}, "memory": {"percent": 20.0}}

            # Receive second message (verifying the loop works)
            data = websocket.receive_json()
            assert data == {"cpu": {"percent": 10.5}, "memory": {"percent": 20.0}}
