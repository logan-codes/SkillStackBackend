# User activity endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.init_db import get_db
from database.crud.mapping.user_activity_mapping import (
    start_activity,
    submit_proof,
    delete_user_activity,
    get_user_activities,
    get_user_activity_by_id,
    get_available_categories,
)
from schemas.mapping.user_activity_mapping import (
    UserActivityStart,
    UserActivityProof,
    UserActivityUpdate,
    UserActivityResponse,
)
from core.auth import get_current_user

router = APIRouter()


@router.get("/activities", response_model=List[dict])
def get_activities_for_workflow(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all generic activities available for workflow"""
    from database.models.master.activity_master import ActivityMaster

    activities = db.query(ActivityMaster).filter(ActivityMaster.is_active == 1).all()
    return [{"id": a.id, "activity_name": a.activity_name} for a in activities]


@router.get("/{activity_id}/categories", response_model=List[dict])
def get_activity_categories(
    activity_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get available categories (student goals) for an activity"""
    categories = get_available_categories(db, activity_id)
    if not categories:
        raise HTTPException(
            status_code=404, detail="No categories found for this activity"
        )
    return categories


@router.post("/{activity_id}/start", response_model=UserActivityResponse)
def start_my_activity(
    activity_id: int,
    request: UserActivityStart,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = start_activity(
        db=db,
        user_id=current_user.id,
        activity_id=activity_id,
        custom_name=request.custom_name,
        permission_proof=request.permission_proof,
        start_date=request.start_date,
        end_date=request.end_date,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    if result == "already_started":
        raise HTTPException(status_code=400, detail="Activity already started")
    return result


@router.put("/{user_activity_id}", response_model=UserActivityResponse)
def update_my_activity(
    user_activity_id: int,
    request: UserActivityUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_activity = get_user_activity_by_id(db, user_activity_id, current_user.id)
    if not user_activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # PENDING: can edit custom_name, start_date, end_date, permission_proof, proof_description
    if user_activity.status_id == 1:
        if request.custom_name is not None:
            user_activity.custom_name = request.custom_name
        if request.start_date is not None:
            user_activity.start_date = request.start_date
        if request.end_date is not None:
            user_activity.end_date = request.end_date
        if request.permission_proof is not None:
            user_activity.permission_proof = request.permission_proof
        if request.proof_description is not None:
            user_activity.proof_description = request.proof_description

    # ONGOING: can edit start_date, end_date only
    elif user_activity.status_id == 2:
        if request.start_date is not None:
            user_activity.start_date = request.start_date
        if request.end_date is not None:
            user_activity.end_date = request.end_date

    # SUBMITTED/COMPLETED: cannot edit
    else:
        raise HTTPException(
            status_code=400, detail="Cannot edit activity after submission"
        )

    db.commit()
    db.refresh(user_activity)
    return user_activity


@router.put("/{user_activity_id}/proof", response_model=UserActivityResponse)
def submit_my_proof(
    user_activity_id: int,
    request: UserActivityProof,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = submit_proof(
        db=db,
        user_activity_id=user_activity_id,
        user_id=current_user.id,
        proof=request.proof,
        proof_description=request.proof_description,
        student_goal_id=request.student_goal_id,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    if result == "invalid_status":
        raise HTTPException(
            status_code=400, detail="Can only submit proof when status is ONGOING"
        )
    if result == "student_goal_required":
        raise HTTPException(
            status_code=400, detail="Please select a category (student_goal_id)"
        )
    if result == "invalid_student_goal":
        raise HTTPException(status_code=400, detail="Invalid category selected")
    if result == "invalid_mapping":
        raise HTTPException(
            status_code=400, detail="Selected category does not match this activity"
        )
    return result


@router.delete("/{user_activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_activity(
    user_activity_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = delete_user_activity(
        db=db,
        user_activity_id=user_activity_id,
        user_id=current_user.id,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    if result == "invalid_status":
        raise HTTPException(
            status_code=400, detail="Can only delete when status is PENDING"
        )
    return None


@router.get("/", response_model=List[UserActivityResponse])
def get_my_activities(
    skip: int = 0,
    limit: int = 10,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_activities(db, current_user.id, skip=skip, limit=limit)


@router.get("/{user_activity_id}", response_model=UserActivityResponse)
def get_my_activity(
    user_activity_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_activity = get_user_activity_by_id(db, user_activity_id, current_user.id)
    if not user_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return user_activity
