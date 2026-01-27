from fastapi import APIRouter, HTTPException, Query
import os
from typing import List
from app.api.deps import CurrentUser
from app.schemas.system import FileItem, PathListResponse
from typing import Optional
from pydantic import BaseModel
import subprocess

class UpdateInfo(BaseModel):
    updates_available: bool
    current_commit: str
    latest_commit: str
    message: str

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

@router.get("/update/check", response_model=UpdateInfo)
def check_for_updates(current_user: CurrentUser):
    try:
        # Fetch remote
        subprocess.run(["git", "fetch"], check=True, timeout=30)

        # Get current hash
        current = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()

        # Get remote hash
        latest = subprocess.check_output(["git", "rev-parse", "--short", "origin/main"], text=True).strip()

        available = current != latest

        return UpdateInfo(
            updates_available=available,
            current_commit=current,
            latest_commit=latest,
            message="Update available" if available else "System is up to date"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git check failed: {str(e)}")

@router.post("/update/apply")
def apply_update(current_user: CurrentUser):
    # This triggers the update script. usage: nohup ./update.sh &
    # We run it in background because it will kill the API.

    # Resolve path relative to this file: .../backend/app/api/v1/system.py
    # Access root: ../../../../update.sh
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    script_path = os.path.join(base_dir, "update.sh")

    # Fallback to CWD check if the above logic fails (e.g. strange install)
    if not os.path.exists(script_path):
        script_path = os.path.abspath("update.sh")

    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail=f"Update script not found at {script_path}")

    try:
        # Run in independent process
        subprocess.Popen(["/bin/bash", script_path], start_new_session=True)
        return {"status": "updating", "message": "Update started in background. Service will restart shortly."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start update: {str(e)}")
