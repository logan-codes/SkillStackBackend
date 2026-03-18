#What data comes IN and goes OUT (shapes)
# schemas/mapping/user.py

from pydantic import BaseModel, EmailStr
from typing import Optional


# ─────────────────────────────────────────
# REQUEST schemas  (data coming IN)
# ─────────────────────────────────────────

class LoginRequest(BaseModel):
    """
    What the frontend sends to /login
    POST /api/v1/users/login
    Body: { "email_id": "student@college.edu" }
    """
    email_id: EmailStr                       # EmailStr auto validates it's a real email format


# ─────────────────────────────────────────
# RESPONSE schemas  (data going OUT)
# ─────────────────────────────────────────

class TokenResponse(BaseModel):
    """
    What YOUR backend returns after successful login
    { "access_token": "eyJ...", "token_type": "bearer" }
    """
    access_token: str
    token_type: str = "bearer"               # always "bearer", frontend needs this


class UserInfo(BaseModel):
    """
    Optional: safe user details to return alongside token
    NEVER return password, never return raw DB row
    """
    id: int
    name: Optional[str] = None
    email_id: str
    role_id: Optional[int] = None
    is_active: int

    class Config:
        from_attributes = True               # allows reading from SQLAlchemy model directly


class LoginResponse(BaseModel):
    """
    Full response after login — token + basic user info
    """
    access_token: str
    token_type: str = "bearer"
    user: UserInfo

class RegisterRequest(BaseModel):
    email_id: EmailStr
    name: str
    role_id: int
    gender_id: int
    password: str
