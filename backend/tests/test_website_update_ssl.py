from unittest.mock import patch, MagicMock
from sqlmodel import Session
from app.models.website import Website
from app.models.waf import WafConfig
from app.schemas.website import WebsiteUpdate
from app.api.v1.websites import update_website

def test_update_website_preserves_ssl_config_direct():
    # 1. Setup mock session and user
    mock_session = MagicMock(spec=Session)
    mock_user = MagicMock()

    # 2. Setup existing website with SSL enabled
    website_id = 1
    existing_website = Website(
        id=website_id,
        name="Test SSL Site",
        domain="ssl.example.com",
        port=8000,
        project_path="/var/www/html",
        ssl_enabled=True,
        is_static=False
    )

    # Configure session.get to return our website
    mock_session.get.return_value = existing_website

    # Configure session.exec().first() to return None (no WAF config)
    mock_exec_result = MagicMock()
    mock_exec_result.first.return_value = None
    mock_session.exec.return_value = mock_exec_result

    # 3. Prepare update data
    update_data = WebsiteUpdate(port=9000)

    # 4. Mock NginxManager methods
    with patch("app.api.v1.websites.NginxManager") as mock_nginx_manager:
        mock_nginx_manager.generate_config.return_value = "mock_config"
        mock_nginx_manager.reload_nginx.return_value = True

        # Mock open() to avoid file I/O
        with patch("builtins.open", new_callable=MagicMock):

            # 5. Call the function directly
            result = update_website(
                website_id=website_id,
                update_data=update_data,
                session=mock_session,
                current_user=mock_user
            )

            # 6. Verify NginxManager.generate_config arguments
            args, kwargs = mock_nginx_manager.generate_config.call_args

            passed_ssl = kwargs.get("ssl_enabled", False)

            # Verify SSL enabled is passed as True
            assert passed_ssl is True, "ssl_enabled was NOT passed as True!"

def test_update_website_preserves_waf_config():
    # 1. Setup mock session and user
    mock_session = MagicMock(spec=Session)
    mock_user = MagicMock()

    # 2. Setup existing website
    website_id = 2
    existing_website = Website(
        id=website_id,
        name="Test WAF Site",
        domain="waf.example.com",
        port=8000,
        project_path="/var/www/html",
        ssl_enabled=False,
        is_static=False
    )

    # Setup WafConfig
    waf_config = WafConfig(website_id=website_id, enabled=True, cc_deny_rate=50)

    # Configure session.get to return our website
    mock_session.get.return_value = existing_website

    # Configure session.exec().first() to return our waf_config
    mock_exec_result = MagicMock()
    mock_exec_result.first.return_value = waf_config
    mock_session.exec.return_value = mock_exec_result

    # 3. Prepare update data
    update_data = WebsiteUpdate(port=9001)

    # 4. Mock NginxManager methods
    with patch("app.api.v1.websites.NginxManager") as mock_nginx_manager:
        mock_nginx_manager.generate_config.return_value = "mock_config"
        mock_nginx_manager.reload_nginx.return_value = True

        # Mock open() to avoid file I/O
        with patch("builtins.open", new_callable=MagicMock):

            # 5. Call the function
            result = update_website(
                website_id=website_id,
                update_data=update_data,
                session=mock_session,
                current_user=mock_user
            )

            # 6. Verify waf_config was passed
            args, kwargs = mock_nginx_manager.generate_config.call_args

            passed_waf = kwargs.get("waf_config", None)

            assert passed_waf is not None
            assert passed_waf.enabled is True
            assert passed_waf.cc_deny_rate == 50
