from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime


class UserLogin(SQLModel):
    username: str
    password: str


class UserCreate(SQLModel):
    username: str
    password: str
    role: str = "admin"


class UserUpdate(SQLModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


class UserRead(SQLModel):
    model_config = {"from_attributes": True}

    id: int
    username: str
    role: str
    last_login: Optional[datetime] = None
