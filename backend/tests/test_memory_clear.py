import pytest
from unittest.mock import patch, MagicMock
from app.services.system_monitor import SystemMonitor
import subprocess

def test_clear_system_memory_success():
    with patch("app.services.system_monitor.subprocess.run") as mock_run:
        result = SystemMonitor.clear_system_memory()
        assert result is True
        assert mock_run.call_count == 2
        mock_run.assert_any_call("sync", shell=True, check=True)
        mock_run.assert_any_call("echo 3 > /proc/sys/vm/drop_caches", shell=True, check=True)

def test_clear_system_memory_failure():
    with patch("app.services.system_monitor.subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")
        result = SystemMonitor.clear_system_memory()
        assert result is False

def test_clear_system_memory_exception():
    with patch("app.services.system_monitor.subprocess.run") as mock_run:
        mock_run.side_effect = Exception("error")
        result = SystemMonitor.clear_system_memory()
        assert result is False

def test_api_clear_memory_success(client):
    with patch("app.services.system_monitor.SystemMonitor.clear_system_memory", return_value=True) as mock_clear:
        response = client.post("/api/v1/system/memory/clear")
        assert response.status_code == 200
        assert response.json() == {"message": "System memory cleared successfully"}
        mock_clear.assert_called_once()

def test_api_clear_memory_failure(client):
    with patch("app.services.system_monitor.SystemMonitor.clear_system_memory", return_value=False) as mock_clear:
        response = client.post("/api/v1/system/memory/clear")
        assert response.status_code == 500
        assert response.json()["detail"] == "Failed to clear system memory"
        mock_clear.assert_called_once()
