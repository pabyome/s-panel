from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Website(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    domain: str = Field(index=True, unique=True)
    port: int
    project_path: str
    ssl_enabled: bool = False
    status: str = "stopped" # running, stopped, error
    created_at: datetime = Field(default_factory=datetime.utcnow)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
