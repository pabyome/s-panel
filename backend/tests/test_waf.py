import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.models.website import Website
from app.models.waf import WafConfig
from main import app
from app.api.deps import get_session, get_current_user
from app.services.nginx_manager import NginxManager
from sqlalchemy.pool import StaticPool

# Setup in-memory DB
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    def get_current_user_override():
        return MagicMock(id=1, role="admin")

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_waf_config_flow(client: TestClient, session: Session):
    # 1. Create a website
    website = Website(
        name="testsite",
        domain="example.com",
        port=8080,
        project_path="/var/www/html",
        owner_id=1,
        ssl_enabled=False
    )
    session.add(website)
    session.commit()
    session.refresh(website)

    # 2. Get default WAF config (should create one)
    response = client.get(f"/api/v1/waf/{website.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["website_id"] == website.id
    assert data["enabled"] == False

    # 3. Update WAF config
    update_data = {
        "website_id": website.id, # Included in Create schema, though usually ignored in update logic via route param
        "enabled": True,
        "cc_deny_rate": 50,
        "cc_deny_burst": 5,
        "rule_keywords": ["sql", "admin"],
        "rule_scan_block": True,
        "rule_hacking_block": True
    }

    # Mock NginxManager.create_site
    with patch("app.services.nginx_manager.NginxManager.create_site") as mock_create_site:
        mock_create_site.return_value = True

        response = client.post(f"/api/v1/waf/{website.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] == True
        assert data["cc_deny_rate"] == 50
        assert data["rule_keywords"] == ["sql", "admin"]

        # Verify NginxManager was called with correct config
        mock_create_site.assert_called_once()
        args, kwargs = mock_create_site.call_args
        waf_config_arg = kwargs.get("waf_config")
        ssl_enabled_arg = kwargs.get("ssl_enabled")

        assert waf_config_arg is not None
        assert waf_config_arg.cc_deny_rate == 50
        assert waf_config_arg.rule_keywords == ["sql", "admin"]
        assert ssl_enabled_arg == False # Default in test website

def test_nginx_generation_logic():
    # Test just the string generation
    waf_config = WafConfig(
        website_id=1,
        enabled=True,
        cc_deny_rate=10,
        cc_deny_burst=5,
        rule_keywords=["hack", "attack"],
        rule_scan_block=True,
        rule_hacking_block=True
    )

    config = NginxManager.generate_config(
        domain="example.com",
        port=8080,
        is_static=False,
        waf_config=waf_config
    )

    # Updated to 1m
    assert "limit_req_zone $binary_remote_addr zone=example_com:1m rate=10r/s;" in config
    assert "limit_req zone=example_com burst=5 nodelay;" in config
    assert 'if ($request_uri ~* "hack") { return 403; }' in config
    assert 'if ($http_user_agent ~* (netcrawler|npbot|malicious|scanner|test|python|curl|wget|nikto|sqlmap))' in config
    assert 'if ($query_string ~* "union.*select.*\\(")' in config

def test_nginx_generation_ssl_logic():
    # Test SSL generation
    waf_config = WafConfig(
        website_id=1,
        enabled=True,
        cc_deny_rate=10,
        cc_deny_burst=5,
        rule_keywords=[],
        rule_scan_block=False,
        rule_hacking_block=False
    )

    config = NginxManager.generate_config(
        domain="example.com",
        port=8080,
        is_static=False,
        waf_config=waf_config,
        ssl_enabled=True
    )

    assert "listen 443 ssl;" in config
    assert "ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;" in config
    assert "return 301 https://$host$request_uri;" in config
