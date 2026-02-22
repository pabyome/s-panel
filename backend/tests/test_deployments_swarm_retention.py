import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from app.api.v1.deployments import handle_deploy_background
from app.models.deployment import DeploymentConfig

@pytest.mark.anyio
async def test_handle_deploy_background_swarm_retention():
    deployment_id = uuid.uuid4()

    mock_session = MagicMock()
    mock_deployment = DeploymentConfig(
        id=deployment_id,
        name="Test Deploy",
        deployment_mode="docker-swarm", # Trigger swarm logic
        project_path="/tmp",
        secret="secret",
        branch="main",
        is_laravel=False
    )

    # Mock session context manager
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.get.return_value = mock_deployment

    # Patch dependencies
    with patch("app.api.v1.deployments.Session", return_value=mock_session), \
         patch("app.api.v1.deployments.engine"), \
         patch("app.api.v1.deployments.docker_service.update_swarm_retention") as mock_update_retention, \
         patch("app.api.v1.deployments.broadcast_deployment_update", new_callable=AsyncMock), \
         patch("app.api.v1.deployments.EmailService.send_email", return_value=(True, "OK")), \
         patch("app.api.v1.deployments.EmailService.get_deployment_alert_settings", return_value={"enabled": False, "alert_email": ""}), \
         patch("asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:

        # Mock loop and executor
        mock_loop = MagicMock()
        mock_run_in_executor = AsyncMock(return_value=(True, "logs", "hash"))
        mock_loop.run_in_executor = mock_run_in_executor

        with patch("asyncio.get_running_loop", return_value=mock_loop):
             await handle_deploy_background(deployment_id)

        # Verify update_swarm_retention was called
        mock_to_thread.assert_called_with(mock_update_retention, 2)

@pytest.mark.anyio
async def test_handle_deploy_background_laravel_retention():
    deployment_id = uuid.uuid4()

    mock_session = MagicMock()
    mock_deployment = DeploymentConfig(
        id=deployment_id,
        name="Test Laravel",
        deployment_mode="docker-swarm",
        project_path="/tmp",
        secret="secret",
        branch="main",
        is_laravel=True # Trigger Laravel logic
    )

    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.get.return_value = mock_deployment

    with patch("app.api.v1.deployments.Session", return_value=mock_session), \
         patch("app.api.v1.deployments.engine"), \
         patch("app.api.v1.deployments.LaravelService.deploy", new_callable=AsyncMock) as mock_laravel_deploy, \
         patch("app.api.v1.deployments.docker_service.update_swarm_retention") as mock_update_retention, \
         patch("app.api.v1.deployments.broadcast_deployment_update", new_callable=AsyncMock), \
         patch("app.api.v1.deployments.EmailService.send_email", return_value=(True, "OK")), \
         patch("app.api.v1.deployments.EmailService.get_deployment_alert_settings", return_value={"enabled": False, "alert_email": ""}), \
         patch("asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread, \
         patch("asyncio.get_running_loop"):

        mock_laravel_deploy.return_value = (True, "logs", "hash", "tag")

        await handle_deploy_background(deployment_id)

        mock_to_thread.assert_called_with(mock_update_retention, 2)
