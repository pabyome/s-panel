from app.services.email_service import EmailService
from app.models.settings import SystemSetting
from sqlmodel import select
from unittest.mock import patch

def test_get_settings_defaults(client, session):
    with patch("app.services.email_service.engine", session.bind):
        response = client.get("/api/v1/notifications/settings")
        assert response.status_code == 200
        data = response.json()
        assert data["host"] == ""

def test_update_and_get_settings(client, session):
    payload = {
        "host": "smtp.example.com",
        "port": 587,
        "user": "user",
        "password": "password",
        "from_email": "noreply@example.com",
        "admin_emails": ["admin@example.com"],
        "deployment_alerts_enabled": True,
        "alert_email_recipient": "alert@example.com"
    }

    with patch("app.services.email_service.engine", session.bind):
        response = client.post("/api/v1/notifications/settings", json=payload)
        if response.status_code != 200:
            print(response.json())
        assert response.status_code == 200

        # Verify persistence
        response = client.get("/api/v1/notifications/settings")
        assert response.status_code == 200
        data = response.json()
        assert data["host"] == "smtp.example.com"
        assert data["deployment_alerts_enabled"] is True
        assert data["alert_email_recipient"] == "alert@example.com"
        assert "admin@example.com" in data["admin_emails"]

@patch("app.services.email_service.EmailService.send_email")
def test_send_test_email(mock_send_email, client, session):
    mock_send_email.return_value = True

    payload = {"to_email": "test@example.com"}
    with patch("app.services.email_service.engine", session.bind):
        response = client.post("/api/v1/notifications/test-email", json=payload)

    assert response.status_code == 200
    mock_send_email.assert_called_once()
