from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.api.deps import get_current_user
from main import app

client = TestClient(app)

# Mock auth to bypass login
async def mock_get_current_user():
    return MagicMock(username="admin", role="admin")

app.dependency_overrides[get_current_user] = mock_get_current_user

def test_path_traversal_vulnerability():
    # ALLOWED_ROOTS include "/tmp"
    # We try to access "/tmp-secret" which starts with "/tmp" but is a sibling directory

    with patch("os.path.exists", return_value=True):
        with patch("os.path.isdir", return_value=True):
             with patch("os.scandir") as mock_scandir:
                # Mock entries
                entry = MagicMock()
                entry.name = "secret.txt"
                entry.is_dir.return_value = False
                entry.path = "/tmp-secret/secret.txt"

                mock_scandir.return_value.__enter__.return_value = [entry]

                # This should FAIL (return 403) if fixed, but currently passes (200)
                response = client.get("/api/v1/system/path/list?path=/tmp-secret")

                # With the fix, this should now be 403 Forbidden
                assert response.status_code == 403
