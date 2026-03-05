# JWT logic lives here (create token, verify token)
# core/auth.py

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt                       # JWT library
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.config import settings                     # SECRET_KEY, ALGORITHM, EXPIRE
from database.init_db import get_db                  # DB session
from database.crud.user import get_user_by_id        # fetch user from DB


# ─────────────────────────────────────────
# OAuth2 scheme
# ─────────────────────────────────────────

# This tells FastAPI: "look for a Bearer token in the Authorization header"
# tokenUrl is just for docs — points to your login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


# ─────────────────────────────────────────
# JOB 1: CREATE token
# ─────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Mints a new JWT token.

    data          = what to put inside the token e.g. {"user_id": 1, "role_id": 2}
    expires_delta = how long until it expires (uses config default if not passed)

    Returns: JWT token string "eyJ..."
    """
    to_encode = data.copy()                          # never mutate original data

    # set expiry time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})               # add expiry into payload

    # SIGN the payload → produces the "eyJ..." string
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,                         # your secret from .env
        algorithm=settings.ALGORITHM                 # HS256
    )

    return encoded_jwt


# ─────────────────────────────────────────
# JOB 2: VERIFY token + get current user
# ─────────────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),             # extracts Bearer token from header
    db: Session = Depends(get_db)                    # gets DB session
):
    """
    The BOUNCER function.
    Called automatically on every protected route via Depends(get_current_user)

    1. Extracts token from Authorization header
    2. Decodes and validates it
    3. Fetches the user from DB
    4. Returns user if all good, raises 401 if not
    """

    # standard 401 error we'll raise if anything goes wrong
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # DECODE the token using SECRET_KEY
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # extract user_id from inside the token
        user_id: int = payload.get("user_id")

        if user_id is None:
            raise credentials_exception             # token has no user_id = invalid

    except JWTError:
        raise credentials_exception                 # token is fake or expired

    # fetch the actual user from DB using the id inside the token
    user = get_user_by_id(db, user_id=user_id)

    if user is None:
        raise credentials_exception                 # user was deleted after token issued

    if user.is_active == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    return user                                     # ✅ all good, return user to endpoint