from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, Header, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from sqlmodel import Session, select, SQLModel
from typing import List, Dict, Set
import uuid
import secrets
import hmac
import hashlib
import logging
import asyncio
from datetime import datetime

from app.models.database import engine
from app.models.deployment import DeploymentConfig, DeploymentCreate, DeploymentRead, DeploymentUpdate
from app.api.deps import CurrentUser, get_session, SessionDep
from app.core.config import settings
from app.services.git_service import GitService
from app.services.supervisor_manager import SupervisorManager
from app.services.email_service import EmailService
import jwt
from pydantic import ValidationError
from fastapi import Query
from app.core.security import ALGORITHM, SECRET_KEY
from app.schemas.token import TokenPayload

router = APIRouter()
logger = logging.getLogger(__name__)

# WebSocket connections for live deployment logs
deployment_connections: Dict[str, Set[WebSocket]] = {}


class DeploymentWebhookInfo(SQLModel):
    webhook_url: str
    secret: str

@router.get("/{deployment_id}/webhook-info", response_model=DeploymentWebhookInfo)
def get_deployment_webhook_info(deployment_id: uuid.UUID, session: SessionDep, current_user: CurrentUser):
    """Get webhook configuration details (URL and Secret)"""
    deployment = session.get(DeploymentConfig, deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    # Calculate webhook URL (or use field if persisted, but checking model, it's calculated in DeploymentRead)
    # DeploymentRead calculates it. We need to replicate or use DeploymentRead logic.
    # DeploymentRead uses: webhook_url: str = "" # Calculated field
    # In API logic usually it's injected.
    # Let's verify how DeploymentRead gets webhook_url.
    # It seems to be done in `read_deployments`? No, SQLModel matching.
    # Actually, `DeploymentRead` has `webhook_url` but `DeploymentConfig` doesn't?
    # DeploymentConfig table definition in tool 263 doesn't have webhook_url column.
    # So `read_deployments` probably computes it?
    # Let's check `read_deployments` impl.
    # For now, I'll calculate it: f"/api/v1/deployments/webhook/{deployment_id}"

    webhook_url = f"/api/v1/deployments/webhook/{deployment_id}"
    return DeploymentWebhookInfo(webhook_url=webhook_url, secret=deployment.secret)

@router.websocket("/ws/{deployment_id}")
async def deployment_logs_ws(
    websocket: WebSocket,
    deployment_id: str,
    token: str = Query(...)
):
    """WebSocket endpoint for streaming deployment logs in real-time"""
    # Authenticate via Token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except (jwt.PyJWTError, ValidationError):
        await websocket.close(code=1008, reason="Invalid authentication token")
        return

    await websocket.accept()

    # Add connection to the set for this deployment
    if deployment_id not in deployment_connections:
        deployment_connections[deployment_id] = set()
    deployment_connections[deployment_id].add(websocket)

    logger.info(f"WebSocket connected for deployment {deployment_id}")

    try:
        # Send current logs immediately
        with Session(engine) as session:
            deployment = session.get(DeploymentConfig, uuid.UUID(deployment_id))
            if deployment:
                await websocket.send_json(
                    {"type": "initial", "logs": deployment.last_logs or "", "status": deployment.last_status}
                )

        # Keep connection open and wait for updates
        while True:
            try:
                # Ping/pong to keep connection alive
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({"type": "heartbeat"})
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for deployment {deployment_id}")
    except Exception as e:
        logger.exception(f"WebSocket error for deployment {deployment_id}: {e}")
    finally:
        # Remove connection from set
        if deployment_id in deployment_connections:
            deployment_connections[deployment_id].discard(websocket)
            if not deployment_connections[deployment_id]:
                del deployment_connections[deployment_id]


async def broadcast_deployment_update(deployment_id: str, logs: str, status: str):
    """Broadcast log updates to all connected WebSocket clients for a deployment"""
    if deployment_id not in deployment_connections:
        return

    dead_connections = set()
    for ws in deployment_connections[deployment_id]:
        try:
            if ws.client_state == WebSocketState.CONNECTED:
                await ws.send_json({"type": "update", "logs": logs, "status": status})
        except Exception:
            dead_connections.add(ws)

    # Clean up dead connections
    for ws in dead_connections:
        deployment_connections[deployment_id].discard(ws)


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


@router.post("/{deployment_id}/logs/clear")
def clear_deployment_logs(
    deployment_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = None,
):
    """Clear the logs for a deployment"""
    deployment = session.get(DeploymentConfig, deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    deployment.last_logs = None
    session.add(deployment)
    session.commit()
    return {"status": "cleared"}


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
    deployment_id_str = str(deployment_id)

    with Session(engine) as session:
        deployment = session.get(DeploymentConfig, deployment_id)
        if not deployment:
            logger.error(f"Deployment {deployment_id} not found")
            return

        logger.info(f"Starting deployment: {deployment.name}")

        # Mark as running
        deployment.last_status = "running"
        deployment.last_logs = "Starting deployment...\n"
        session.add(deployment)
        session.commit()

        # Broadcast initial status
        try:
            asyncio.create_task(broadcast_deployment_update(deployment_id_str, deployment.last_logs, "running"))
        except:
            pass

        try:
            loop = asyncio.get_running_loop()

            async def update_logs(current_logs):
                # Update database
                deployment.last_logs = current_logs
                session.add(deployment)
                session.commit()

                # Broadcast to WebSocket clients
                try:
                    await broadcast_deployment_update(deployment_id_str, current_logs, "running")
                except Exception as e:
                    logger.warning(f"Failed to broadcast log update: {e}")

            # Wrap sync callback for GitService
            def sync_update_logs(current_logs):
                try:
                    asyncio.run_coroutine_threadsafe(update_logs(current_logs), loop)
                except Exception:
                    pass

            if deployment.deployment_mode == "docker-swarm":
                success, logs, commit_hash = await loop.run_in_executor(
                    None,
                    lambda: GitService.deploy_swarm(
                        project_path=deployment.project_path,
                        branch=deployment.branch,
                        app_name=deployment.name,
                        swarm_replicas=deployment.swarm_replicas,
                        current_port=deployment.current_port,
                        dockerfile_path=deployment.dockerfile_path or "Dockerfile",
                        run_as_user=deployment.run_as_user,
                        log_callback=sync_update_logs,
                    )
                )
            else:
                # Default / Supervisor Mode
                success, logs, commit_hash = await loop.run_in_executor(
                    None,
                    lambda: GitService.pull_and_deploy(
                        deployment.project_path,
                        deployment.branch,
                        deployment.post_deploy_command,
                        deployment.run_as_user,
                        log_callback=sync_update_logs,
                    )
                )

            # Update Status
            final_status = "success" if success else "failed"
            deployment.last_status = final_status
            deployment.last_deployed_at = datetime.utcnow()
            deployment.last_logs = logs
            deployment.last_commit = commit_hash
            deployment.deploy_count = (deployment.deploy_count or 0) + 1
            session.add(deployment)
            session.commit()

            # Broadcast final status
            try:
                asyncio.create_task(broadcast_deployment_update(deployment_id_str, logs, final_status))
            except:
                pass

            # Restart Supervisor if needed and successful
            # Restart Supervisor if needed and successful (Only for supervisor mode)
            if success and deployment.deployment_mode == "supervisor" and deployment.supervisor_process:
                logger.info(f"Restarting supervisor process: {deployment.supervisor_process}")
                SupervisorManager.restart_process(deployment.supervisor_process)

            logger.info(f"Deployment {deployment.name} completed: {'success' if success else 'failed'}")

            # Send Notification
            from app.services.email_service import EmailService

            subject = f"Deployment {deployment.name}: {'Successful' if success else 'Failed'}"
            body = f"""
Deployment for {deployment.name} has completed.
Status: {'Success' if success else 'Failed'}
Branch: {deployment.branch}
Commit: {commit_hash}
Time: {datetime.utcnow()}

Logs snippet:
{logs[-500:] if logs else 'No logs'}
            """
            # Parse notification emails for this deployment
            recipients = []
            if deployment.notification_emails:
                recipients.extend([e.strip() for e in deployment.notification_emails.split(",") if e.strip()])

            # Add global alert recipient if enabled
            alert_settings = EmailService.get_deployment_alert_settings()
            if alert_settings["enabled"] and alert_settings["alert_email"]:
                recipients.append(alert_settings["alert_email"])

            # Deduplicate
            recipients = list(set(recipients))

            custom_success, custom_msg = EmailService.send_email(subject, body, recipients)
            if not custom_success:
                logger.warning(f"Failed to send deployment notification: {custom_msg}")

        except Exception as e:
            logger.exception(f"Deployment {deployment.name} failed with exception")
            error_logs = f"Unexpected error: {str(e)}"
            deployment.last_status = "failed"
            deployment.last_logs = error_logs
            deployment.last_deployed_at = datetime.utcnow()
            session.add(deployment)
            session.commit()

            # Broadcast error
            try:
                asyncio.create_task(broadcast_deployment_update(deployment_id_str, error_logs, "failed"))
            except:
                pass

            # Send Notification (Exception case)
            from app.services.email_service import EmailService

            recipients = []
            if deployment.notification_emails:
                recipients.extend([e.strip() for e in deployment.notification_emails.split(",") if e.strip()])

            # Add global alert recipient if enabled
            alert_settings = EmailService.get_deployment_alert_settings()
            if alert_settings["enabled"] and alert_settings["alert_email"]:
                recipients.append(alert_settings["alert_email"])

            # Deduplicate
            recipients = list(set(recipients))

            err_success, err_msg = EmailService.send_email(
                f"Deployment {deployment.name}: Failed (Exception)",
                f"Deployment failed with error: {str(e)}",
                recipients,
            )
            if not err_success:
                logger.warning(f"Failed to send failure notification: {err_msg}")


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

        # Check GitHub event type
        event_type = request.headers.get("X-GitHub-Event", "push")

        if event_type == "ping":
            return {"status": "ok", "message": "Webhook configured successfully"}

        if event_type != "push":
            return {"status": "ignored", "message": f"Event type '{event_type}' not supported"}

        # Parse body to check branch
        try:
            payload = await request.json()
        except:
            raise HTTPException(status_code=400, detail="Invalid JSON body")

        ref = payload.get("ref")
        # specific check for branch
        if deployment.branch:
            expected_ref = f"refs/heads/{deployment.branch}"
            if ref != expected_ref:
                logger.info(f"Ignored webhook for {deployment.name}: pushed to {ref}, expected {expected_ref}")
                return {"status": "ignored", "message": f"Push to {ref} ignored. Configured for {deployment.branch}"}

        # Set status to running immediately
        deployment.last_status = "running"
        session.add(deployment)
        session.commit()

        # Trigger Background Task
        background_tasks.add_task(handle_deploy_background, deployment_id)

        return {"status": "deployment_queued", "message": "Deployment started"}
