from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, Header
from sqlmodel import Session, select
from typing import List
import uuid
import secrets
import hmac
import hashlib
from datetime import datetime

from app.models.database import engine
from app.models.deployment import DeploymentConfig, DeploymentCreate, DeploymentRead
from app.api.deps import CurrentUser, get_session
from app.core.config import settings
from app.services.git_service import GitService
from app.services.supervisor_manager import SupervisorManager

router = APIRouter()

@router.post("/", response_model=DeploymentRead)
def create_deployment(deployment_data: DeploymentCreate, session: Session = Depends(get_session), current_user: CurrentUser = None):
    # Generate secret
    new_secret = secrets.token_hex(20) # 40 chars

    db_obj = DeploymentConfig(
        **deployment_data.model_dump(),
        secret=new_secret
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    # Enrich with webhook URL (frontend needs this)
    # Ideally base URL is from config, but for now relative or constructed in frontend.
    # We will just return the object, frontend can construct the URL using the ID.
    db_obj_read = DeploymentRead.model_validate(db_obj)
    db_obj_read.webhook_url = f"{settings.API_V1_STR}/deployments/webhook/{db_obj.id}"
    return db_obj_read

@router.get("/", response_model=List[DeploymentRead])
def read_deployments(session: Session = Depends(get_session), current_user: CurrentUser = None):
    deployments = session.exec(select(DeploymentConfig)).all()
    # Enrich
    results = []
    for d in deployments:
        d_read = DeploymentRead.model_validate(d)
        d_read.webhook_url = f"{settings.API_V1_STR}/deployments/webhook/{d.id}"
        results.append(d_read)
    return results

@router.delete("/{deployment_id}")
def delete_deployment(deployment_id: uuid.UUID, session: Session = Depends(get_session), current_user: CurrentUser = None):
    deployment = session.get(DeploymentConfig, deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    session.delete(deployment)
    session.commit()
    return {"ok": True}

# --- Webhook Handler (No Auth Required, verification via Signature) ---

async def handle_deploy_background(deployment_id: uuid.UUID):
    with Session(engine) as session:
        deployment = session.get(DeploymentConfig, deployment_id)
        if not deployment:
            return

        success, logs = GitService.pull_and_deploy(
            deployment.project_path,
            deployment.branch,
            deployment.post_deploy_command
        )

        # Update Status
        deployment.last_status = "success" if success else "failed"
        deployment.last_deployed_at = datetime.utcnow()
        session.add(deployment)
        session.commit()

        # Restart Supervisor if needed and successful
        if success and deployment.supervisor_process:
            SupervisorManager.restart_process(deployment.supervisor_process)
            # Log restart?

@router.post("/webhook/{deployment_id}")
async def webhook_trigger(
    deployment_id: uuid.UUID,
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(None)
):
    with Session(engine) as session:
        deployment = session.get(DeploymentConfig, deployment_id)
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment config not found")

        if not x_hub_signature_256:
             raise HTTPException(status_code=401, detail="Missing signature header")

        # Verify Signature
        body = await request.body()
        secret_bytes = deployment.secret.encode()
        expected_signature = "sha256=" + hmac.new(secret_bytes, body, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected_signature, x_hub_signature_256):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Trigger Background Task
        background_tasks.add_task(handle_deploy_background, deployment_id)

        return {"status": "deployment_queued"}
