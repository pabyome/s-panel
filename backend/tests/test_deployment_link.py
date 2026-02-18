from unittest.mock import MagicMock, patch
from sqlmodel import Session, SQLModel, create_engine, select
from app.models.deployment import DeploymentConfig, DeploymentUpdate
from app.models.website import Website
from app.models.database import User
from app.api.v1.deployments import update_deployment
import uuid
import pytest

# Setup in-memory DB
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
SQLModel.metadata.create_all(engine)

@pytest.fixture(name="session")
def session_fixture():
    with Session(engine) as session:
        yield session

def test_update_deployment_link_website(session):
    # Mock NginxManager to avoid system calls
    with patch("app.services.website_manager.NginxManager") as mock_nginx:
        mock_nginx.create_site.return_value = True
        mock_nginx.secure_site.return_value = True
        mock_nginx.remove_site.return_value = True

        # Create User
        user = User(username="admin", password_hash="pw")
        session.add(user)
        session.commit()
        session.refresh(user)

        # Create deployment
        deploy = DeploymentConfig(
            name="Test Deploy",
            project_path="/var/www/test",
            secret="secret",
            deployment_mode="supervisor"
        )
        session.add(deploy)
        session.commit()
        session.refresh(deploy)

        # Mock User (Use real user object actually, or mock that mimics it)
        # update_deployment expects CurrentUser which is usually User model instance
        # passing real user is better

        # 1. Update to ADD website
        update_data = DeploymentUpdate(
            website_domain="example.com",
            website_ssl=True
        )

        # We need to ensure CronManager doesn't fail either
        with patch("app.services.cron_manager.CronManager"):
             result = update_deployment(deploy.id, update_data, session, user)

        # Verify result has fields
        # Note: if website creation failed, these might be None
        print(f"Result Domain: {result.website_domain}")

        # Verify DB
        website = session.exec(select(Website).where(Website.deployment_id == deploy.id)).first()
        assert website is not None, "Website was not created in DB"
        assert website.domain == "example.com"
        assert website.ssl_enabled is True

        # Verify result match
        assert result.website_domain == "example.com"
        assert result.website_ssl is True

        # 2. Update to REMOVE website
        update_data_remove = DeploymentUpdate(
            website_domain="",
            website_ssl=False
        )

        result = update_deployment(deploy.id, update_data_remove, session, user)

        # Verify result fields cleared
        assert not result.website_domain
        assert result.website_ssl is False # Default

        # Verify DB
        website = session.exec(select(Website).where(Website.deployment_id == deploy.id)).first()
        assert website is None
