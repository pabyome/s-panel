import pytest
from unittest.mock import MagicMock, patch
from sqlmodel import Session, SQLModel, create_engine
from app.services.website_manager import WebsiteManager
from app.schemas.website import WebsiteCreate
from app.models.website import Website

# Use in-memory SQLite for tests
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@patch("app.services.website_manager.NginxManager")
def test_create_website(mock_nginx, session):
    # Setup
    mock_nginx.create_site.return_value = True
    manager = WebsiteManager(session)
    website_data = WebsiteCreate(
        name="Test Site",
        domain="test.com",
        port=3000,
        project_path="/var/www/test"
    )

    # Action
    website = manager.create_website(website_data)

    # Assert
    assert website.id is not None
    assert website.domain == "test.com"
    # Verify NginxManager was called
    mock_nginx.create_site.assert_called_once_with("test.com", 3000, is_static=False, project_path="/var/www/test")

@patch("app.services.website_manager.NginxManager")
def test_delete_website(mock_nginx, session):
    # Setup
    manager = WebsiteManager(session)
    website = Website(name="Del Site", domain="del.com", port=4000, project_path="/")
    session.add(website)
    session.commit()

    # Action
    success = manager.delete_website(website.id)

    # Assert
    assert success is True
    assert session.get(Website, website.id) is None
    mock_nginx.remove_site.assert_called_once_with("del.com")
