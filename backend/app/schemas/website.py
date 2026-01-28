from sqlmodel import SQLModel
from typing import Optional
from pydantic import field_validator, model_validator
import re


class WebsiteCreate(SQLModel):
    name: str
    domain: str
    port: Optional[int] = None  # Optional for static sites
    project_path: str
    is_static: bool = False  # True for static HTML sites

    @model_validator(mode="after")
    def validate_port_for_dynamic_sites(self):
        if not self.is_static and self.port is None:
            raise ValueError("Port is required for dynamic (proxied) sites")
        if self.is_static and self.port is None:
            # Set a dummy port for static sites (not used but required by model)
            self.port = 0
        return self

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        # Relaxed regex: Allow underscores for internal/dev domains
        hostname_regex = r"^(([a-zA-Z0-9_]|[a-zA-Z0-9_][a-zA-Z0-9\-_]*[a-zA-Z0-9_])\.)*([A-Za-z0-9_]|[A-Za-z0-9_][A-Za-z0-9\-_]*[A-Za-z0-9_])$"
        if not re.match(hostname_regex, v):
            raise ValueError(
                "Invalid domain format. Use format like 'example.com', 'sub.domain.com', or 'staging_site.local'. Underscores are allowed."
            )
        return v

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v != 0 and not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v


class WebsiteRead(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    domain: str
    port: int
    project_path: str
    ssl_enabled: bool
    is_static: bool
    status: str


class WebsiteUpdate(SQLModel):
    """Schema for updating a website - all fields optional"""

    name: Optional[str] = None
    port: Optional[int] = None
    project_path: Optional[str] = None
    is_static: Optional[bool] = None

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v


class NginxConfigUpdate(SQLModel):
    """Schema for nginx config update with validation option"""

    content: str
    validate_only: bool = False  # If true, only validate without saving
