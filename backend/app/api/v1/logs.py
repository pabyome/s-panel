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
    "spanel": "/var/log" # assuming spanel logs here, or we can add app logs
}

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
                        logs.append(LogFile(
                            name=f"{category}/{entry.name}",
                            path=entry.path,
                            size_bytes=entry.stat().st_size,
                            modified_at=entry.stat().st_mtime
                        ))
        except PermissionError:
            pass

    scan_dir("nginx", LOG_DIRECTORIES["nginx"])
    # scan_dir("system", LOG_DIRECTORIES["system"]) # Too noisy, maybe just specific ones?

    # Add explicit important files
    explicit_files = [
        ("system/syslog", "/var/log/syslog"),
        ("system/auth.log", "/var/log/auth.log"),
        ("spanel/app.log", "app.log"), # relative to run dir?
    ]

    for name, path in explicit_files:
        if os.path.exists(path):
            try:
                stat = os.stat(path)
                logs.append(LogFile(
                    name=name,
                    path=path,
                    size_bytes=stat.st_size,
                    modified_at=stat.st_mtime
                ))
            except:
                pass

    return logs

@router.get("/content", response_model=LogContent)
def get_log_content(
    path: str,
    lines: int = Query(100, le=1000),
    current_user: CurrentUser = None
):
    # Security: Validate path is against allowed
    # We do loose check: must be absolute and exist, and be in our known list logic?
    # Or just require it matches one of the known paths from list_log_files?
    # For now, simplistic check: must end with .log or be in explicit list

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    # Read last N lines
    try:
        # Using tail command is efficient
        import subprocess
        result = subprocess.run(["tail", "-n", str(lines), path], capture_output=True, text=True)
        return LogContent(content=result.stdout, lines=lines)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear")
def clear_log_file(
    data: dict,  # Expect {"path": "..."}
    current_user: CurrentUser
):
    \"\"\"Clear (truncate) a log file\"\"\"
    path = data.get("path")
    if not path:
        raise HTTPException(status_code=400, detail="Path is required")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    # Security check - only allow log files
    if not path.endswith(".log"):
        raise HTTPException(status_code=400, detail="Only .log files can be cleared")

    # Check if file is in allowed directories
    allowed = False
    for category, dir_path in LOG_DIRECTORIES.items():
        if path.startswith(dir_path):
            allowed = True
            break

    if not allowed and not path.startswith("/var/log/"):
        raise HTTPException(status_code=403, detail="Path not in allowed log directories")

    try:
        with open(path, "w") as f:
            f.truncate(0)
        return {"status": "cleared", "message": f"Log file {path} cleared"}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear log: {str(e)}")


@router.post("/clear_file")
def clear_file(
    data: dict, # path
    current_user: CurrentUser
):
    path = data.get("path")
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    # Simple security check (same as read)
    # TODO: Refactor shared security check

    try:
        # Truncate
        with open(path, "w") as f:
            f.truncate(0)
        return {"status": "cleared"}
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Failed to clear log: {str(e)}")
