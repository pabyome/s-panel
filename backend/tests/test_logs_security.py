import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.api.v1 import logs

def test_get_log_content_traversal(client: TestClient):
    """
    Test that reading arbitrary files is blocked.
    """
    target_file = os.path.abspath("pyproject.toml")
    # This should fail if vulnerability exists (returns 200)
    response = client.get(f"/api/v1/logs/content?path={target_file}&lines=10")

    assert response.status_code in [403, 400], f"VULNERABILITY: Successfully read non-log file! Status: {response.status_code}"

def test_clear_file_traversal(client: TestClient):
    """
    Test that clearing arbitrary files is blocked.
    """
    target_file = os.path.abspath("pyproject.toml")

    # Mock open to prevent actual file destruction during test if vulnerability exists
    with patch("builtins.open", MagicMock()) as mock_open:
        response = client.post("/api/v1/logs/clear_file", json={"path": target_file})

        assert response.status_code in [403, 400], f"VULNERABILITY: Successfully cleared non-log file! Status: {response.status_code}"

def test_valid_log_access(client: TestClient, tmp_path):
    """
    Test that accessing a valid log file in an allowed directory works.
    """
    # Create a dummy log file in a temp dir
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    log_file = log_dir / "test.log"
    log_file.write_text("log content\nline 2")

    # Patch LOG_DIRECTORIES to include this temp dir
    # We patch the dictionary in the module
    with patch.dict(logs.LOG_DIRECTORIES, {"test": str(log_dir)}, clear=False):
        response = client.get(f"/api/v1/logs/content?path={str(log_file)}&lines=10")

        # This might fail BEFORE refactor because get_log_content has NO validation logic (it allows everything),
        # so it actually SHOULD pass (return 200).
        # BUT after refactor, it should also pass.
        assert response.status_code == 200
        assert "log content" in response.json()["content"]
