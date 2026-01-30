import os
import tempfile
import pytest
from fastapi.testclient import TestClient

def test_get_log_content_path_traversal_prevention(client: TestClient):
    """
    Test that the path traversal vulnerability is fixed.
    We attempt to read a file outside allowed directories, expecting a 403.
    """
    # Create a secret file outside of standard log locations
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
        tmp.write("SECRET_DATA_12345")
        tmp_path = tmp.name

    try:
        # Attempt to read the file using the endpoint
        response = client.get(f"/api/v1/logs/content?path={tmp_path}")

        # We expect access to be denied
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    finally:
        os.remove(tmp_path)

def test_clear_file_arbitrary_write_prevention(client: TestClient):
    """
    Test that arbitrary file clearing is prevented.
    """
    # Create a file with content
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
        tmp.write("IMPORTANT_DATA")
        tmp_path = tmp.name

    try:
        # Attempt to clear the file
        response = client.post("/api/v1/logs/clear_file", json={"path": tmp_path})

        # We expect access to be denied
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

        # Verify content is still there
        with open(tmp_path, "r") as f:
             content = f.read()
        assert content == "IMPORTANT_DATA"

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
