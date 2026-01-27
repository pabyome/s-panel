from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Website(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    domain: str = Field(index=True, unique=True)
    port: int
    is_ssl: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
