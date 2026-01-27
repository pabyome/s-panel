from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api.deps import CurrentUser
from app.services.backup_service import BackupService, BackupInfo

router = APIRouter()

@router.get("/", response_model=List[BackupInfo])
def list_backups(current_user: CurrentUser):
    return BackupService.list_backups()

@router.post("/", response_model=BackupInfo)
def create_backup(current_user: CurrentUser):
    backup = BackupService.create_backup()
    if not backup:
        raise HTTPException(status_code=500, detail="Backup creation failed")
    return backup

@router.post("/{filename}/restore")
def restore_backup(filename: str, current_user: CurrentUser):
    success = BackupService.restore_backup(filename)
    if not success:
        raise HTTPException(status_code=400, detail="Restore failed or file not found")
    return {"ok": True, "message": "Database restored. Service restart recommended."}

@router.delete("/{filename}")
def delete_backup(filename: str, current_user: CurrentUser):
    success = BackupService.delete_backup(filename)
    if not success:
        raise HTTPException(status_code=404, detail="Backup not found")
    return {"ok": True}
