from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class Website(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    domain: str = Field(index=True, unique=True)
    port: int
    project_path: str
    ssl_enabled: bool = False
    is_static: bool = False  # True for static HTML sites, False for proxied apps
    is_laravel: bool = Field(default=False)
    deployment_id: Optional[uuid.UUID] = Field(default=None, foreign_key="deploymentconfig.id")
    status: str = "stopped"  # running, stopped, error
    created_at: datetime = Field(default_factory=datetime.utcnow)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
