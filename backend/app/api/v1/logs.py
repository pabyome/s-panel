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

# Add explicit important files
EXPLICIT_FILES = [
    ("system/syslog", "/var/log/syslog"),
    ("system/auth.log", "/var/log/auth.log"),
    ("spanel/app.log", "app.log"),  # relative to run dir?
]


def validate_log_path(path: str) -> str:
    """
    Validates that the path is safe to access.
    - Must be an absolute path (or resolve to one).
    - Must exist and be a file.
    - Must be within allowed directories or be an explicit allowed file.
    - Prevents path traversal.
    """
    if not path:
        raise HTTPException(status_code=400, detail="Path is required")

    # Resolve symlinks and absolute path
    try:
        real_path = os.path.realpath(path)
    except OSError:
        raise HTTPException(status_code=404, detail="File not found")

    if not os.path.exists(real_path):
        raise HTTPException(status_code=404, detail="File not found")

    if not os.path.isfile(real_path):
        raise HTTPException(status_code=400, detail="Not a file")

    allowed = False

    # Check against allowed directories
    for category, dir_path in LOG_DIRECTORIES.items():
        # Resolve directory path too to ensure match works correctly
        real_dir_path = os.path.realpath(dir_path)
        # Ensure it ends with separator to prevent prefix matching (e.g. /var/log vs /var/log-secret)
        if real_path.startswith(os.path.join(real_dir_path, "")):
            allowed = True
            break

    # Check against explicit files
    if not allowed:
        for name, explicit_path in EXPLICIT_FILES:
            if os.path.realpath(explicit_path) == real_path:
                allowed = True
                break

    if not allowed:
        # Fallback check for .log extension ONLY if in a subdirectory of allowed roots,
        # but we already checked starts_with above.
        # If the original code allowed any .log file anywhere, that is insecure if user controls path.
        # So we stick to strict directory allowlist.
        raise HTTPException(status_code=403, detail="Access denied: Path not in allowed log directories")

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
    # Security: Validate path
    validated_path = validate_log_path(path)

    # Read last N lines
    try:
        # Using tail command is efficient
        import subprocess

        # Using validated_path ensures we are reading the resolved file
        result = subprocess.run(["tail", "-n", str(lines), validated_path], capture_output=True, text=True)
        return LogContent(content=result.stdout, lines=lines)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
def clear_log_file(data: dict, current_user: CurrentUser):  # Expect {"path": "..."}
    """Clear (truncate) a log file"""
    path = data.get("path")
    validated_path = validate_log_path(path)

    # Additional check: enforce .log extension for clearing to be extra safe?
    # The original code had this check.
    if not validated_path.endswith(".log") and validated_path not in [os.path.realpath(p[1]) for p in EXPLICIT_FILES]:
         # allow clearing explicit files even if no .log?
         # Original code: if not path.endswith(".log"): raise ...
         # But explicit files might not have .log? (syslog, auth.log do, but maybe others don't)
         # Let's keep the .log check or check if it is one of the explicit files.

         is_explicit = False
         for _, exp_path in EXPLICIT_FILES:
             if os.path.realpath(exp_path) == validated_path:
                 is_explicit = True
                 break

         if not is_explicit and not validated_path.endswith(".log"):
              raise HTTPException(status_code=400, detail="Only .log files can be cleared")

    try:
        with open(validated_path, "w") as f:
            f.truncate(0)
        return {"status": "cleared", "message": f"Log file {path} cleared"}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear log: {str(e)}")


@router.post("/clear_file")
def clear_file(data: dict, current_user: CurrentUser):  # path
    # This endpoint seems redundant with clear_log_file, but it was there.
    # It had NO security checks beyond existence in the original code!
    # We should apply the SAME security checks.

    path = data.get("path")
    validated_path = validate_log_path(path)

    # Apply same restriction: only clear allowed log files
    is_explicit = False
    for _, exp_path in EXPLICIT_FILES:
        if os.path.realpath(exp_path) == validated_path:
            is_explicit = True
            break

    if not is_explicit and not validated_path.endswith(".log"):
          raise HTTPException(status_code=400, detail="Only .log files can be cleared")

    try:
        # Truncate
        with open(validated_path, "w") as f:
            f.truncate(0)
        return {"status": "cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear log: {str(e)}")
