from pydantic import BaseModel
from typing import Optional, List

class MysqlStatus(BaseModel):
    installed: bool
    running: bool
    version: Optional[str]
    uptime: Optional[str]
    data_dir: Optional[str]
    remote_access: bool

class DbCreate(BaseModel):
    name: str
    # MySQL databases don't have an owner at creation time like Postgres

class UserCreate(BaseModel):
    name: str
    password: str
    # Simplified permissions for the UI
    grant_all: bool = False # Grants ALL PRIVILEGES ON *.* (Superuser-like)

class UserUpdate(BaseModel):
    password: Optional[str] = None

class GrantAccess(BaseModel):
    database: str
    user: str

class RemoteAccess(BaseModel):
    enable: bool
