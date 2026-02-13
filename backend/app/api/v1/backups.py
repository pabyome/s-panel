from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
import re
import subprocess
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


@router.get("/database/stream")
def stream_database_dump(database: str, current_user: CurrentUser):
    """
    Stream a database dump (mysqldump) directly to the client.
    """
    # Security check: validate database name (alphanumeric + underscores)
    if not re.match(r"^[a-zA-Z0-9_]+$", database):
         raise HTTPException(status_code=400, detail="Invalid database name")

    # Use sudo mysqldump via socket auth
    cmd = ["sudo", "mysqldump", database]

    def iterfile():
        try:
            # Popen with stdout pipe
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
                while True:
                    # Read 8KB chunks
                    chunk = proc.stdout.read(8192)
                    if not chunk:
                        break
                    yield chunk

                # Check for errors after streaming
                # If returncode is non-zero, the stream might have ended abruptly
                # We can't easily signal HTTP error mid-stream, but we can log.
                if proc.returncode and proc.returncode != 0:
                    print(f"Backup stream warning: mysqldump exited with {proc.returncode}")
        except Exception as e:
            print(f"Backup stream error: {e}")

    return StreamingResponse(
        iterfile(),
        media_type="application/x-sql",
        headers={"Content-Disposition": f"attachment; filename={database}.sql"}
    )
