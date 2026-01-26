from pydantic import BaseModel
from typing import Optional

class SupervisorProcess(BaseModel):
    name: str
    group: str
    statename: str
    state: int
    description: str

class SupervisorConfigUpdate(BaseModel):
    content: str
