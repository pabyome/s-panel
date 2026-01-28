import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.models.database import engine, get_session
from app.models.deployment import DeploymentConfig
from main import app
from app.services.git_service import GitService
from unittest.mock import patch, MagicMock
import hmac
import hashlib
import json

# Setup in-memory DB for tests
from sqlalchemy.pool import StaticPool

@pytest.fixture(name="session")
def session_fixture():
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(test_engine)

    # Patch the global engine AND GitService internals for user detection
    # We patch pwd and os.stat globally for tests to assume a safe user
    with patch("app.api.v1.deployments.engine", test_engine), \
         patch("app.models.database.engine", test_engine), \
         patch("app.services.git_service.os.stat") as mock_stat, \
         patch("app.services.git_service.pwd") as mock_pwd:

         # Setup mock user
         mock_stat.return_value.st_uid = 1000
         mock_pwd.getpwuid.return_value.pw_name = "testuser"

         with Session(test_engine) as session:
            yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    # Mock Auth to return a dummy user
    # app.dependency_overrides[get_current_user] = ... (if auth required for CRUD)
    return TestClient(app)

# Helper to generate HMAC
def generate_signature(secret: str, payload: bytes) -> str:
    return "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

def test_create_deployment(client: TestClient):
    pass

def test_git_service_pull_success():
    with patch("subprocess.run") as mock_run, \
         patch("os.path.isdir", return_value=True): # Mock isdir
        mock_run.return_value = MagicMock(returncode=0, stdout="Already up to date.")

        # Test basic pull
        success, logs, commit = GitService.pull_and_deploy("/tmp/test", "main")

        assert success is True
        assert "Step 1: Fetching and pulling" in logs
        assert "Deployment completed successfully" in logs

def test_git_service_post_command():
    with patch("subprocess.run") as mock_run, \
         patch("app.services.git_service.os.stat") as mock_stat, \
         patch("app.services.git_service.pwd") as mock_pwd, \
         patch("os.path.isdir", return_value=True):

        # Setup user mock
        mock_stat.return_value.st_uid = 1000
        mock_pwd.getpwuid.return_value.pw_name = "testuser"

        # We expect 4 calls roughly (git config, git pull, git rev-parse, post cmd)
        # But wait, GitService does calls.

        # side_effect:
        # 1. git config (ignored)
        # 2. git pull
        # 3. git rev-parse
        # 4. npm (command parsed: [npm, run, build]) -> subprocess.run(['sudo', '-u', 'root', 'npm', 'run', 'build'])

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=""), # git config
            MagicMock(returncode=0, stdout="Already up to date."), # git pull
            MagicMock(returncode=0, stdout="hash123"), # git rev-parse
            MagicMock(returncode=0, stdout="Built.")   # npm run build
        ]

        success, logs, commit = GitService.pull_and_deploy("/tmp/test", "main", "npm run build")

        assert success is True
        assert "Step 2: Running post-deploy command" in logs

def test_webhook_hmac_verification(client: TestClient, session: Session):
    # 1. Create a Deployment in DB
    deploy = DeploymentConfig(
        name="Test Deploy",
        project_path="/tmp/test",
        secret="mysecretkey123"
    )
    session.add(deploy)
    session.commit()
    session.refresh(deploy)

    url = f"/api/v1/deployments/webhook/{deploy.id}"
    payload = {"ref": "refs/heads/main"}
    payload_bytes = json.dumps(payload).encode()

    # 2. Valid Signature
    signature = generate_signature(deploy.secret, payload_bytes)

    # We patch handle_deploy_background to avoid DB issues during background execution
    with patch("app.api.v1.deployments.handle_deploy_background") as mock_bg:

        # Needed headers for new logic
        headers = {
            "X-Hub-Signature-256": signature,
            "X-GitHub-Event": "push"
        }

        response = client.post(
            f"/api/v1/deployments/webhook/{deploy.id}", # Correct URL
            content=payload_bytes,
            headers=headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "deployment_queued"

        # Verify background task was added
        mock_bg.assert_called_once_with(deploy.id)

def test_webhook_invalid_signature(client: TestClient, session: Session):
    deploy = DeploymentConfig(
        name="Test Deploy",
        project_path="/tmp/test",
        secret="mysecretkey123"
    )
    session.add(deploy)
    session.commit()

    url = f"/api/v1/deployments/webhook/{deploy.id}"
    payload = b"{}"

    response = client.post(
        url,
        content=payload,
        headers={"X-Hub-Signature-256": "sha256=invalid"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid signature"

def test_git_service_subshell_syntax():
    # Test (cd foo && bar) syntax
    command = "(cd backend && npm install)"
    is_valid, msg, parsed = GitService.validate_command(command)
    assert is_valid is True
    # parsed should be [['cd', 'backend'], ['npm', 'install']]
    assert len(parsed) == 2
    assert parsed[0] == ['cd', 'backend']
    assert parsed[1] == ['npm', 'install']
