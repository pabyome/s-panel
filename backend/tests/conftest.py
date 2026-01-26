import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from app.models.database import get_session
from app.api.deps import get_current_user
from main import app
from unittest.mock import MagicMock

# Create a shared in-memory engine for all tests
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    def get_current_user_override():
        user = MagicMock()
        user.is_superuser = True
        user.username = "testadmin"
        return user

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    yield TestClient(app)

    app.dependency_overrides.clear()
