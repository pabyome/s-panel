from sqlmodel import SQLModel
from typing import List, Optional
from pydantic import field_validator

class WafConfigBase(SQLModel):
    enabled: bool = True
    cc_deny_rate: int = 100
    cc_deny_burst: int = 10
    rule_keywords: List[str] = []
    rule_scan_block: bool = False
    rule_hacking_block: bool = False

    @field_validator('cc_deny_rate')
    @classmethod
    def check_rate(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('Rate must be positive')
        return v

    @field_validator('cc_deny_burst')
    @classmethod
    def check_burst(cls, v: int) -> int:
        if v < 0:
            raise ValueError('Burst must be non-negative')
        return v

class WafConfigCreate(WafConfigBase):
    website_id: int

class WafConfigUpdate(WafConfigBase):
    pass

class WafConfigRead(WafConfigBase):
    id: int
    website_id: int
