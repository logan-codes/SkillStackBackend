# Student profile endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.init_db import get_db
from database.crud.mapping.users import update_external_links
from schemas.mapping.user import StudentProfileUpdate
from core.auth import get_current_user

router = APIRouter()


@router.put("/profile")
def update_my_profile(
    request: StudentProfileUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    links = request.model_dump(exclude_none=True)
    user = update_external_links(db, current_user.id, links)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Profile updated successfully"}
