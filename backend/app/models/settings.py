from typing import Optional
from sqlmodel import SQLModel, Field

class SystemSetting(SQLModel, table=True):
    key: str = Field(primary_key=True)
    value: str
    description: Optional[str] = None
