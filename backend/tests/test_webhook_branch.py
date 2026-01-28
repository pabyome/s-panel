from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models.deployment import DeploymentConfig
from app.models.database import engine
import hmac
import hashlib
import json
import uuid
from unittest.mock import patch

def create_deployment(session, branch="main", secret="test_secret"):
    deployment = DeploymentConfig(
        name="Test Deploy",
        repo_url="https://github.com/user/repo",
        branch=branch,
        secret=secret,
        project_path="/tmp/test",
        # other required fields?
        is_active=True
    )
    session.add(deployment)
    session.commit()
    session.refresh(deployment)
    return deployment

def generate_signature(secret: str, payload: bytes) -> str:
    return "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

def test_webhook_ping(client, session):
    d = create_deployment(session)
    deployment_id = d.id
    secret = d.secret

    payload = {"zen": "Keep it logically awesome."}
    body = json.dumps(payload).encode()
    signature = generate_signature(secret, body)

    headers = {
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "ping"
    }

    with patch("app.api.v1.deployments.engine", session.bind):
        response = client.post(f"/api/v1/deployments/webhook/{deployment_id}", content=body, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Webhook configured successfully"

def test_webhook_push_match(client, session):
    d = create_deployment(session, branch="main")
    deployment_id = d.id
    secret = d.secret

    payload = {"ref": "refs/heads/main"}
    body = json.dumps(payload).encode()
    signature = generate_signature(secret, body)

    headers = {
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "push"
    }

    with patch("app.api.v1.deployments.engine", session.bind):
        with patch("app.api.v1.deployments.handle_deploy_background") as mock_bg:
            response = client.post(f"/api/v1/deployments/webhook/{deployment_id}", content=body, headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == "deployment_queued"
    # Ensure background task was triggered
    mock_bg.assert_called_once_with(deployment_id)

def test_webhook_push_mismatch(client, session):
    d = create_deployment(session, branch="main")
    deployment_id = d.id
    secret = d.secret

    payload = {"ref": "refs/heads/dev"}
    body = json.dumps(payload).encode()
    signature = generate_signature(secret, body)

    headers = {
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "push"
    }

    with patch("app.api.v1.deployments.engine", session.bind):
        response = client.post(f"/api/v1/deployments/webhook/{deployment_id}", content=body, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "ignored"
    assert "ignored" in response.json()["message"]

def test_webhook_tag_push(client, session):
    d = create_deployment(session, branch="main")
    deployment_id = d.id
    secret = d.secret

    payload = {"ref": "refs/tags/v1.0.0"}
    body = json.dumps(payload).encode()
    signature = generate_signature(secret, body)

    headers = {
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "push"
    }

    with patch("app.api.v1.deployments.engine", session.bind):
        response = client.post(f"/api/v1/deployments/webhook/{deployment_id}", content=body, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "ignored"

def test_webhook_invalid_signature(client, session):
    d = create_deployment(session)
    deployment_id = d.id

    payload = {"ref": "refs/heads/main"}
    body = json.dumps(payload).encode()
    signature = "sha256=invalid"

    headers = {
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "push"
    }

    with patch("app.api.v1.deployments.engine", session.bind):
        response = client.post(f"/api/v1/deployments/webhook/{deployment_id}", content=body, headers=headers)
    assert response.status_code == 401
