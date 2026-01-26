from sqlmodel import SQLModel
from typing import Optional

class FirewallRuleCreate(SQLModel):
    port: int
    protocol: str # tcp, udp
    action: str = "allow" # allow, deny

class FirewallRuleRead(SQLModel):
    id: int # UFW numbered rule ID
    to_port: str
    action: str
    from_ip: str
    description: Optional[str] = None
