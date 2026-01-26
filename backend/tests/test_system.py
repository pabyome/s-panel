from fastapi.testclient import TestClient
import os
from unittest.mock import patch, MagicMock
from app.api.deps import get_current_user
from main import app

# app.dependency_overrides... - Removed
# client = TestClient(app) - Removed

def test_list_directory_success(client):
    # We mock os.scandir to avoid reading real FS
    with patch("os.path.exists", return_value=True):
        with patch("os.path.isdir", return_value=True):
             with patch("os.scandir") as mock_scandir:
                # Mock entries
                entry_dir = MagicMock()
                entry_dir.name = "test_dir"
                entry_dir.is_dir.return_value = True
                entry_dir.path = "/tmp/test_dir"

                entry_file = MagicMock()
                entry_file.name = "test_file.txt"
                entry_file.is_dir.return_value = False
                entry_file.path = "/tmp/test_file.txt"

                # Context manager mock
                mock_scandir.return_value.__enter__.return_value = [entry_dir, entry_file]

                # /tmp is in our ALLOWED_ROOTS
                response = client.get("/api/v1/system/path/list?path=/tmp")
                assert response.status_code == 200
                data = response.json()
                assert data["current_path"] == "/tmp" # Mocked abstractions might vary, but logic holds
                assert len(data["items"]) == 2
                assert data["items"][0]["name"] == "test_dir" # Sorted dirs first
                assert data["items"][1]["name"] == "test_file.txt"

def test_list_directory_not_found(client):
    with patch("os.path.exists", return_value=False):
        # Must use an allowed path to pass the Safe Mode check first
        response = client.get("/api/v1/system/path/list?path=/tmp/nonexistent")
        assert response.status_code == 404

def test_list_directory_is_file(client):
     with patch("os.path.exists", return_value=True):
        with patch("os.path.isdir", return_value=False):
            response = client.get("/api/v1/system/path/list?path=/tmp/file.txt")
            assert response.status_code == 400
