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

EXPLICIT_FILES = {
    "system/syslog": "/var/log/syslog",
    "system/auth.log": "/var/log/auth.log",
    "spanel/app.log": "app.log",
}


def validate_log_path(path: str) -> str:
    """
    Centralized security check for log file paths.
    Resolves real path, checks existence, validates against allowed directories or explicit files.
    """
    if not path:
        raise HTTPException(status_code=400, detail="Path is required")

    # Resolve to real path to prevent traversal attacks
    real_path = os.path.realpath(path)

    # Check if it is one of the explicit files
    is_explicit = False
    for exp_path in EXPLICIT_FILES.values():
        if real_path == os.path.realpath(exp_path):
            is_explicit = True
            break

    if not os.path.exists(real_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Check if file is in allowed directories
    allowed = is_explicit
    if not allowed:
        # Check explicit LOG_DIRECTORIES
        for dir_path in LOG_DIRECTORIES.values():
            abs_allowed = os.path.realpath(dir_path)
            if os.path.commonpath([abs_allowed, real_path]) == abs_allowed:
                allowed = True
                break

    if not allowed:
        raise HTTPException(status_code=403, detail="Path not in allowed log directories")

    # Security check - only allow log files if not explicit
    if not is_explicit and not real_path.endswith(".log"):
        raise HTTPException(status_code=400, detail="Only .log files can be accessed")

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
    for name, path in EXPLICIT_FILES.items():
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
    validated_path = validate_log_path(path)

    # Read last N lines
    try:
        # Using tail command is efficient
        import subprocess

        result = subprocess.run(["tail", "-n", str(lines), validated_path], capture_output=True, text=True)
        return LogContent(content=result.stdout, lines=lines)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
def clear_log_file(data: dict, current_user: CurrentUser):  # Expect {"path": "..."}
    """Clear (truncate) a log file"""
    path = data.get("path")
    validated_path = validate_log_path(path)

    try:
        with open(validated_path, "w") as f:
            f.truncate(0)
        return {"status": "cleared", "message": f"Log file {validated_path} cleared"}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear log: {str(e)}")


@router.post("/clear_file")
def clear_file(data: dict, current_user: CurrentUser):  # path
    path = data.get("path")
    validated_path = validate_log_path(path)

    try:
        # Truncate
        with open(validated_path, "w") as f:
            f.truncate(0)
        return {"status": "cleared"}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear log: {str(e)}")
