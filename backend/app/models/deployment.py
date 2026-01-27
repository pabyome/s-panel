from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class DeploymentConfig(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    project_path: str
    branch: str = Field(default="main")
    secret: str  # HMAC secret
    supervisor_process: Optional[str] = None  # Name of process to restart
    post_deploy_command: Optional[str] = None  # Shell command to run after pull
    last_deployed_at: Optional[datetime] = None
    last_status: Optional[str] = None  # success, failed, running
    last_commit: Optional[str] = None  # Last deployed commit hash
    last_logs: Optional[str] = None  # Deployment logs
    deploy_count: int = Field(default=0)  # Total deployment count
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DeploymentCreate(SQLModel):
    name: str
    project_path: str
    branch: str = "main"
    supervisor_process: Optional[str] = None
    post_deploy_command: Optional[str] = None


class DeploymentUpdate(SQLModel):
    """Schema for updating a deployment - all fields optional"""

    name: Optional[str] = None
    project_path: Optional[str] = None
    branch: Optional[str] = None
    supervisor_process: Optional[str] = None
    post_deploy_command: Optional[str] = None


class DeploymentRead(SQLModel):
    """Schema for reading a deployment - excludes secret for security"""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    project_path: str
    branch: str
    supervisor_process: Optional[str] = None
    post_deploy_command: Optional[str] = None
    last_deployed_at: Optional[datetime] = None
    last_status: Optional[str] = None
    last_commit: Optional[str] = None
    last_logs: Optional[str] = None
    deploy_count: int = 0
    created_at: Optional[datetime] = None
    secret: str  # Include for webhook setup
    webhook_url: str = ""  # Calculated field
