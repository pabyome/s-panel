from sqlmodel import SQLModel
from typing import Optional

class WebsiteCreate(SQLModel):
    name: str
    domain: str
    port: int
    project_path: str

class WebsiteRead(SQLModel):
    id: int
    name: str
    domain: str
    port: int
    project_path: str
    ssl_enabled: bool
    status: str
