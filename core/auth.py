# core/auth.py
# Handles all JWT logic:
#   - Creating access tokens
#   - Verifying tokens and returning the current authenticated user
#   - Role-based access control (RBAC)

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.config import settings
from database.init_db import get_db
from database.crud.mapping.users import get_user_by_id


# ──────────────────────────────────────────────────────────────
# ROLE CONSTANTS
# Used for RBAC - Role-Based Access Control
# ──────────────────────────────────────────────────────────────

ADMIN = 0      # Admin role ID (highest privilege)
STUDENT = 1    # Student role ID
STAFF = 2      # Staff role ID

ROLE_NAMES = {
    ADMIN: "admin",
    STUDENT: "student",
    STAFF: "staff"
}


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
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})  # Embed expiry into the payload

    # Sign and encode the payload into a JWT string
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,   # Secret key from .env
        algorithm=settings.ALGORITHM  # e.g. HS256
    )

    return encoded_jwt


# ──────────────────────────────────────────────────────────────
# DECODE BEARER TOKEN
# Returns user_id and role_id from JWT token
# ──────────────────────────────────────────────────────────────

def decode_bearer(token: str = Depends(oauth2_scheme)) -> tuple:
    """
    Decodes the Bearer token and returns user_id and role_id.

    Returns:
        tuple: (user_id, role_id)

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
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

        # Extract user_id and role_id from the token payload
        user_id = payload.get("user_id")
        role_id = payload.get("role_id")

        if user_id is None:
            raise credentials_exception

        return user_id, role_id

    except JWTError:
        raise credentials_exception


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

    return user  # Token valid, user active — return to the protected route


# ──────────────────────────────────────────────────────────────
# RBAC - ROLE-BASED ACCESS CONTROL DEPENDENCIES
# ──────────────────────────────────────────────────────────────

def require_admin(current_user = Depends(get_current_user)):
    """Dependency for admin-only endpoints"""
    if current_user.role_id != ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_staff(current_user = Depends(get_current_user)):
    """Dependency for staff-only endpoints (includes admin)"""
    if current_user.role_id not in [ADMIN, STAFF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff access required"
        )
    return current_user


def require_any_auth(current_user = Depends(get_current_user)):
    """Dependency for any authenticated user (all roles)"""
    return current_user
