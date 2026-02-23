from datetime import timedelta
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from app.api.deps import SessionDep, CurrentUser, CurrentAdmin
from app.models.database import User
from app.services.auth_service import AuthService
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserUpdate, UserRead

router = APIRouter()


@router.post("/login", response_model=Token)
def login_for_access_token(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    auth_service = AuthService(session)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=user.username, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


# --- User Management Endpoints ---


@router.get("/users", response_model=List[UserRead])
def list_users(session: SessionDep, current_user: CurrentAdmin):
    """List all panel users"""
    users = session.exec(select(User)).all()
    return users


@router.post("/users", response_model=UserRead)
def create_user(user_data: UserCreate, session: SessionDep, current_user: CurrentAdmin):
    """Create a new panel user"""
    # Check if username already exists
    existing = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    auth_service = AuthService(session)
    new_user = auth_service.create_user(user_data.username, user_data.password, user_data.role)
    return new_user


@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: SessionDep, current_user: CurrentUser):
    """Get a single user by ID"""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_data: UserUpdate, session: SessionDep, current_user: CurrentUser):
    """Update a panel user"""
    # Authorization Check
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent role escalation
    if current_user.role != "admin" and user_data.role is not None and user_data.role != user.role:
        raise HTTPException(status_code=403, detail="Cannot change role")

    # Check if trying to update username to an existing one
    if user_data.username and user_data.username != user.username:
        existing = session.exec(select(User).where(User.username == user_data.username)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")
        user.username = user_data.username

    if user_data.password:
        user.password_hash = get_password_hash(user_data.password)

    if user_data.role:
        user.role = user_data.role

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/users/{user_id}")
def delete_user(user_id: int, session: SessionDep, current_user: CurrentAdmin):
    """Delete a panel user"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent deleting the last admin
    admin_count = len(session.exec(select(User).where(User.role == "admin")).all())
    if user.role == "admin" and admin_count <= 1:
        raise HTTPException(status_code=400, detail="Cannot delete the last admin user")

    session.delete(user)
    session.commit()
    return {"ok": True}


@router.get("/me", response_model=UserRead)
def get_current_user(current_user: CurrentUser):
    """Get current authenticated user info"""
    return current_user
