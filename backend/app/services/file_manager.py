import os
import shutil
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from fastapi import HTTPException

class FileManager:
    ALLOWED_ROOTS = ["/var/www", "/home", "/etc/supervisor", "/var/log", "/tmp", "/www"]
    MAX_FILE_SIZE = 1024 * 1024  # 1MB limit for reading files

    @staticmethod
    def validate_path(path: str) -> str:
        # Use realpath to resolve symlinks preventing traversal attacks
        clean_path = os.path.realpath(path)
        # Check if the path is one of the roots or inside one of them
        is_allowed = any(clean_path == root or clean_path.startswith(root + os.sep) for root in FileManager.ALLOWED_ROOTS)

        if not is_allowed:
            raise HTTPException(
                status_code=403, detail=f"Path not allowed. Allowed roots: {', '.join(FileManager.ALLOWED_ROOTS)}"
            )
        return clean_path

    @staticmethod
    def list_directory(path: str) -> Dict[str, Any]:
        # Special handling for root path to list allowed roots
        if path == "/" or path == "":
            items = []
            for root in FileManager.ALLOWED_ROOTS:
                if os.path.exists(root):
                    try:
                        stats = os.stat(root)
                        items.append({
                            "name": root,  # Display full path for roots to avoid ambiguity
                            "is_dir": True,
                            "path": root,
                            "size": stats.st_size,
                            "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                            "permissions": oct(stats.st_mode)[-3:]
                        })
                    except OSError:
                        continue
            return {
                "items": items,
                "current_path": "/",
                "parent_path": ""
            }

        clean_path = FileManager.validate_path(path)

        if not os.path.exists(clean_path):
            raise HTTPException(status_code=404, detail="Path not found")

        if not os.path.isdir(clean_path):
             raise HTTPException(status_code=400, detail="Path is not a directory")

        items = []
        try:
            with os.scandir(clean_path) as entries:
                for entry in entries:
                    try:
                        stats = entry.stat()
                        items.append({
                            "name": entry.name,
                            "is_dir": entry.is_dir(),
                            "path": entry.path,
                            "size": stats.st_size,
                            "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                            "permissions": oct(stats.st_mode)[-3:]
                        })
                    except FileNotFoundError:
                        # File might have disappeared
                        continue
        except PermissionError:
            raise HTTPException(status_code=403, detail="Permission denied")

        # Sort: Directories first, then files. A-Z.
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))

        return {
            "items": items,
            "current_path": clean_path,
            "parent_path": os.path.dirname(clean_path)
        }

    @staticmethod
    def read_file(path: str) -> str:
        clean_path = FileManager.validate_path(path)

        if not os.path.exists(clean_path):
            raise HTTPException(status_code=404, detail="File not found")

        if os.path.isdir(clean_path):
            raise HTTPException(status_code=400, detail="Path is a directory")

        try:
            if os.path.getsize(clean_path) > FileManager.MAX_FILE_SIZE:
                 raise HTTPException(status_code=400, detail="File too large to read")
        except OSError:
             # Could fail on special files
             pass

        try:
            with open(clean_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File is not text")
        except PermissionError:
            raise HTTPException(status_code=403, detail="Permission denied")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def save_file(path: str, content: str):
        clean_path = FileManager.validate_path(path)

        # We allow creating new files via save_file if path allows
        # But usually we want to ensure parent dir exists
        parent = os.path.dirname(clean_path)
        if not os.path.exists(parent):
             raise HTTPException(status_code=404, detail="Parent directory does not exist")

        try:
            with open(clean_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except PermissionError:
            raise HTTPException(status_code=403, detail="Permission denied")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def create_item(path: str, is_dir: bool):
        # path is the full path of the new item
        clean_path = FileManager.validate_path(path)

        if os.path.exists(clean_path):
            raise HTTPException(status_code=400, detail="Item already exists")

        try:
            if is_dir:
                os.makedirs(clean_path)
            else:
                with open(clean_path, 'w') as f:
                    pass
        except PermissionError:
            raise HTTPException(status_code=403, detail="Permission denied")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def delete_item(path: str):
        clean_path = FileManager.validate_path(path)

        if not os.path.exists(clean_path):
            raise HTTPException(status_code=404, detail="Item not found")

        try:
            if os.path.isdir(clean_path):
                shutil.rmtree(clean_path)
            else:
                os.remove(clean_path)
        except PermissionError:
            raise HTTPException(status_code=403, detail="Permission denied")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
