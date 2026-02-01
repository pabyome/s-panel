from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
import os
from app.api.deps import CurrentUser

router = APIRouter()


class LogFile(BaseModel):
    name: str
    path: str
    size_bytes: int
    modified_at: float


class LogContent(BaseModel):
    content: str
    lines: int


# Configuration for allowed log paths
LOG_DIRECTORIES = {
    "nginx": "/var/log/nginx",
    "system": "/var/log",
    "spanel": "/var/log",  # assuming spanel logs here, or we can add app logs
}

EXPLICIT_FILES = [
    ("system/syslog", "/var/log/syslog"),
    ("system/auth.log", "/var/log/auth.log"),
    ("spanel/app.log", "app.log"),  # relative to run dir?
]


def validate_log_path(path: str) -> str:
    """
    Validates that the path is safe to access.
    Returns the absolute resolved path or raises HTTPException.
    """
    if not path:
        raise HTTPException(status_code=400, detail="Path is required")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Resolve symlinks and ..
        real_path = os.path.realpath(path)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid path")

    # Check explicit files
    for _, explicit_path in EXPLICIT_FILES:
        if os.path.exists(explicit_path):
            if os.path.realpath(explicit_path) == real_path:
                return real_path

    # Check directories
    is_allowed_dir = False
    for _, dir_path in LOG_DIRECTORIES.items():
        if not os.path.exists(dir_path):
            continue
        real_dir = os.path.realpath(dir_path)
        # Use commonpath to ensure it's truly inside
        if os.path.commonpath([real_dir, real_path]) == real_dir:
            is_allowed_dir = True
            break

    if not is_allowed_dir:
        raise HTTPException(status_code=403, detail="Access denied: Path not allowed")

    # Enforce extension for directory-based files
    if not real_path.endswith(".log"):
         raise HTTPException(status_code=403, detail="Access denied: Only .log files allowed")

    return real_path


@router.get("/files", response_model=List[LogFile])
def list_log_files(current_user: CurrentUser):
    logs = []

    # helper to add logs
    def scan_dir(category, path):
        if not os.path.exists(path):
            return
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    if entry.is_file() and entry.name.endswith(".log"):
                        logs.append(
                            LogFile(
                                name=f"{category}/{entry.name}",
                                path=entry.path,
                                size_bytes=entry.stat().st_size,
                                modified_at=entry.stat().st_mtime,
                            )
                        )
        except PermissionError:
            pass

    scan_dir("nginx", LOG_DIRECTORIES["nginx"])
    # scan_dir("system", LOG_DIRECTORIES["system"]) # Too noisy, maybe just specific ones?

    # Add explicit important files
    for name, path in EXPLICIT_FILES:
        if os.path.exists(path):
            try:
                stat = os.stat(path)
                logs.append(LogFile(name=name, path=path, size_bytes=stat.st_size, modified_at=stat.st_mtime))
            except:
                pass

    return logs


@router.get("/content", response_model=LogContent)
def get_log_content(path: str, lines: int = Query(100, le=1000), current_user: CurrentUser = None):
    # Security: Validate path is against allowed
    safe_path = validate_log_path(path)

    # Read last N lines
    try:
        # Using tail command is efficient
        import subprocess

        result = subprocess.run(["tail", "-n", str(lines), safe_path], capture_output=True, text=True)
        return LogContent(content=result.stdout, lines=lines)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
def clear_log_file(data: dict, current_user: CurrentUser):  # Expect {"path": "..."}
    """Clear (truncate) a log file"""
    path = data.get("path")
    safe_path = validate_log_path(path)

    try:
        with open(safe_path, "w") as f:
            f.truncate(0)
        return {"status": "cleared", "message": f"Log file {path} cleared"}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear log: {str(e)}")


@router.post("/clear_file")
def clear_file(data: dict, current_user: CurrentUser):  # path
    path = data.get("path")
    safe_path = validate_log_path(path)

    try:
        # Truncate
        with open(safe_path, "w") as f:
            f.truncate(0)
        return {"status": "cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear log: {str(e)}")
