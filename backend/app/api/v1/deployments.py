from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, Header
from sqlmodel import Session, select
from typing import List
import uuid
import secrets
import hmac
import hashlib
import logging
from datetime import datetime

from app.models.database import engine
from app.models.deployment import DeploymentConfig, DeploymentCreate, DeploymentRead, DeploymentUpdate
from app.api.deps import CurrentUser, get_session, SessionDep
from app.core.config import settings
from app.services.git_service import GitService
from app.services.supervisor_manager import SupervisorManager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=DeploymentRead)
def create_deployment(
    deployment_data: DeploymentCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = None,
):
    # Generate secret
    new_secret = secrets.token_hex(20)  # 40 chars

    db_obj = DeploymentConfig(**deployment_data.model_dump(), secret=new_secret)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    db_obj_read = DeploymentRead.model_validate(db_obj)
    db_obj_read.webhook_url = f"{settings.API_V1_STR}/deployments/webhook/{db_obj.id}"
    return db_obj_read


@router.get("/", response_model=List[DeploymentRead])
def read_deployments(session: Session = Depends(get_session), current_user: CurrentUser = None):
    deployments = session.exec(select(DeploymentConfig)).all()
    results = []
    for d in deployments:
        d_read = DeploymentRead.model_validate(d)
        d_read.webhook_url = f"{settings.API_V1_STR}/deployments/webhook/{d.id}"
        results.append(d_read)
    return results


@router.get("/{deployment_id}", response_model=DeploymentRead)
def get_deployment(
    deployment_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = None,
):
    """Get a single deployment with full details including logs."""
    deployment = session.get(DeploymentConfig, deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    d_read = DeploymentRead.model_validate(deployment)
    d_read.webhook_url = f"{settings.API_V1_STR}/deployments/webhook/{deployment.id}"
    return d_read


@router.put("/{deployment_id}", response_model=DeploymentRead)
def update_deployment(
    deployment_id: uuid.UUID,
    update_data: DeploymentUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = None,
):
    """Update a deployment configuration."""
    deployment = session.get(DeploymentConfig, deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    # Update only provided fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(deployment, key, value)

    session.add(deployment)
    session.commit()
    session.refresh(deployment)

    d_read = DeploymentRead.model_validate(deployment)
    d_read.webhook_url = f"{settings.API_V1_STR}/deployments/webhook/{deployment.id}"
    return d_read


@router.post("/{deployment_id}/trigger")
async def manual_trigger(
    deployment_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: CurrentUser = None,
):
    """Manually trigger a deployment (useful for testing or manual deploys)."""
    deployment = session.get(DeploymentConfig, deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    # Set status to running immediately
    deployment.last_status = "running"
    session.add(deployment)
    session.commit()

    background_tasks.add_task(handle_deploy_background, deployment_id)
    return {"status": "deployment_queued", "message": "Deployment started"}


@router.delete("/{deployment_id}")
def delete_deployment(
    deployment_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = None,
):
    deployment = session.get(DeploymentConfig, deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    session.delete(deployment)
    session.commit()
    return {"ok": True}


# --- Webhook Handler (No Auth Required, verification via Signature) ---


async def handle_deploy_background(deployment_id: uuid.UUID):
    """Background task to handle the actual deployment."""
    with Session(engine) as session:
        deployment = session.get(DeploymentConfig, deployment_id)
        if not deployment:
            logger.error(f"Deployment {deployment_id} not found")
            return

        logger.info(f"Starting deployment: {deployment.name}")

        # Mark as running
        deployment.last_status = "running"
        session.add(deployment)
        session.commit()

        try:
            def update_logs(current_logs):
                # We need to use a new session or refresh carefully to avoid conflicts/detached instances?
                # Actually we are in a session context.
                # But to commit intermediate results, we should careful.
                # Simpler: just set the field and commit.
                deployment.last_logs = current_logs
                session.add(deployment)
                session.commit()
                # session.refresh(deployment) # Optional, but good to keep in sync

            success, logs, commit_hash = GitService.pull_and_deploy(
                deployment.project_path,
                deployment.branch,
                deployment.post_deploy_command,
                deployment.run_as_user,
                log_callback=update_logs
            )

            # Update Status
            deployment.last_status = "success" if success else "failed"
            deployment.last_deployed_at = datetime.utcnow()
            deployment.last_logs = logs
            deployment.last_commit = commit_hash
            deployment.deploy_count = (deployment.deploy_count or 0) + 1
            session.add(deployment)
            session.commit()

            # Restart Supervisor if needed and successful
            if success and deployment.supervisor_process:
                logger.info(f"Restarting supervisor process: {deployment.supervisor_process}")
                SupervisorManager.restart_process(deployment.supervisor_process)

            logger.info(f"Deployment {deployment.name} completed: {'success' if success else 'failed'}")

        except Exception as e:
            logger.exception(f"Deployment {deployment.name} failed with exception")
            deployment.last_status = "failed"
            deployment.last_logs = f"Unexpected error: {str(e)}"
            deployment.last_deployed_at = datetime.utcnow()
            session.add(deployment)
            session.commit()


@router.post("/webhook/{deployment_id}")
async def webhook_trigger(
    deployment_id: uuid.UUID,
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(None),
):
    """GitHub webhook endpoint for automatic deployments."""
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

        # Set status to running immediately
        deployment.last_status = "running"
        session.add(deployment)
        session.commit()

        # Trigger Background Task
        background_tasks.add_task(handle_deploy_background, deployment_id)

        return {"status": "deployment_queued", "message": "Deployment started"}
