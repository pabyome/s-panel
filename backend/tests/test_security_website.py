import pytest
from app.schemas.website import WebsiteCreate
from pydantic import ValidationError

def test_website_create_invalid_domain_path_traversal():
    with pytest.raises(ValidationError):
        WebsiteCreate(
            name="Bad Site",
            domain="../../etc/passwd",
            port=3000,
            project_path="/var/www/html"
        )

def test_website_create_invalid_domain_injection():
    with pytest.raises(ValidationError):
        WebsiteCreate(
            name="Bad Site",
            domain="example.com; rm -rf /",
            port=3000,
            project_path="/var/www/html"
        )

def test_website_create_invalid_domain_spaces():
    with pytest.raises(ValidationError):
        WebsiteCreate(
            name="Bad Site",
            domain="example .com",
            port=3000,
            project_path="/var/www/html"
        )

def test_website_create_valid_domain():
    # Should not raise
    WebsiteCreate(
        name="Good Site",
        domain="example.com",
        port=3000,
        project_path="/var/www/html"
    )
    WebsiteCreate(
        name="Good Site",
        domain="sub.example.co.uk",
        port=3000,
        project_path="/var/www/html"
    )
