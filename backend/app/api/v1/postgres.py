from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.api.deps import CurrentUser
from app.services.postgres_manager import PostgresManager
from app.schemas.postgres import (
    PostgresStatus, DbCreate, UserCreate, UserUpdate,
    GrantAccess, ExtensionAction, RemoteAccess
)

router = APIRouter()

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
