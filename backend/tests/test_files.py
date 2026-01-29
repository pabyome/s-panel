import os
import shutil
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.services.file_manager import FileManager
from app.api.deps import get_current_user
from main import app

# Setup a temporary directory for tests
@pytest.fixture
def temp_roots():
    tmp_dir = tempfile.mkdtemp()

    roots = {
        "test_web": os.path.join(tmp_dir, "web"),
        "test_logs": os.path.join(tmp_dir, "logs")
    }

    for path in roots.values():
        os.makedirs(path)

    yield roots

    shutil.rmtree(tmp_dir)

@pytest.fixture
def mock_file_manager(temp_roots):
    with patch("app.services.file_manager.FileManager.ALLOWED_ROOTS", temp_roots):
        yield

def test_file_manager_validation(mock_file_manager, temp_roots):
    web_root = temp_roots["test_web"]

    # Valid path
    valid_path = os.path.join(web_root, "index.html")
    with open(valid_path, "w") as f:
        f.write("hello")

    assert FileManager.validate_path(valid_path) == os.path.realpath(valid_path)

    # Invalid path
    with pytest.raises(ValueError, match="Access denied"):
        FileManager.validate_path("/etc/passwd")

def test_file_manager_list(mock_file_manager, temp_roots):
    # List roots
    items = FileManager.list_directory("/")
    assert len(items) == 2
    names = [item["name"] for item in items]
    assert "test_web" in names
    assert "test_logs" in names

    # List subdir
    web_root = temp_roots["test_web"]
    with open(os.path.join(web_root, "test.txt"), "w") as f:
        f.write("content")

    items = FileManager.list_directory(web_root)
    assert len(items) == 1
    assert items[0]["name"] == "test.txt"

def test_api_list_files(mock_file_manager, temp_roots):
    # Mock auth
    app.dependency_overrides[get_current_user] = lambda: MagicMock()

    client = TestClient(app)

    response = client.get("/api/v1/files/list?path=/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Test access denied
    response = client.get("/api/v1/files/list?path=/etc/passwd")
    # depending on system, /etc/passwd might exist, but it's not in ALLOWED_ROOTS (which are mocked)
    # so it should return 403
    assert response.status_code == 403

    app.dependency_overrides = {}

def test_api_create_file(mock_file_manager, temp_roots):
    app.dependency_overrides[get_current_user] = lambda: MagicMock()
    client = TestClient(app)

    web_root = temp_roots["test_web"]
    new_file = os.path.join(web_root, "new.txt")

    response = client.post("/api/v1/files/create", json={"path": new_file, "is_dir": False})
    assert response.status_code == 200
    assert os.path.exists(new_file)

    app.dependency_overrides = {}
