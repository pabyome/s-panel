from unittest.mock import patch, MagicMock
from sqlmodel import Session
from app.services.website_manager import WebsiteManager
from app.models.website import Website


@patch("app.services.website_manager.NginxManager")
@patch("app.services.cron_manager.CronManager")
def test_enable_ssl_calls_ensure_job(mock_cron_manager, mock_nginx_manager):
    # Setup mock session and website
    mock_session = MagicMock(spec=Session)
    mock_website = MagicMock(spec=Website)
    mock_website.domain = "example.com"
    mock_website.id = 1

    # Mock get_website_by_id
    mock_session.get.return_value = mock_website

    # Mock NginxManager success
    mock_nginx_manager.secure_site.return_value = (True, "Certificate installed")

    manager = WebsiteManager(mock_session)
    result, msg = manager.enable_ssl(1, "test@example.com")

    assert result is True
    assert mock_website.ssl_enabled is True

    # Verify NginxManager called
    mock_nginx_manager.secure_site.assert_called_with(mock_website.domain, "test@example.com")

    # Verify CronManager.ensure_job called
    mock_cron_manager.ensure_job.assert_called_once_with(
        job_id="ssl-auto-renew",
        command='certbot renew --quiet --deploy-hook "nginx -s reload"',
        schedule="0 3 * * *",
        comment="Global SSL Auto-Renewal",
    )


@patch("app.services.website_manager.NginxManager")
@patch("app.services.cron_manager.CronManager")
def test_enable_ssl_fails_cron_does_not_break(mock_cron_manager, mock_nginx_manager):
    # Setup mock session and website
    mock_session = MagicMock(spec=Session)
    mock_website = MagicMock(spec=Website)
    mock_website.domain = "example.com"
    mock_website.id = 1

    mock_session.get.return_value = mock_website
    mock_nginx_manager.secure_site.return_value = (True, "Certificate installed")

    # Mock CronManager raising exception
    mock_cron_manager.ensure_job.side_effect = Exception("Cron failure")

    manager = WebsiteManager(mock_session)
    # Should not raise exception
    result, msg = manager.enable_ssl(1, "test@example.com")

    assert result is True
    mock_cron_manager.ensure_job.assert_called_once()
