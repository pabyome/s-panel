from unittest.mock import patch, MagicMock

@patch("app.services.file_manager.FileManager.list_directory")
def test_list_files(mock_list_dir, client):
    mock_list_dir.return_value = [{"name": "test", "path": "/test", "is_dir": False, "size": 10, "modified": 0, "permissions": "rwxr-xr-x", "owner": "root", "group": "root"}]
    response = client.get("/api/v1/files/list?path=/")
    assert response.status_code == 200
    assert response.json() == [{"name": "test", "path": "/test", "is_dir": False, "size": 10, "modified": 0, "permissions": "rwxr-xr-x", "owner": "root", "group": "root"}]

@patch("app.services.file_manager.FileManager.read_file")
def test_get_content(mock_read, client):
    mock_read.return_value = "content"
    response = client.get("/api/v1/files/content?path=/test.txt")
    assert response.status_code == 200
    assert response.json() == {"content": "content"}

@patch("app.services.file_manager.FileManager.write_file")
def test_save_content(mock_write, client):
    response = client.post("/api/v1/files/content", json={"path": "/test.txt", "content": "new content"})
    assert response.status_code == 200
    mock_write.assert_called_with("/test.txt", "new content")

@patch("app.services.file_manager.FileManager.create_directory")
def test_create_directory(mock_create, client):
    response = client.post("/api/v1/files/directory", json={"path": "/newdir"})
    assert response.status_code == 200
    mock_create.assert_called_with("/newdir")

@patch("app.services.file_manager.FileManager.delete_item")
def test_delete_item(mock_delete, client):
    response = client.post("/api/v1/files/delete", json={"path": "/item"})
    assert response.status_code == 200
    mock_delete.assert_called_with("/item")

@patch("app.services.file_manager.FileManager.save_upload")
def test_upload_file(mock_save_upload, client):
    file_content = b"test content"
    response = client.post(
        "/api/v1/files/upload",
        data={"path": "/uploads"},
        files={"file": ("test.txt", file_content, "text/plain")}
    )
    assert response.status_code == 200
    mock_save_upload.assert_called_once()
    # Check arguments
    args = mock_save_upload.call_args[0]
    assert args[0] == "/uploads"
    assert args[2] == "test.txt"
