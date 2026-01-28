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


class UserItem(BaseModel):
    username: str
    uid: int
    gid: int
    home: str
    shell: str


router = APIRouter()


@router.get("/path/list", response_model=PathListResponse)
def list_directory(
    path: str = Query(default="/", description="Absolute path to list"), current_user: CurrentUser = None
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
        raise HTTPException(
            status_code=403, detail=f"Path not allowed in Safe Mode. Allowed roots: {', '.join(ALLOWED_ROOTS)}"
        )

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
                items.append(FileItem(name=entry.name, is_dir=entry.is_dir(), path=entry.path))
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Sort: Directories first, then files. A-Z.
    items.sort(key=lambda x: (not x.is_dir, x.name.lower()))

    return PathListResponse(items=items, current_path=clean_path, parent_path=os.path.dirname(clean_path))


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
            message="Update available" if available else "System is up to date",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git check failed: {str(e)}")


@router.post("/update/apply")
def apply_update(current_user: CurrentUser):
    # This triggers the update script. usage: nohup ./update.sh &
    # We run it in background because it will kill the API.

    # Resolve path relative to this file: .../backend/app/api/v1/system.py
    # Access root: ../../../../update.sh
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    )
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


@router.get("/users", response_model=List[UserItem])
def list_system_users(current_user: CurrentUser):
    users = []

    # Common service users we want to show
    # 'www' is our custom one, 'www-data' is standard, 'nginx', 'root'
    WHITELIST = ["root", "www", "www-data", "nginx", "nobody"]

    try:
        import pwd

        for p in pwd.getpwall():
            # Filter logic:
            # 1. UID >= 1000 (normal users)
            # 2. OR username in WHITELIST
            if p.pw_uid >= 1000 or p.pw_name in WHITELIST:
                users.append(UserItem(username=p.pw_name, uid=p.pw_uid, gid=p.pw_gid, home=p.pw_dir, shell=p.pw_shell))

        # Sort by name
        users.sort(key=lambda x: x.username)
        return users

    except Exception as e:
        # Fallback for non-Unix systems (dev on windows?)
        # But pwd is unix only.
        raise HTTPException(status_code=500, detail=f"Failed to list users: {str(e)}")


from app.models.settings import SystemSetting
from app.api.deps import SessionDep
import json
from pydantic import BaseModel, EmailStr


class SMTPSettings(BaseModel):
    host: str
    port: int
    user: str
    password: str
    from_email: EmailStr
    admin_emails: List[EmailStr]


@router.get("/settings/smtp", response_model=SMTPSettings)
def get_smtp_settings(session: SessionDep, current_user: CurrentUser):
    setting = session.get(SystemSetting, "smtp_config")
    if not setting:
        return SMTPSettings(host="", port=587, user="", password="", from_email="noreply@example.com", admin_emails=[])
    return SMTPSettings(**json.loads(setting.value))


@router.post("/settings/smtp")
def save_smtp_settings(settings: SMTPSettings, session: SessionDep, current_user: CurrentUser):
    setting = session.get(SystemSetting, "smtp_config")
    if not setting:
        setting = SystemSetting(key="smtp_config", value="")

    setting.value = settings.json()
    session.add(setting)
    session.commit()
    return {"ok": True}


# --- Port Utilities ---

from app.services.system_monitor import SystemMonitor


@router.get("/ports/check/{port}")
def check_port(port: int, current_user: CurrentUser):
    """Check if a specific port is available or in use."""
    if port < 1 or port > 65535:
        raise HTTPException(status_code=400, detail="Invalid port number. Must be between 1 and 65535.")

    info = SystemMonitor.get_port_info(port)
    return info


@router.get("/ports/listening")
def get_listening_ports(current_user: CurrentUser):
    """Get all listening ports on the system."""
    return SystemMonitor.get_listening_ports()


@router.get("/ports/find-free")
def find_free_port(
    start: int = Query(default=3000, description="Start of port range"),
    end: int = Query(default=9000, description="End of port range"),
    current_user: CurrentUser = None,
):
    """Find the next available port in a range."""
    if start < 1 or end > 65535 or start > end:
        raise HTTPException(status_code=400, detail="Invalid port range.")

    port = SystemMonitor.find_free_port(start, end)
    if port is None:
        raise HTTPException(status_code=404, detail=f"No free port found in range {start}-{end}")

    return {"port": port}


@router.get("/ports/process/{pid}")
def get_process_ports(pid: int, current_user: CurrentUser):
    """Get all ports that a specific process is listening on."""
    ports = SystemMonitor.get_process_ports(pid)
    return {"pid": pid, "ports": ports}
