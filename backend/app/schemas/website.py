from sqlmodel import SQLModel
from typing import Optional
from pydantic import field_validator
import re

class WebsiteCreate(SQLModel):
    name: str
    domain: str
    port: int
    project_path: str

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        # Simple regex for hostname (subdomains allowed, no paths, no schemes)
        # e.g., example.com, sub.example.co.uk, localhost
        hostname_regex = r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
        if not re.match(hostname_regex, v):
            raise ValueError("Invalid domain format. Use format like 'example.com' or 'sub.domain.com'")
        return v

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v

class WebsiteRead(SQLModel):
    id: int
    name: str
    domain: str
    port: int
    project_path: str
    ssl_enabled: bool
    status: str
