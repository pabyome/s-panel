import pytest
from app.services.file_manager import FileManager
from fastapi import HTTPException
import os
import shutil

# Use a temporary directory for testing
TEST_ROOT = "/tmp/test_file_manager"

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup
    if not os.path.exists(TEST_ROOT):
        os.makedirs(TEST_ROOT)
    # Add TEST_ROOT to ALLOWED_ROOTS for testing purposes
    # We modify the class attribute directly, which affects the class globally in this process
    original_roots = list(FileManager.ALLOWED_ROOTS)
    FileManager.ALLOWED_ROOTS = original_roots + [TEST_ROOT]

    yield

    # Teardown
    FileManager.ALLOWED_ROOTS = original_roots
    if os.path.exists(TEST_ROOT):
        shutil.rmtree(TEST_ROOT)

def test_list_directory():
    # Create some files
    with open(os.path.join(TEST_ROOT, "file1.txt"), "w") as f:
        f.write("content")
    os.makedirs(os.path.join(TEST_ROOT, "subdir"))

    result = FileManager.list_directory(TEST_ROOT)
    items = result["items"]

    assert len(items) == 2
    assert any(i["name"] == "file1.txt" and not i["is_dir"] for i in items)
    assert any(i["name"] == "subdir" and i["is_dir"] for i in items)

def test_read_file():
    file_path = os.path.join(TEST_ROOT, "read.txt")
    with open(file_path, "w") as f:
        f.write("hello world")

    content = FileManager.read_file(file_path)
    assert content == "hello world"

def test_save_file():
    file_path = os.path.join(TEST_ROOT, "save.txt")
    FileManager.save_file(file_path, "new content")

    with open(file_path, "r") as f:
        assert f.read() == "new content"

def test_create_item():
    dir_path = os.path.join(TEST_ROOT, "new_dir")
    FileManager.create_item(dir_path, is_dir=True)
    assert os.path.isdir(dir_path)

    file_path = os.path.join(TEST_ROOT, "new_file.txt")
    FileManager.create_item(file_path, is_dir=False)
    assert os.path.isfile(file_path)

def test_delete_item():
    file_path = os.path.join(TEST_ROOT, "delete.txt")
    with open(file_path, "w") as f:
        f.write("bye")

    FileManager.delete_item(file_path)
    assert not os.path.exists(file_path)

def test_security_check():
    # /usr is typically not in ALLOWED_ROOTS (default list: /var/www, /home, /etc/supervisor, /var/log, /tmp, /www)
    # We just need to make sure we try a path that is NOT in ALLOWED_ROOTS + TEST_ROOT
    forbidden_path = "/root_forbidden"
    with pytest.raises(HTTPException) as excinfo:
        FileManager.list_directory(forbidden_path)
    assert excinfo.value.status_code == 403
