from sqlmodel import SQLModel
from typing import Optional

class UserLogin(SQLModel):
    username: str
    password: str

class UserRead(SQLModel):
    id: int
    username: str
    role: str
