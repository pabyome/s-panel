from fastapi.testclient import TestClient
from app.services.file_manager import FileManager
from unittest.mock import patch, MagicMock
from app.models.database import User

# Mock User
mock_user = User(id=1, username="admin", role="admin")

def test_list_files(client: TestClient):
    with patch("app.services.file_manager.FileManager.list_directory") as mock_list, \
         patch("app.api.deps.get_current_user", return_value=mock_user):
        mock_list.return_value = [{"name": "test.txt", "is_dir": False}]
        response = client.get("/api/v1/files/list?path=/")
        assert response.status_code == 200
        assert response.json() == [{"name": "test.txt", "is_dir": False}]

def test_get_content(client: TestClient):
    with patch("app.services.file_manager.FileManager.read_file") as mock_read, \
         patch("app.api.deps.get_current_user", return_value=mock_user):
        mock_read.return_value = "hello"
        response = client.get("/api/v1/files/content?path=/test.txt")
        assert response.status_code == 200
        assert response.json() == {"content": "hello"}

def test_save_content(client: TestClient):
    with patch("app.services.file_manager.FileManager.write_file") as mock_write, \
         patch("app.api.deps.get_current_user", return_value=mock_user):
        mock_write.return_value = True
        response = client.post("/api/v1/files/content", json={"path": "/test.txt", "content": "world"})
        assert response.status_code == 200
        assert response.json() == {"message": "File saved successfully"}

def test_create_item(client: TestClient):
    with patch("app.services.file_manager.FileManager.create_item") as mock_create, \
         patch("app.api.deps.get_current_user", return_value=mock_user):
        mock_create.return_value = True
        response = client.post("/api/v1/files/create", json={"path": "/newdir", "is_directory": True})
        assert response.status_code == 200
        assert response.json() == {"message": "Item created successfully"}

def test_delete_item(client: TestClient):
    with patch("app.services.file_manager.FileManager.delete_item") as mock_delete, \
         patch("app.api.deps.get_current_user", return_value=mock_user):
        mock_delete.return_value = True
        response = client.delete("/api/v1/files/?path=/test.txt")
        assert response.status_code == 200
        assert response.json() == {"message": "Item deleted successfully"}
