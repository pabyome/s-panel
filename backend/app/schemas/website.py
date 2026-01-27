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
        # Relaxed regex: Allow underscores for internal/dev domains
        hostname_regex = r"^(([a-zA-Z0-9_]|[a-zA-Z0-9_][a-zA-Z0-9\-_]*[a-zA-Z0-9_])\.)*([A-Za-z0-9_]|[A-Za-z0-9_][A-Za-z0-9\-_]*[A-Za-z0-9_])$"
        if not re.match(hostname_regex, v):
            raise ValueError("Invalid domain format. Use format like 'example.com', 'sub.domain.com', or 'staging_site.local'. Underscores are allowed.")
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
