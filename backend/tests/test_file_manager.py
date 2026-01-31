import os
import shutil
import pytest
from app.services.file_manager import FileManager

@pytest.fixture
def temp_dir(tmp_path):
    d = tmp_path / "test_dir"
    d.mkdir()
    return d

def test_list_directory(temp_dir):
    (temp_dir / "file1.txt").write_text("hello")
    (temp_dir / "subfolder").mkdir()

    items = FileManager.list_directory(str(temp_dir))

    assert len(items) == 2
    names = {item["name"] for item in items}
    assert "file1.txt" in names
    assert "subfolder" in names

def test_read_file(temp_dir):
    f = temp_dir / "file.txt"
    f.write_text("content")

    content = FileManager.read_file(str(f))
    assert content == "content"

def test_create_directory(temp_dir):
    new_dir = temp_dir / "new_folder"
    FileManager.create_directory(str(new_dir))

    assert new_dir.exists()
    assert new_dir.is_dir()

def test_save_file(temp_dir):
    f = temp_dir / "saved.txt"
    FileManager.save_file(str(f), "saved content")

    assert f.exists()
    assert f.read_text() == "saved content"

def test_delete_item(temp_dir):
    f = temp_dir / "todelete.txt"
    f.write_text("bye")

    FileManager.delete_item(str(f))
    assert not f.exists()

    d = temp_dir / "todelete_dir"
    d.mkdir()
    FileManager.delete_item(str(d))
    assert not d.exists()
