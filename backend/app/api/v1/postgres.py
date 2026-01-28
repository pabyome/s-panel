from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from app.api.deps import CurrentUser
from app.services.postgres_manager import PostgresManager
from app.schemas.postgres import (
    PostgresStatus,
    DbCreate,
    UserCreate,
    UserUpdate,
    GrantAccess,
    ExtensionAction,
    RemoteAccess,
)

router = APIRouter()


class BackupRequest(BaseModel):
    format: str = "plain"


@router.get("/status", response_model=PostgresStatus)
def get_status(current_user: CurrentUser):
    return PostgresManager.get_service_status()


@router.post("/install")
def install_postgres(current_user: CurrentUser):
    success, msg = PostgresManager.install_service()
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "installed"}


@router.post("/control/{action}")
def control_service(action: str, current_user: CurrentUser):
    success, msg = PostgresManager.control_service(action)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "ok", "message": msg}


# --- Databases ---


@router.get("/databases")
def list_databases(current_user: CurrentUser):
    return PostgresManager.list_databases()


@router.post("/databases")
def create_database(db: DbCreate, current_user: CurrentUser):
    success, msg = PostgresManager.create_database(db.name, db.owner)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "created"}


@router.delete("/databases/{name}")
def delete_database(name: str, current_user: CurrentUser):
    success, msg = PostgresManager.delete_database(name)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "deleted"}


@router.get("/databases/{name}/extensions")
def list_extensions(name: str, current_user: CurrentUser):
    return PostgresManager.list_extensions(name)


@router.get("/extensions/available")
def list_available_extensions(current_user: CurrentUser):
    """List all extensions available in PostgreSQL (installed packages)."""
    return PostgresManager.list_available_extensions()


@router.get("/extensions/popular")
def list_popular_extensions(current_user: CurrentUser):
    """List popular extensions with availability status and install info."""
    return PostgresManager.get_popular_extensions()


@router.get("/extensions/{ext_name}/info")
def get_extension_info(ext_name: str, current_user: CurrentUser):
    """Get detailed info about an extension including installation instructions."""
    return PostgresManager.get_extension_info(ext_name)


@router.post("/extensions/{ext_name}/install-package")
def install_extension_package(ext_name: str, current_user: CurrentUser):
    """Install the system package required for an extension."""
    success, msg = PostgresManager.install_extension_package(ext_name)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "ok", "message": msg}


@router.post("/databases/{name}/extensions")
def manage_extension(name: str, ext: ExtensionAction, current_user: CurrentUser):
    success, msg = PostgresManager.manage_extension(name, ext.name, ext.action)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "ok"}


# --- Users ---


@router.get("/users")
def list_users(current_user: CurrentUser):
    return PostgresManager.list_users()


@router.post("/users")
def create_user(user: UserCreate, current_user: CurrentUser):
    success, msg = PostgresManager.create_user(user.name, user.password, user.superuser, user.createdb)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "created"}


@router.delete("/users/{name}")
def delete_user(name: str, current_user: CurrentUser):
    success, msg = PostgresManager.delete_user(name)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "deleted"}


@router.put("/users/{name}/password")
def change_password(name: str, data: UserUpdate, current_user: CurrentUser):
    success, msg = PostgresManager.change_password(name, data.password)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "updated"}


@router.post("/grant")
def grant_access(data: GrantAccess, current_user: CurrentUser):
    success, msg = PostgresManager.grant_access(data.database, data.user)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "granted"}


# --- Config ---


@router.post("/remote-access")
def toggle_remote_access(data: RemoteAccess, current_user: CurrentUser):
    success, msg = PostgresManager.toggle_remote_access(data.enable)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "updated", "message": msg}


# --- Maintenance ---


@router.post("/databases/{name}/vacuum")
def vacuum_database(name: str, current_user: CurrentUser):
    success, msg = PostgresManager.vacuum_database(name)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "ok", "message": "Vacuum completed"}


@router.post("/vacuum-all")
def vacuum_all(current_user: CurrentUser):
    success, msg = PostgresManager.vacuum_all()
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "ok", "message": "Vacuum completed for all databases"}


# --- Backup Operations ---


@router.post("/databases/{name}/backup")
def backup_database(name: str, data: BackupRequest, current_user: CurrentUser):
    success, msg = PostgresManager.backup_database(name, data.format)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "ok", "message": msg}


@router.post("/backup-all")
def backup_all(data: BackupRequest, current_user: CurrentUser):
    success, msg = PostgresManager.backup_all(data.format)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "ok", "message": msg}


@router.get("/backups")
def list_backups(current_user: CurrentUser):
    return PostgresManager.list_backups()


# --- Update Check ---


@router.get("/check-update")
def check_update(current_user: CurrentUser):
    return PostgresManager.check_update()
