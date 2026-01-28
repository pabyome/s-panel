from unittest.mock import patch
from fastapi.testclient import TestClient

def test_partial_path_traversal_prevention(client):
    """
    Verifies that a path like /tmp-secret is blocked when /tmp is an allowed root.
    """
    with patch("os.path.exists", return_value=True), \
         patch("os.path.isdir", return_value=True):

        # Allowed: /tmp
        # Attack: /tmp-secret
        response = client.get("/api/v1/system/path/list?path=/tmp-secret")

        # Should be forbidden
        assert response.status_code == 403, f"Expected 403 Forbidden, got {response.status_code}"
        assert "Path not allowed" in response.json()["detail"]

def test_exact_root_allowed(client):
    """
    Verifies that /tmp is allowed.
    """
    with patch("os.path.exists", return_value=True), \
         patch("os.path.isdir", return_value=True), \
         patch("os.scandir") as mock_scandir:

        mock_scandir.return_value.__enter__.return_value = []

        response = client.get("/api/v1/system/path/list?path=/tmp")
        assert response.status_code == 200

def test_sub_directory_allowed(client):
    """
    Verifies that /tmp/subdir is allowed.
    """
    with patch("os.path.exists", return_value=True), \
         patch("os.path.isdir", return_value=True), \
         patch("os.scandir") as mock_scandir:

        mock_scandir.return_value.__enter__.return_value = []

        response = client.get("/api/v1/system/path/list?path=/tmp/subdir")
        assert response.status_code == 200
