import uuid
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class DeploymentConfig(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    project_path: str
    branch: str = Field(default="main")
    secret: str  # HMAC secret
    supervisor_process: Optional[str] = None  # Name of process to restart
    post_deploy_command: Optional[str] = None  # Shell command to run after pull
    run_as_user: Optional[str] = Field(default="root")  # User to run build command
    notification_emails: Optional[str] = None  # Comma-separated emails for notifications

    # Swarm Configuration
    deployment_mode: str = Field(default="supervisor") # supervisor, docker-swarm
    swarm_replicas: int = Field(default=2)
    current_port: int = Field(default=3000) # Internal app port
    dockerfile_path: Optional[str] = Field(default="Dockerfile") # Path to Dockerfile relative to project_path

    # Laravel Configuration
    is_laravel: bool = Field(default=False)
    laravel_worker_replicas: int = Field(default=1)
    laravel_scheduler_enabled: bool = Field(default=False)
    laravel_horizon_enabled: bool = Field(default=False)

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
    run_as_user: Optional[str] = "root"
    notification_emails: Optional[str] = None
    deployment_mode: str = "supervisor"
    swarm_replicas: int = 2
    current_port: int = 3000
    dockerfile_path: Optional[str] = "Dockerfile"
    is_laravel: bool = False
    laravel_worker_replicas: int = 1
    laravel_scheduler_enabled: bool = False
    laravel_horizon_enabled: bool = False

    # Automated Website Creation
    website_domain: Optional[str] = None
    website_ssl: bool = False


class DeploymentUpdate(SQLModel):
    """Schema for updating a deployment - all fields optional"""

    name: Optional[str] = None
    project_path: Optional[str] = None
    branch: Optional[str] = None
    supervisor_process: Optional[str] = None
    post_deploy_command: Optional[str] = None
    run_as_user: Optional[str] = None
    notification_emails: Optional[str] = None
    deployment_mode: Optional[str] = None
    swarm_replicas: Optional[int] = None
    current_port: Optional[int] = None
    dockerfile_path: Optional[str] = None
    is_laravel: Optional[bool] = None
    laravel_worker_replicas: Optional[int] = None
    laravel_scheduler_enabled: Optional[bool] = None
    laravel_horizon_enabled: Optional[bool] = None

    # Website Linking
    website_domain: Optional[str] = None
    website_ssl: Optional[bool] = None


class DeploymentRead(SQLModel):
    """Schema for reading a deployment"""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    project_path: str
    branch: str
    supervisor_process: Optional[str] = None
    post_deploy_command: Optional[str] = None
    run_as_user: Optional[str] = "root"  # User to run build command
    notification_emails: Optional[str] = None  # Comma-separated emails for notifications
    deployment_mode: str = "supervisor"
    swarm_replicas: int = 2
    current_port: int = 3000
    dockerfile_path: Optional[str] = "Dockerfile"
    is_laravel: bool = False
    laravel_worker_replicas: int = 1
    laravel_scheduler_enabled: bool = False
    laravel_horizon_enabled: bool = False
    last_deployed_at: Optional[datetime] = None
    last_status: Optional[str] = None
    last_commit: Optional[str] = None
    last_logs: Optional[str] = None
    deploy_count: int = 0
    created_at: Optional[datetime] = None
    # secret: str  # Excluded from default read for security
    webhook_url: str = ""  # Calculated field

    # Website Linking
    website_domain: Optional[str] = None
    website_ssl: bool = False
