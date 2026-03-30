# api/v1/endpoints/mapping/users.py
# User endpoints - login, profile, activities

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.init_db import get_db
from database.crud.mapping.users import get_user_by_email, get_user_by_id
from schemas.mapping.user import LoginRequest, LoginResponse, UserInfo
from core.auth import create_access_token, get_current_user, require_admin

router = APIRouter()


# ──────────────────────────────────────────────────────────────
# PUBLIC ROUTES — no token needed
# ──────────────────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login endpoint — SSO Option A.

    Frontend handles SSO login (Google/Microsoft) and extracts the user's email.
    Frontend sends that email here. Backend then:
        1. Checks if the email exists in our DB
        2. Checks if the user account is active
        3. Mints our own JWT token
        4. Returns the token + user info to the frontend
    """
    # Step 1: Find user in database
    user = get_user_by_email(db, email_id=request.email_id)

    # Step 2: Does this email exist?
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please contact admin."
        )

    # Step 3: Is this user active?
    if user.is_active == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive. Please contact admin."
        )

    # Step 4: Mint the JWT token
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "role_id": user.role_id
        }
    )

    # Step 5: Return token + user info
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


# ──────────────────────────────────────────────────────────────
# PROTECTED ROUTES — token required
# ──────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserInfo)
def get_my_profile(
    current_user = Depends(get_current_user)
):
    """
    Get current user's profile.
    Frontend must send: Authorization: Bearer <token>
    """
    return UserInfo(
        id=current_user.id,
        name=current_user.name,
        email_id=current_user.email_id,
        role_id=current_user.role_id,
        is_active=current_user.is_active
    )


@router.get("/profile/full")
def get_my_full_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's full profile including all fields.
    """
    user = get_user_by_id(db, user_id=current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "email_id": user.email_id,
        "name": user.name,
        "role_id": user.role_id,
        "gender_id": user.gender_id,
        "register_no": user.register_no,
        "staff_id": user.staff_id,
        "program_dept_id": user.program_dept_id,
        "year": user.year,
        "semester": user.semester,
        "cgpa": float(user.cgpa) if user.cgpa else None,
        "contact_no": user.contact_no,
        "total_tokens": user.total_tokens,
        "is_active": user.is_active,
        "created_date": user.created_date
    }


@router.put("/profile")
def update_my_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.
    Note: Add fields you want to allow updating
    """
    user = get_user_by_id(db, user_id=current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # TODO: Add fields to update (contact_no, etc.)
    # For now, just return success
    
    return {
        "message": "Profile update endpoint ready",
        "user_id": user.id
    }


# ──────────────────────────────────────────────────────────────
# ADMIN ONLY ROUTES
# ──────────────────────────────────────────────────────────────

@router.get("/all")
def get_all_users(
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all users (Admin only).
    """
    from database.models.mapping.users import User
    
    users = db.query(User).filter(User.is_active == 1).all()
    
    return [
        UserInfo(
            id=user.id,
            name=user.name,
            email_id=user.email_id,
            role_id=user.role_id,
            is_active=user.is_active
        )
        for user in users
    ]
