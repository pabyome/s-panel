import uuid
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class DeploymentHistory(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    deployment_id: uuid.UUID = Field(foreign_key="deploymentconfig.id", index=True)
    commit_hash: Optional[str] = None
    image_tag: Optional[str] = None
    status: str # success, failed, rollback
    logs: Optional[str] = None
    deployed_at: datetime = Field(default_factory=datetime.utcnow)
