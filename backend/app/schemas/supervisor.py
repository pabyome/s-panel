from pydantic import BaseModel
from typing import Optional


class SupervisorProcess(BaseModel):
    name: str
    group: str
    statename: str
    state: int
    description: str
    start: Optional[int] = 0
    stop: Optional[int] = 0
    pid: Optional[int] = 0
    uptime_seconds: Optional[int] = 0


class SupervisorConfigUpdate(BaseModel):
    content: str


class SupervisorStatus(BaseModel):
    running: bool
    state: str
    version: Optional[str] = None
    error: Optional[str] = None


class SupervisorConfigCreate(BaseModel):
    name: str
    command: str
    directory: Optional[str] = None
    user: Optional[str] = "root"
    autostart: bool = True
    autorestart: bool = True
    numprocs: int = 1

