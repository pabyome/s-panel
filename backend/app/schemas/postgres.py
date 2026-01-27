from pydantic import BaseModel
from typing import Optional, List

class PostgresStatus(BaseModel):
    installed: bool
    running: bool
    version: Optional[str]
    uptime: Optional[str]
    data_dir: Optional[str]
    remote_access: bool

class DbCreate(BaseModel):
    name: str
    owner: str = "postgres"

class UserCreate(BaseModel):
    name: str
    password: str
    superuser: bool = False
    createdb: bool = False

class UserUpdate(BaseModel):
    password: Optional[str] = None

class GrantAccess(BaseModel):
    database: str
    user: str

class ExtensionAction(BaseModel):
    name: str
    action: str # create or drop

class RemoteAccess(BaseModel):
    enable: bool
