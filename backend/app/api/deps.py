from typing import Generator, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import ValidationError
from sqlmodel import Session
from app.models.database import get_session, User
from app.core.security import ALGORITHM, SECRET_KEY
from app.schemas.token import TokenPayload
from app.services.auth_service import AuthService

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)

def get_db() -> Generator[Session, None, None]:
    yield from get_session()

SessionDep = Annotated[Session, Depends(get_db)]

def get_current_user(session: SessionDep, token: Annotated[str, Depends(reusable_oauth2)]) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except (jwt.PyJWTError, ValidationError): # PyJWT raises PyJWTError
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    auth_service = AuthService(session)
    user = auth_service.get_user_by_username(token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

def get_current_admin(current_user: CurrentUser) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user

CurrentAdmin = Annotated[User, Depends(get_current_admin)]
