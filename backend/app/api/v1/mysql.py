from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from app.api.deps import CurrentUser, CurrentAdmin
from app.services.mysql_manager import MysqlManager
from app.schemas.mysql import (
    MysqlStatus,
    DbCreate,
    UserCreate,
    UserUpdate,
    GrantAccess,
    RemoteAccess,
)

router = APIRouter()


class BackupRequest(BaseModel):
    format: str = "sql" # default to sql


@router.get("/status", response_model=MysqlStatus)
def get_status(current_user: CurrentUser):
    return MysqlManager.get_service_status()


@router.post("/install")
def install_mysql(current_user: CurrentUser):
    success, msg = MysqlManager.install_service()
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "installed"}


@router.post("/control/{action}")
def control_service(action: str, current_user: CurrentUser):
    success, msg = MysqlManager.control_service(action)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "ok", "message": msg}


# --- Databases ---


@router.get("/databases")
def list_databases(current_user: CurrentUser):
    return MysqlManager.list_databases()


@router.post("/databases")
def create_database(db: DbCreate, current_user: CurrentUser):
    # MySQL doesn't use owner at creation
    success, msg = MysqlManager.create_database(db.name)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "created"}


@router.delete("/databases/{name}")
def delete_database(name: str, current_user: CurrentUser):
    success, msg = MysqlManager.delete_database(name)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "deleted"}


# --- Users ---


@router.get("/users")
def list_users(current_user: CurrentAdmin):
    return MysqlManager.list_users()


@router.post("/users")
def create_user(user: UserCreate, current_user: CurrentAdmin):
    success, msg = MysqlManager.create_user(user.name, user.password, user.grant_all)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "created"}


@router.delete("/users/{name}")
def delete_user(name: str, current_user: CurrentAdmin):
    # name is expected to be user@host
    success, msg = MysqlManager.delete_user(name)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "deleted"}


@router.put("/users/{name}/password")
def change_password(name: str, data: UserUpdate, current_user: CurrentAdmin):
    # name is expected to be user@host
    success, msg = MysqlManager.change_password(name, data.password)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "updated"}


@router.post("/grant")
def grant_access(data: GrantAccess, current_user: CurrentAdmin):
    # data.user is expected to be user@host
    success, msg = MysqlManager.grant_access(data.database, data.user)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "granted"}


# --- Config ---


@router.post("/remote-access")
def toggle_remote_access(data: RemoteAccess, current_user: CurrentUser):
    success, msg = MysqlManager.toggle_remote_access(data.enable)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "updated", "message": msg}


# --- Backup Operations ---


@router.post("/databases/{name}/backup")
def backup_database(name: str, data: BackupRequest, current_user: CurrentUser):
    # data.format is ignored for now, always SQL
    success, msg = MysqlManager.backup_database(name)
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "ok", "message": msg}


@router.post("/backup-all")
def backup_all(data: BackupRequest, current_user: CurrentUser):
    success, msg = MysqlManager.backup_all()
    if not success:
        raise HTTPException(status_code=500, detail=msg)
    return {"status": "ok", "message": msg}


@router.get("/backups")
def list_backups(current_user: CurrentUser):
    return MysqlManager.list_backups()


# --- Update Check ---


@router.get("/check-update")
def check_update(current_user: CurrentUser):
    return MysqlManager.check_update()
