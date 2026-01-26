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
        # 1. No whitespace
        if re.search(r"\s", v):
            raise ValueError("Domain must not contain whitespace")

        # 2. No path traversal or command injection chars
        if any(char in v for char in ["/", "\\", ";", "&", "|", ">", "<", "`", "$", "(", ")"]):
            raise ValueError("Domain contains invalid characters")

        # 3. Structure check
        # Alphanumeric, hyphen, dot. No consecutive dots. No start/end hyphen/dot.
        domain_regex = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$"

        if not re.match(domain_regex, v):
             raise ValueError("Invalid domain format")

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
