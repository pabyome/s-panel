import shutil
import os
import datetime
import glob
from typing import List, Optional
from pydantic import BaseModel

class BackupInfo(BaseModel):
    filename: str
    size_bytes: int
    created_at: datetime.datetime

class BackupService:
    BACKUP_DIR = "backups"
    DB_FILE = "spanel.db"

    @classmethod
    def _ensure_backup_dir(cls):
        if not os.path.exists(cls.BACKUP_DIR):
            os.makedirs(cls.BACKUP_DIR)

    @classmethod
    def create_backup(cls) -> Optional[BackupInfo]:
        cls._ensure_backup_dir()

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.spanel.db"
        destination = os.path.join(cls.BACKUP_DIR, backup_filename)

        if not os.path.exists(cls.DB_FILE):
             print(f"Database file {cls.DB_FILE} not found.")
             return None

        try:
            # Simple file copy for SQLite (WAL mode handles concurrency reasonably well for backup)
            # For strict integrity, using the SQLite API to backup is better, but copy is okay for MVP
            shutil.copy2(cls.DB_FILE, destination)

            return BackupInfo(
                filename=backup_filename,
                size_bytes=os.path.getsize(destination),
                created_at=datetime.datetime.now()
            )
        except Exception as e:
            print(f"Backup failed: {e}")
            return None

    @classmethod
    def list_backups(cls) -> List[BackupInfo]:
        cls._ensure_backup_dir()
        files = glob.glob(os.path.join(cls.BACKUP_DIR, "backup_*.spanel.db"))
        backups = []

        for f in files:
            try:
                stat = os.stat(f)
                filename = os.path.basename(f)
                # Parse timestamp from filename backup_YYYYMMDD_HHMMSS.spanel.db
                # fallback to file mtime if parse fails
                created_at = datetime.datetime.fromtimestamp(stat.st_mtime)

                backups.append(BackupInfo(
                    filename=filename,
                    size_bytes=stat.st_size,
                    created_at=created_at
                ))
            except Exception:
                continue

        # Sort by newest first
        backups.sort(key=lambda x: x.created_at, reverse=True)
        return backups

    @classmethod
    def restore_backup(cls, filename: str) -> bool:
        cls._ensure_backup_dir()
        source = os.path.join(cls.BACKUP_DIR, filename)

        if not os.path.exists(source):
            return False

        try:
            # Create a localized backup of current state just in case
            cls.create_backup()

            shutil.copy2(source, cls.DB_FILE)
            return True
        except Exception as e:
            print(f"Restore failed: {e}")
            return False

    @classmethod
    def delete_backup(cls, filename: str) -> bool:
        cls._ensure_backup_dir()
        target = os.path.join(cls.BACKUP_DIR, filename)

        # Simple path safety check (prevent ../ traversal)
        if os.path.dirname(os.path.abspath(target)) != os.path.abspath(cls.BACKUP_DIR):
            return False

        if os.path.exists(target):
            os.remove(target)
            return True
        return False
