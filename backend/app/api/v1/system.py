from fastapi import APIRouter, HTTPException, Query
import os
from typing import List
from app.api.deps import CurrentUser
from app.schemas.system import FileItem, PathListResponse

router = APIRouter()

@router.get("/path/list", response_model=PathListResponse)
def list_directory(
    path: str = Query(default="/", description="Absolute path to list"),
    current_user: CurrentUser = None
):
    # Security check: Ensure we don't go above root
    # For MVP running as root, we allow browsing everything.

    clean_path = os.path.abspath(path)

    # SAFE MODE: Restrict browsing to specific directories
    ALLOWED_ROOTS = ["/var/www", "/home", "/etc/supervisor", "/var/log", "/tmp", "/www"]

    # Check if path starts with any allowed root
    is_allowed = any(clean_path.startswith(root) for root in ALLOWED_ROOTS)

    if not is_allowed:
        # One exception: Allow root listing "/" to show the initial choices (if they match roots)
        # But our FE asks for specific path.
        # Let's return 403 Forbidden with a helpful message.
        raise HTTPException(status_code=403, detail=f"Path not allowed in Safe Mode. Allowed roots: {', '.join(ALLOWED_ROOTS)}")


    if not os.path.exists(clean_path):
        raise HTTPException(status_code=404, detail="Path not found")

    if not os.path.isdir(clean_path):
        # If it's a file, return parent dir? Or just error.
        # Let's return the parent dir to be helpful, or strictly error.
        # Strict seems better for an API.
        raise HTTPException(status_code=400, detail="Path is not a directory")

    items = []
    try:
        # List dir
        with os.scandir(clean_path) as entries:
            for entry in entries:
                items.append(FileItem(
                    name=entry.name,
                    is_dir=entry.is_dir(),
                    path=entry.path
                ))
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Sort: Directories first, then files. A-Z.
    items.sort(key=lambda x: (not x.is_dir, x.name.lower()))

    return PathListResponse(
        items=items,
        current_path=clean_path,
        parent_path=os.path.dirname(clean_path)
    )
