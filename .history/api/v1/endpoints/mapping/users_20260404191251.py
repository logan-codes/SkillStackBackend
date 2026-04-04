# User endpoints - login, profile, authentication
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.init_db import get_db
from database.crud.mapping.users import get_user_by_email, get_user_by_id
from schemas.mapping.user import LoginRequest, LoginResponse, UserInfo
from core.auth import create_access_token, get_current_user, require_admin

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email_id=request.email_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user.is_active == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive"
        )

    access_token = create_access_token(
        data={"user_id": user.id, "role_id": user.role_id}
    )
    return LoginResponse(
        access_token=access_token,
        user=UserInfo(
            id=user.id,
            name=user.name,
            email_id=user.email_id,
            role_id=user.role_id,
            is_active=user.is_active,
        ),
    )


@router.get("/me", response_model=UserInfo)
def get_my_profile(current_user=Depends(get_current_user)):
    return UserInfo(
        id=current_user.id,
        name=current_user.name,
        email_id=current_user.email_id,
        role_id=current_user.role_id,
        is_active=current_user.is_active,
    )


@router.get("/profile/full")
def get_my_full_profile(
    current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    user = get_user_by_id(db, user_id=current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {
        "id": user.id,
        "email_id": user.email_id,
        "name": user.name,
        "role_id": user.role_id,
        "is_active": user.is_active,
    }



@router.get("/all")
def get_all_users(current_user=Depends(require_admin), db: Session = Depends(get_db)):
    from database.models.mapping.users import User

    users = db.query(User).filter(User.is_active == 1).all()
    return [
        UserInfo(
            id=u.id,
            name=u.name,
            email_id=u.email_id,
            role_id=u.role_id,
            is_active=u.is_active,
        )
        for u in users
    ]
