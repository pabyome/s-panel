from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON, Column
from app.models.website import Website

class WafConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    website_id: int = Field(foreign_key="website.id", unique=True)
    enabled: bool = Field(default=True)

    # CC Defense
    cc_deny_rate: int = Field(default=100) # req/s
    cc_deny_burst: int = Field(default=10)

    # Rules
    rule_keywords: List[str] = Field(default=[], sa_column=Column(JSON))
    rule_scan_block: bool = Field(default=False)
    rule_hacking_block: bool = Field(default=False)

    website: Optional[Website] = Relationship()
