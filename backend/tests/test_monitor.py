from fastapi.testclient import TestClient
from unittest.mock import patch
from app.services.system_monitor import SystemMonitor
# Import main app directly
# Assuming main.py is in backend/ and PYTHONPATH includes backend/
# The structure is backend/app/main.py or backend/main.py?
# Based on earlier exploration, it is backend/main.py
from main import app

def test_websocket_monitor_stats():
    mock_stats = {
        "cpu": {"percent": 10.0, "count": 4},
        "memory": {"percent": 50.0},
        "disk": {"percent": 20.0},
        "uptime": 100,
        "load_avg": {"1min": 0.5},
        "os_info": {"system": "Linux"}
    }

    # Patch the method on the class
    with patch.object(SystemMonitor, "get_all_stats", return_value=mock_stats):
        with TestClient(app) as client:
            with client.websocket_connect("/api/v1/monitor/ws") as websocket:
                # Wait for the first message
                data = websocket.receive_json()
                assert data == mock_stats
