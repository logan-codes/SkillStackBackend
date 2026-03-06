# core/auth.py
# Handles all JWT logic:
#   - Creating access tokens
#   - Verifying tokens and returning the current authenticated user

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.config import settings
from database.init_db import get_db
from database.crud.user import get_user_by_id


# ──────────────────────────────────────────────────────────────
# OAuth2 Scheme
# Tells FastAPI to extract the Bearer token from the
# Authorization header on every protected request.
# tokenUrl is used only by Swagger UI docs.
# ──────────────────────────────────────────────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


# ──────────────────────────────────────────────────────────────
# CREATE ACCESS TOKEN
# ──────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Mints and returns a signed JWT access token.

    Args:
        data          : Payload to embed inside the token (e.g. user_id, role_id).
        expires_delta : Custom expiry duration. Falls back to config default if not provided.

    Returns:
        Signed JWT string (e.g. "eyJ...")
    """
    to_encode = data.copy()  # Avoid mutating the original dict

    # Determine token expiry time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})  # Embed expiry into the payload

    # Sign and encode the payload into a JWT string
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,   # Secret key from .env
        algorithm=settings.ALGORITHM  # e.g. HS256
    )

    return encoded_jwt


# ──────────────────────────────────────────────────────────────
# GET CURRENT USER (Token Verifier / Bouncer)
# ──────────────────────────────────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),  # Pulls Bearer token from Authorization header
    db: Session = Depends(get_db)         # Injects DB session
):
    """
    Validates the JWT token and returns the authenticated user.

    Used as a dependency on protected routes: Depends(get_current_user)

    Flow:
        1. Extract Bearer token from the request header.
        2. Decode and validate the token using the secret key.
        3. Pull the user_id from the token payload.
        4. Fetch the user from the database.
        5. Return the user if everything checks out, else raise 401/403.
    """

    # Reusable 401 error — raised whenever token validation fails
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the token using our secret key
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Extract user_id embedded in the token payload
        user_id: int = payload.get("user_id")

        if user_id is None:
            raise credentials_exception  # Token is missing user_id — invalid

    except JWTError:
        raise credentials_exception  # Token is expired, tampered, or malformed

    # Look up the user in the database using the id from the token
    user = get_user_by_id(db, user_id=user_id)

    if user is None:
        raise credentials_exception  # User no longer exists (deleted after token was issued)

    if user.is_active == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact admin."
        )

    return user  # ✅ Token valid, user active — return to the protected route