from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.api.deps import get_current_user
from main import app
import pytest

def test_regular_user_cannot_access_files(client: TestClient):
    def get_current_user_override():
        user = MagicMock()
        user.username = "regular"
        user.role = "user"
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override

    response = client.get("/api/v1/files/list?path=/")
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"

def test_regular_user_cannot_manage_db_users(client: TestClient):
    def get_current_user_override():
        user = MagicMock()
        user.username = "regular"
        user.role = "user"
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override

    # Create user
    response = client.post("/api/v1/mysql/users", json={"name": "test", "password": "password", "grant_all": False})
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"

    # List users (New Check)
    response_list = client.get("/api/v1/mysql/users")
    assert response_list.status_code == 403, f"Expected 403, got {response_list.status_code}"


def test_regular_user_cannot_manage_panel_users(client: TestClient):
    def get_current_user_override():
        user = MagicMock()
        user.username = "regular"
        user.role = "user"
        user.id = 123
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override

    # List users
    response = client.get("/api/v1/auth/users")
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"

    # Get OTHER user (id 999)
    response_other = client.get("/api/v1/auth/users/999")
    assert response_other.status_code == 403, f"Expected 403, got {response_other.status_code}"

    # Get SELF (id 123) - Should be allowed (404 Not Found because user doesn't exist in DB, but NOT 403)
    # Note: We expect 404 because user 123 is not in real DB, or 200 if found.
    # But definitely NOT 403.
    response_self = client.get("/api/v1/auth/users/123")
    assert response_self.status_code != 403, f"Expected !403 for self, got {response_self.status_code}"
