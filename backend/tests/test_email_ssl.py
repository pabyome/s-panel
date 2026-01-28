from unittest.mock import patch, MagicMock
from app.services.email_service import EmailService

def test_email_ssl_port_465():
    """Verify that port 465 triggers SMTP_SSL"""

    mock_config = {
        "host": "smtp.example.com",
        "port": 465, # Trigger for SSL
        "user": "user",
        "password": "pass",
        "from_email": "admin@example.com",
        "admin_emails": ["admin@example.com"]
    }

    with patch("app.services.email_service.EmailService.get_smtp_config", return_value=mock_config):
        with patch("smtplib.SMTP_SSL") as mock_ssl, patch("smtplib.SMTP") as mock_plain:
            # Setup mocks
            instance = mock_ssl.return_value

            # Act
            result, msg = EmailService.send_email("Test", "Body", ["test@example.com"])

            # Assert
            assert result is True
            mock_ssl.assert_called_with("smtp.example.com", 465)
            mock_plain.assert_not_called()
            instance.login.assert_called_with("user", "pass")
            instance.send_message.assert_called()

def test_email_tls_port_587():
    """Verify that port 587 triggers SMTP + starttls"""

    mock_config = {
        "host": "smtp.example.com",
        "port": 587, # Trigger for TLS
        "user": "user",
        "password": "pass",
        "from_email": "admin@example.com",
        "admin_emails": ["admin@example.com"]
    }

    with patch("app.services.email_service.EmailService.get_smtp_config", return_value=mock_config):
        with patch("smtplib.SMTP_SSL") as mock_ssl, patch("smtplib.SMTP") as mock_plain:
             # Setup mocks
            instance = mock_plain.return_value

            # Act
            result, msg = EmailService.send_email("Test", "Body", ["test@example.com"])

            # Assert
            assert result is True
            mock_plain.assert_called_with("smtp.example.com", 587)
            mock_ssl.assert_not_called()
            instance.starttls.assert_called_once()
            instance.login.assert_called_with("user", "pass")
