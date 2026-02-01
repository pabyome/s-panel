from unittest.mock import patch, MagicMock
from app.services.supervisor_manager import SupervisorManager

@patch("app.services.supervisor_manager.xmlrpc.client.ServerProxy")
def test_read_log_stdout(mock_server_proxy, client):
    # Setup mock
    mock_supervisor = MagicMock()
    mock_server_proxy.return_value.__enter__.return_value = mock_supervisor
    mock_supervisor.supervisor.readProcessStdoutLog.return_value = "stdout log content"

    response = client.get("/api/v1/supervisor/processes/test_process/logs?channel=stdout")
    assert response.status_code == 200
    assert response.json()["log"] == "stdout log content"
    mock_supervisor.supervisor.readProcessStdoutLog.assert_called_with("test_process", 0, 2000)

@patch("app.services.supervisor_manager.xmlrpc.client.ServerProxy")
def test_read_log_stderr(mock_server_proxy, client):
    # Setup mock
    mock_supervisor = MagicMock()
    mock_server_proxy.return_value.__enter__.return_value = mock_supervisor
    mock_supervisor.supervisor.readProcessStderrLog.return_value = "stderr log content"

    # Default offset/length
    response = client.get("/api/v1/supervisor/processes/test_process/logs?channel=stderr")
    assert response.status_code == 200
    assert response.json()["log"] == "stderr log content"
    mock_supervisor.supervisor.readProcessStderrLog.assert_called_with("test_process", 0, 2000)

@patch("app.services.supervisor_manager.xmlrpc.client.ServerProxy")
def test_read_log_default(mock_server_proxy, client):
    # Setup mock
    mock_supervisor = MagicMock()
    mock_server_proxy.return_value.__enter__.return_value = mock_supervisor
    mock_supervisor.supervisor.readProcessStdoutLog.return_value = "default log content"

    # No channel param -> stdout
    response = client.get("/api/v1/supervisor/processes/test_process/logs")
    assert response.status_code == 200
    assert response.json()["log"] == "default log content"
    mock_supervisor.supervisor.readProcessStdoutLog.assert_called_with("test_process", 0, 2000)
