import os
import shutil
import pwd
import grp

class FileManager:

    @staticmethod
    def _validate_path(path: str):
        return os.path.abspath(path)

    @staticmethod
    def list_directory(path: str) -> list[dict]:
        path = FileManager._validate_path(path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path not found: {path}")
        if not os.path.isdir(path):
             raise NotADirectoryError(f"Path is not a directory: {path}")

        items = []
        try:
            with os.scandir(path) as it:
                for entry in it:
                    try:
                        stat = entry.stat()
                        try:
                            owner = pwd.getpwuid(stat.st_uid).pw_name
                        except KeyError:
                            owner = str(stat.st_uid)

                        try:
                            group = grp.getgrgid(stat.st_gid).gr_name
                        except KeyError:
                            group = str(stat.st_gid)

                        items.append({
                            "name": entry.name,
                            "path": entry.path,
                            "is_dir": entry.is_dir(),
                            "size": stat.st_size,
                            "modified": stat.st_mtime,
                            "permissions": oct(stat.st_mode)[-3:],
                            "owner": owner,
                            "group": group
                        })
                    except (PermissionError, FileNotFoundError):
                        continue
        except PermissionError:
             raise PermissionError(f"Permission denied accessing: {path}")

        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        return items

    @staticmethod
    def read_file(path: str) -> str:
        path = FileManager._validate_path(path)
        if not os.path.exists(path):
             raise FileNotFoundError(f"File not found: {path}")
        if not os.path.isfile(path):
             raise IsADirectoryError(f"Path is a directory: {path}")

        if os.path.getsize(path) > 1024 * 1024: # 1MB limit
            raise ValueError("File too large to edit (max 1MB)")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            raise ValueError("File is not text/utf-8 encoded")

    @staticmethod
    def save_file(path: str, content: str) -> bool:
        path = FileManager._validate_path(path)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except PermissionError:
            raise PermissionError(f"Permission denied writing to: {path}")

    @staticmethod
    def create_directory(path: str) -> bool:
        path = FileManager._validate_path(path)
        if os.path.exists(path):
            raise FileExistsError(f"Path already exists: {path}")

        try:
            os.makedirs(path)
            return True
        except PermissionError:
             raise PermissionError(f"Permission denied creating: {path}")

    @staticmethod
    def delete_item(path: str) -> bool:
        path = FileManager._validate_path(path)
        if not os.path.exists(path):
             raise FileNotFoundError(f"Path not found: {path}")

        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return True
        except PermissionError:
             raise PermissionError(f"Permission denied deleting: {path}")
