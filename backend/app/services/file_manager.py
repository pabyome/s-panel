import os
import shutil
from typing import List, Dict, Union, Optional

class FileManager:
    # Allowed roots mapping: Name -> Path
    # Using safe defaults for now, assuming these directories might exist or are standard
    ALLOWED_ROOTS = {
        "web": "/var/www",
        "configs": "/etc/nginx/sites-available",
        "logs": "/var/log"
    }

    MAX_FILE_SIZE = 1024 * 1024  # 1MB

    @classmethod
    def validate_path(cls, path: str) -> str:
        """
        Validates that the path is within one of the ALLOWED_ROOTS.
        Returns the absolute real path if valid, raises ValueError otherwise.
        """
        if not path:
            raise ValueError("Path is required")

        # Resolve symlinks and get absolute path
        real_path = os.path.realpath(path)

        allowed = False
        for root in cls.ALLOWED_ROOTS.values():
            real_root = os.path.realpath(root)
            # Ensure root ends with separator to prevent prefix matching (e.g. /var/www vs /var/www-secret)
            # But os.path.realpath might remove trailing slash.
            # So we check if it starts with root + os.sep OR it IS the root.
            if real_path == real_root or real_path.startswith(real_root + os.sep):
                allowed = True
                break

        if not allowed:
            raise ValueError(f"Access denied: Path '{path}' is not in allowed roots")

        return real_path

    @classmethod
    def list_directory(cls, path: str = "/") -> List[Dict]:
        """
        Lists directory contents.
        If path is "/" or empty, returns the list of allowed roots.
        """
        if not path or path == "/":
            items = []
            for name, root_path in cls.ALLOWED_ROOTS.items():
                # For simplicity, assuming they exist or we just show them.
                items.append({
                    "name": name,
                    "path": root_path,
                    "is_dir": True,
                    "size": 0,
                    "mtime": 0
                })
            return items

        real_path = cls.validate_path(path)

        if not os.path.isdir(real_path):
            raise ValueError("Not a directory")

        items = []
        try:
            with os.scandir(real_path) as entries:
                for entry in entries:
                    try:
                        stat = entry.stat()
                        items.append({
                            "name": entry.name,
                            "path": entry.path,
                            "is_dir": entry.is_dir(),
                            "size": stat.st_size if not entry.is_dir() else 0,
                            "mtime": stat.st_mtime
                        })
                    except OSError:
                        # Skip files we can't stat
                        continue
        except PermissionError:
            raise ValueError("Permission denied")

        return items

    @classmethod
    def read_file(cls, path: str) -> str:
        real_path = cls.validate_path(path)

        if not os.path.isfile(real_path):
            raise ValueError("Not a file")

        if os.path.getsize(real_path) > cls.MAX_FILE_SIZE:
            raise ValueError("File too large (>1MB)")

        try:
            with open(real_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except PermissionError:
            raise ValueError("Permission denied")

    @classmethod
    def write_file(cls, path: str, content: str) -> None:
        real_path = cls.validate_path(path)

        # Check if parent exists
        parent = os.path.dirname(real_path)
        if not os.path.exists(parent):
            raise ValueError("Parent directory does not exist")

        try:
            with open(real_path, "w", encoding="utf-8") as f:
                f.write(content)
        except PermissionError:
            raise ValueError("Permission denied")

    @classmethod
    def create_item(cls, path: str, is_dir: bool) -> None:
        # Validate parent allows us to create here
        parent = os.path.dirname(path)
        # We use validate_path on parent to ensure it's safe
        cls.validate_path(parent)

        # Also validate the full path (even if not exists) to ensure no traversal tricks in the filename
        # e.g. "path/to/parent/../../etc/passwd" -> realpath resolves to /etc/passwd
        # So validating the full path is crucial.
        real_path = cls.validate_path(path)

        if os.path.exists(real_path):
            raise ValueError("Item already exists")

        try:
            if is_dir:
                os.mkdir(real_path)
            else:
                with open(real_path, "w") as f:
                    pass # Create empty file
        except PermissionError:
            raise ValueError("Permission denied")

    @classmethod
    def delete_item(cls, path: str) -> None:
        real_path = cls.validate_path(path)

        if not os.path.exists(real_path):
            raise ValueError("Item not found")

        # Prevent deleting roots
        for root in cls.ALLOWED_ROOTS.values():
            real_root = os.path.realpath(root)
            if real_path == real_root:
                raise ValueError("Cannot delete root directory")

        try:
            if os.path.isdir(real_path):
                shutil.rmtree(real_path)
            else:
                os.remove(real_path)
        except PermissionError:
            raise ValueError("Permission denied")
