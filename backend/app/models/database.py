from sqlmodel import Field, SQLModel, create_engine, Session
from typing import Optional
from datetime import datetime
from app.models.settings import SystemSetting

# Database Models

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    last_login: Optional[datetime] = None
    role: str = "admin"


class FirewallRule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    direction: str # in, out
    port: int
    protocol: str # tcp, udp
    action: str # allow, deny
    group_name: Optional[str] = None

class Plugin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    status: str # installed, running, stopped
    version: str

# Database Connection
sqlite_file_name = "spanel.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
