from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class DeploymentConfig(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    project_path: str
    branch: str = Field(default="main")
    secret: str # HMAC secret
    supervisor_process: Optional[str] = None # Name of process to restart
    post_deploy_command: Optional[str] = None # Shell command to run after pull
    last_deployed_at: Optional[datetime] = None
    last_status: Optional[str] = None # success, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DeploymentCreate(SQLModel):
    name: str
    project_path: str
    branch: str = "main"
    supervisor_process: Optional[str] = None
    post_deploy_command: Optional[str] = None

class DeploymentRead(DeploymentConfig):
    webhook_url: str # Calculated field
