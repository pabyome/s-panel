from fastapi.testclient import TestClient
import os
import pytest
from unittest.mock import patch
import tempfile

def test_get_log_content_path_traversal(client: TestClient):
    # Try to read the config file which contains secrets
    target_file = "app/core/config.py"
    if not os.path.exists(target_file):
        target_file = "backend/app/core/config.py"

    # We now expect 403 Forbidden or 400
    response = client.get(f"/api/v1/logs/content?path={target_file}&lines=10")

    # Assert security enforced
    assert response.status_code in [403, 400], f"Expected 403/400, got {response.status_code}"

def test_clear_file_arbitrary_file_destruction(client: TestClient):
    dummy_file = "vulnerable_test_file.txt"
    with open(dummy_file, "w") as f:
        f.write("important data")

    try:
        # Try to clear it - should fail as it's not in allowed logs and not .log (or not allowed dir)
        # Note: validate_log_path uses realpath, so even if we are in allowed dir,
        # it checks against LOG_DIRECTORIES. Since CWD is not in LOG_DIRECTORIES, it should fail.
        response = client.post("/api/v1/logs/clear_file", json={"path": dummy_file})

        assert response.status_code in [403, 400], f"Expected 403/400, got {response.status_code}"

        # Verify it's NOT empty
        with open(dummy_file, "r") as f:
            content = f.read()
        assert content == "important data"

    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)

def test_valid_log_access(client: TestClient):
    # Create a temp dir and a log file inside
    with tempfile.TemporaryDirectory() as tmpdir:
        # realpath needed because /tmp might be symlink on some systems
        tmpdir = os.path.realpath(tmpdir)
        log_file = os.path.join(tmpdir, "test.log")
        with open(log_file, "w") as f:
            f.write("line1\nline2\nline3\n")

        # Mock LOG_DIRECTORIES to include this tmpdir
        with patch("app.api.v1.logs.LOG_DIRECTORIES", {"test": tmpdir}):
            # Test Read
            response = client.get(f"/api/v1/logs/content?path={log_file}&lines=10")
            assert response.status_code == 200
            assert response.json()["content"] == "line1\nline2\nline3\n"

            # Test Clear
            response = client.post("/api/v1/logs/clear_file", json={"path": log_file})
            assert response.status_code == 200

            with open(log_file, "r") as f:
                assert f.read() == ""
