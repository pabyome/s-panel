from pydantic import BaseModel
from typing import Optional

class CronJob(BaseModel):
    id: Optional[str] = None
    command: str
    schedule: str
    comment: Optional[str] = None
    enabled: bool = True

class CronJobCreate(BaseModel):
    command: str
    schedule: str # "* * * * *"
    comment: Optional[str] = None

class CronJobUpdate(BaseModel):
    command: Optional[str] = None
    schedule: Optional[str] = None
