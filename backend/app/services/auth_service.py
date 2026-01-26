from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
from app.models.database import User
from app.core.config import settings
from app.core.security import get_password_hash, verify_password

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.SECRET_KEY = settings.SECRET_KEY
        self.ALGORITHM = settings.ALGORITHM

    def get_user_by_username(self, username: str) -> Optional[User]:
        statement = select(User).where(User.username == username)
        return self.session.exec(statement).first()

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def create_user(self, username: str, password: str, role: str = "admin") -> User:
        hashed_password = get_password_hash(password)
        db_user = User(username=username, password_hash=hashed_password, role=role)
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def ensure_admin_exists(self):
        if not self.get_user_by_username("admin"):
            print("Seeding initial admin user...")
            # Check for env var or default
            import os
            admin_pwd = os.getenv("ADMIN_PASSWORD", "admin123")
            print(f"Seeding initial admin user with password: {admin_pwd}")
            self.create_user("admin", admin_pwd)
