import os
import shutil
from pathlib import Path
from typing import List, Dict, Union

class FileManager:
    MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB

    @staticmethod
    def list_directory(path: str) -> List[Dict[str, Union[str, bool, int]]]:
        # Basic validation to ensure we are using absolute paths or safe defaults
        # For this panel, we assume we want to explore the whole system, so we resolve to absolute.
        # If path is empty or "/", list root.

        if not path:
            path = "/"

        target_path = Path(path).resolve()

        if not target_path.exists():
            # Fallback to root if path doesn't exist? Or raise error?
            # Raising error is better.
            raise FileNotFoundError(f"Path not found: {path}")

        if not target_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")

        items = []
        try:
            with os.scandir(target_path) as it:
                for entry in it:
                    try:
                        stat = entry.stat()
                        items.append({
                            "name": entry.name,
                            "path": str(Path(entry.path)),
                            "is_dir": entry.is_dir(),
                            "size": stat.st_size,
                            "modified": stat.st_mtime,
                            "permissions": oct(stat.st_mode)[-3:]
                        })
                    except OSError:
                        # Skip files we can't access
                        continue
        except PermissionError:
             raise PermissionError(f"Permission denied: {path}")

        # Sort: directories first, then alphabetical
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        return items

    @staticmethod
    def read_file(path: str) -> str:
        target_path = Path(path).resolve()
        if not target_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not target_path.is_file():
             raise IsADirectoryError(f"Path is a directory: {path}")

        # Check file size
        if target_path.stat().st_size > FileManager.MAX_FILE_SIZE:
             raise ValueError("File is too large to read")

        # simplistic text read
        try:
            return target_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise ValueError("File is not a valid text file")

    @staticmethod
    def write_file(path: str, content: str) -> bool:
        target_path = Path(path).resolve()
        # parent must exist
        if not target_path.parent.exists():
             raise FileNotFoundError(f"Directory not found: {target_path.parent}")

        target_path.write_text(content, encoding="utf-8")
        return True

    @staticmethod
    def create_item(path: str, is_directory: bool) -> bool:
        target_path = Path(path).resolve()
        if target_path.exists():
            raise FileExistsError(f"Item already exists: {path}")

        if is_directory:
            target_path.mkdir(parents=True, exist_ok=True)
        else:
            target_path.touch()
        return True

    @staticmethod
    def delete_item(path: str) -> bool:
        target_path = Path(path).resolve()
        if not target_path.exists():
            raise FileNotFoundError(f"Path not found: {path}")

        if target_path.is_dir():
            shutil.rmtree(target_path)
        else:
            target_path.unlink()
        return True
