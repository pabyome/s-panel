from pydantic import BaseModel
from typing import Optional

class CronJob(BaseModel):
    id: Optional[str] = None
    command: str
    schedule: str
    comment: Optional[str] = None
    enabled: bool = True
    user: Optional[str] = "root"

class CronJobCreate(BaseModel):
    command: str
    schedule: str # "* * * * *"
    comment: Optional[str] = None
    user: Optional[str] = "root"

class CronJobUpdate(BaseModel):
    command: Optional[str] = None
    schedule: Optional[str] = None
