import os
import shutil
import stat
from typing import List, Dict, Any
from pathlib import Path

# Try to import pwd/grp for Unix systems
try:
    import pwd
    import grp
except ImportError:
    pwd = None
    grp = None


class FileManager:
    @staticmethod
    def _get_owner(uid: int) -> str:
        if pwd:
            try:
                return pwd.getpwuid(uid).pw_name
            except KeyError:
                pass
        return str(uid)

    @staticmethod
    def _get_group(gid: int) -> str:
        if grp:
            try:
                return grp.getgrgid(gid).gr_name
            except KeyError:
                pass
        return str(gid)

    @staticmethod
    def list_directory(path: str) -> List[Dict[str, Any]]:
        target_path = Path(path).resolve()

        if not target_path.exists():
            raise FileNotFoundError(f"Path not found: {path}")

        if not target_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")

        items = []
        try:
            with os.scandir(target_path) as entries:
                for entry in entries:
                    try:
                        stat_info = entry.stat()
                        item = {
                            "name": entry.name,
                            "path": str(Path(entry.path).resolve()),
                            "is_dir": entry.is_dir(),
                            "size": stat_info.st_size,
                            "modified": stat_info.st_mtime,
                            "permissions": stat.filemode(stat_info.st_mode),
                            "owner": FileManager._get_owner(stat_info.st_uid),
                            "group": FileManager._get_group(stat_info.st_gid),
                        }
                        items.append(item)
                    except (PermissionError, FileNotFoundError):
                        continue
        except PermissionError:
            raise PermissionError(f"Permission denied: {path}")

        # Sort: Directories first, then files
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        return items

    @staticmethod
    def read_file(path: str, max_size: int = 1024 * 1024) -> str:  # 1MB limit
        target_path = Path(path).resolve()
        if not target_path.exists() or not target_path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        if target_path.stat().st_size > max_size:
            raise ValueError(f"File too large (max {max_size} bytes)")

        try:
            return target_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise ValueError("File is not text")

    @staticmethod
    def write_file(path: str, content: str):
        target_path = Path(path).resolve()
        # Ensure parent exists
        if not target_path.parent.exists():
            raise FileNotFoundError(f"Parent directory does not exist: {target_path.parent}")

        target_path.write_text(content, encoding="utf-8")

    @staticmethod
    def save_upload(directory: str, file_obj, filename: str):
        target_dir = Path(directory).resolve()
        if not target_dir.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        if not target_dir.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory}")

        # Sanitize filename to prevent directory traversal
        safe_filename = os.path.basename(filename)
        target_path = target_dir / safe_filename

        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file_obj, buffer)

    @staticmethod
    def create_directory(path: str):
        target_path = Path(path).resolve()
        target_path.mkdir(parents=False, exist_ok=False)

    @staticmethod
    def delete_item(path: str):
        target_path = Path(path).resolve()
        if not target_path.exists():
            raise FileNotFoundError(f"Path not found: {path}")

        if target_path.is_dir():
            shutil.rmtree(target_path)
        else:
            target_path.unlink()
