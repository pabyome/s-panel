import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.api.deps import get_current_user

# Mock the CronManager service to avoid messing with actual crontab
@patch("app.services.cron_manager.CronManager._get_cron")
def test_list_jobs(mock_get_cron, client: TestClient):
    # Setup mock cron data
    mock_cron = MagicMock()
    mock_job = MagicMock()
    mock_job.command = "echo hello"
    mock_job.slices = "* * * * *"
    mock_job.comment = "spanel-id:12345 | Test Job"
    mock_job.is_enabled.return_value = True

    # Iterating over mock_cron yields mock_job
    mock_cron.__iter__.return_value = [mock_job]
    mock_get_cron.return_value = mock_cron

    response = client.get("/api/v1/cron/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["command"] == "echo hello"
    assert data[0]["id"] == "12345"
    assert "Test Job" in data[0]["comment"]

@patch("app.services.cron_manager.CronManager._get_cron")
def test_add_job(mock_get_cron, client: TestClient):
    mock_cron = MagicMock()
    mock_job = MagicMock()
    mock_job.is_valid.return_value = True
    mock_cron.new.return_value = mock_job
    mock_get_cron.return_value = mock_cron

    payload = {
        "command": "python script.py",
        "schedule": "*/5 * * * *",
        "comment": "My Script"
    }
    response = client.post("/api/v1/cron/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["command"] == "python script.py"
    assert data["schedule"] == "*/5 * * * *"
    assert "spanel-id:" in data["comment"]

    # Verify cron.write() was called
    mock_cron.write.assert_called_once()

@patch("app.services.cron_manager.CronManager._get_cron")
def test_delete_job(mock_get_cron, client: TestClient):
    mock_cron = MagicMock()
    mock_job = MagicMock()
    mock_job.comment = "spanel-id:target-id | To Delete"

    # Setup iteration for delete search
    mock_cron.__iter__.return_value = [mock_job]
    mock_get_cron.return_value = mock_cron

    response = client.delete("/api/v1/cron/target-id")
    assert response.status_code == 200
    assert response.json() == {"status": "deleted"}

    # Verify cron.remove(job) and cron.write() called
    mock_cron.remove.assert_called_with(mock_job)
    mock_cron.write.assert_called_once()

@patch("app.services.cron_manager.CronManager._get_cron")
def test_add_invalid_job(mock_get_cron, client: TestClient):
    mock_cron = MagicMock()
    mock_job = MagicMock()
    mock_job.is_valid.return_value = False # Invalid schedule
    mock_cron.new.return_value = mock_job
    mock_get_cron.return_value = mock_cron

    payload = {
        "command": "cmd",
        "schedule": "invalid schedule",
        "comment": "bad"
    }
    response = client.post("/api/v1/cron/", json=payload)
    assert response.status_code == 400
    assert "Invalid schedule" in response.json()["detail"]
