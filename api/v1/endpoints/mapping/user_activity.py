# User activity endpoints - Simplified for PostgreSQL
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from database.init_db import get_db
from database.crud.mapping.user_activity_mapping import (
    start_activity,
    submit_proof,
    delete_user_activity,
    get_user_activities,
    get_user_activity_by_id,
    get_available_activities,
    teacher_review,
    validate_teacher_access,
    get_teacher_students,
    get_teacher_student_activities,
    apply_malpractice,
)
from core.auth import get_current_user
from database.models.master.malpractice_master import MalpracticeMaster

router = APIRouter()


class UserActivityStart(BaseModel):
    title: str
    activity_details: Optional[str] = None
    event_type: Optional[int] = None
    activity_start_date: Optional[date] = None
    activity_end_date: Optional[date] = None


class UserActivityUpdate(BaseModel):
    title: Optional[str] = None
    activity_details: Optional[str] = None
    activity_start_date: Optional[date] = None
    activity_end_date: Optional[date] = None


class TeacherReviewRequest(BaseModel):
    action: str  # "approve" or "reject"
    reason: Optional[str] = None


class MalpracticeApply(BaseModel):
    student_id: int
    malpractice_id: int


@router.get("/activities")
def get_all_activities(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all available activities from activity master table"""
    return get_available_activities(db)


@router.post("/{activity_id}/start")
def start_my_activity(
    activity_id: int,
    request: UserActivityStart,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a new activity"""
    result = start_activity(
        db=db,
        user_id=current_user.id,
        activity_id=activity_id,
        title=request.title,
        activity_details=request.activity_details,
        event_type=request.event_type,
        activity_start_date=request.activity_start_date,
        activity_end_date=request.activity_end_date,
    )

    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)

    return {
        "id": result.id,
        "activity_id": result.activity_id,
        "title": result.title,
        "status": result.status,
    }


@router.put("/{activity_id}")
def update_my_activity(
    activity_id: int,
    request: UserActivityUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an activity (only while status is Yet To Start)"""
    user_activity = get_user_activity_by_id(db, activity_id, current_user.id)

    if not user_activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    if user_activity.status != 1:  # Not Yet To Start
        raise HTTPException(
            status_code=400, detail="Cannot edit - activity already in progress"
        )

    if request.title:
        user_activity.title = request.title
    if request.activity_details is not None:
        user_activity.activity_details = request.activity_details
    if request.activity_start_date:
        user_activity.activity_start_date = request.activity_start_date
    if request.activity_end_date:
        user_activity.activity_end_date = request.activity_end_date

    db.commit()
    db.refresh(user_activity)

    return {
        "id": user_activity.id,
        "title": user_activity.title,
        "status": user_activity.status,
    }


@router.post("/{activity_id}/submit")
def submit_activity_proof(
    activity_id: int,
    request: UserActivityUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit proof for an activity (move from In Progress to Submitted)"""
    result = submit_proof(
        db=db,
        activity_id=activity_id,
        user_id=current_user.id,
        activity_details=request.activity_details,
    )

    if result == "not_found":
        raise HTTPException(status_code=404, detail="Activity not found")
    if result == "invalid_status":
        raise HTTPException(status_code=400, detail="Can only submit when in progress")

    return {"status": "submitted", "activity_id": activity_id}


@router.delete("/{activity_id}")
def delete_my_activity(
    activity_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete/withdraw an activity"""
    result = delete_user_activity(db, activity_id, current_user.id)

    if result == "not_found":
        raise HTTPException(status_code=404, detail="Activity not found")
    if result == "cannot_delete":
        raise HTTPException(
            status_code=400, detail="Cannot delete - activity already in progress"
        )

    return {"status": "deleted"}


@router.get("/")
def get_my_activities(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
):
    """Get all my activities"""
    activities = get_user_activities(db, current_user.id, skip, limit)
    return [
        {
            "id": a.id,
            "activity_id": a.activity_id,
            "title": a.title,
            "status": a.status,
            "activity_start_date": a.activity_start_date,
            "activity_end_date": a.activity_end_date,
        }
        for a in activities
    ]


@router.get("/{activity_id}")
def get_my_activity(
    activity_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific activity"""
    activity = get_user_activity_by_id(db, activity_id, current_user.id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    return {
        "id": activity.id,
        "activity_id": activity.activity_id,
        "title": activity.title,
        "activity_details": activity.activity_details,
        "status": activity.status,
        "event_type": activity.event_type,
        "stage_id": activity.stage_id,
        "activity_start_date": activity.activity_start_date,
        "activity_end_date": activity.activity_end_date,
    }


# Teacher endpoints
@router.get("/teacher/students")
def get_teacher_students_list(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get students assigned to current teacher"""
    return get_teacher_students(db, current_user.id)


@router.get("/teacher/students/{student_id}/activities")
def get_student_activities_for_teacher(
    student_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    status: Optional[int] = None,
):
    """Get activities for a specific student"""
    # Validate teacher access
    valid, msg = validate_teacher_access(db, current_user.id, student_id)
    if not valid:
        raise HTTPException(status_code=403, detail=msg)

    activities = get_teacher_student_activities(db, current_user.id, status)
    return [
        {
            "id": a.id,
            "activity_id": a.activity_id,
            "title": a.title,
            "status": a.status,
        }
        for a in activities
    ]


@router.post("/teacher/review/{activity_id}")
def teacher_review_activity(
    activity_id: int,
    request: TeacherReviewRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Teacher approves or rejects an activity"""
    result = teacher_review(
        db=db,
        activity_id=activity_id,
        teacher_user_id=current_user.id,
        action=request.action,
        reason=request.reason,
    )

    if result == "not_found":
        raise HTTPException(status_code=404, detail="Activity not found")
    if result == "invalid_status":
        raise HTTPException(status_code=400, detail="Cannot review this activity")
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)

    return {"status": "reviewed", "action": request.action}


@router.post("/teacher/malpractice")
def apply_student_malpractice(
    request: MalpracticeApply,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Apply malpractice penalty to a student"""
    result = apply_malpractice(
        db=db,
        student_id=request.student_id,
        malpractice_id=request.malpractice_id,
        teacher_user_id=current_user.id,
    )

    if result == "malpractice_not_found":
        raise HTTPException(status_code=404, detail="Malpractice type not found")
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)

    return {"status": "applied"}
