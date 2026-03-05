#The /login route the frontend calls
# api/v1/endpoints/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.init_db import get_db                        # DB session
from database.crud.user import get_user_by_email           # Step 4
from schemas.user import LoginRequest, LoginResponse, UserInfo  # Step 3
from core.auth import create_access_token, get_current_user     # Step 5

router = APIRouter()

# PUBLIC ROUTE — no token needed

@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,                  # frontend sends { "email_id": "..." }
    db: Session = Depends(get_db)           # DB session auto injected
):
    """
    Login endpoint.
    1. Receive email_id from frontend
    2. Check if user exists in DB
    3. Check if user is active
    4. Mint JWT token
    5. Return token + user info
    """

    # ── Step 1: Find user in database ──
    user = get_user_by_email(db, email_id=request.email_id)

    # ── Step 2: Does this email exist? ──
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please contact admin."
        )

    # ── Step 3: Is this user active? ──
    if user.is_active == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive. Please contact admin."
        )

    # ── Step 4: Mint the JWT token ──
    access_token = create_access_token(
        data={
            "user_id": user.id,             # goes inside the token
            "role_id": user.role_id         # useful for permissions later
        }
    )

    # ── Step 5: Return token + user info ──
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserInfo(
            id=user.id,
            name=user.name,
            email_id=user.email_id,
            role_id=user.role_id,
            is_active=user.is_active
        )
    )


# ─────────────────────────────────────────
# PROTECTED ROUTE — token required
# This is an example of how to protect any route
# ─────────────────────────────────────────

@router.get("/me")
def get_my_profile(
    current_user = Depends(get_current_user)   # bouncer checks token first
):
    """
    Example protected route.
    Frontend must send: Authorization: Bearer <token>
    Returns the logged in user's profile.
    """
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email_id": current_user.email_id,
        "role_id": current_user.role_id,
        "is_active": current_user.is_active
    }