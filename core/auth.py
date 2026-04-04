# Authentication & Authorization
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from core.config import settings
from database.init_db import get_db
from database.crud.mapping.users import get_user_by_id

# Role constants
ADMIN = 1
STAFF = 2
STUDENT = 3

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_id(db, user_id=user_id)
    if user is None or user.is_active == 0:
        raise credentials_exception
    return user


def require_admin(current_user=Depends(get_current_user)):
    if current_user.role_id != ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


def require_staff(current_user=Depends(get_current_user)):
    if current_user.role_id not in [ADMIN, STAFF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Staff access required"
        )
    return current_user
