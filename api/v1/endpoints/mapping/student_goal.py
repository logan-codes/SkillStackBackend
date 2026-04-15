# Student Goal endpoints - Restored full workflow with token tracking
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from database.init_db import get_db
from database.crud.mapping.student_goal import StudentGoalRepo
from database.models.master.activity_master import ActivityMaster
from database.models.mapping.user_activity_mapping import UserActivityMapping
from core.auth import get_current_user

router = APIRouter()

MIN_GOALS = 16  # Minimum token goals required


class PlannedActivity(BaseModel):
    activity_id: int


class StudentGoalCreate(BaseModel):
    activities: List[PlannedActivity]
    target_month: Optional[int] = None


class StudentGoalDelete(BaseModel):
    goal_ids: List[int]


@router.get("/activities")
def get_available_activities(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all activities available for student goals"""
    activities = db.query(ActivityMaster).filter(ActivityMaster.is_active == 1).all()
    return [
        {
            "id": a.id,
            "activity_name": a.activity_name,
            "token": a.token,
            "activity_type_id": a.activity_type_id,
        }
        for a in activities
    ]


@router.get("/")
def get_my_goals(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get my student goals with activity details"""
    repo = StudentGoalRepo(db)
    goals = repo.get_user_goals(current_user.id)

    result = []
    for goal in goals:
        activity = (
            db.query(ActivityMaster)
            .filter(ActivityMaster.id == goal.activity_id)
            .first()
        )

        # Check if this activity is completed
        completed = (
            db.query(UserActivityMapping)
            .filter(
                UserActivityMapping.user_id == current_user.id,
                UserActivityMapping.activity_id == goal.activity_id,
                UserActivityMapping.status == 3,
                UserActivityMapping.is_active == 1,
            )
            .first()
        )

        result.append(
            {
                "id": goal.id,
                "activity_id": goal.activity_id,
                "activity_name": activity.activity_name if activity else "Unknown",
                "token": activity.token if activity else 0,
                "target_month": goal.target_month,
                "is_completed": completed is not None,
            }
        )

    return result


@router.get("/summary")
def get_goal_summary(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get complete goal summary with target/current tokens"""
    repo = StudentGoalRepo(db)
    return repo.get_goal_summary(current_user.id)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_goals(
    request: StudentGoalCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create multiple student goals at once"""
    repo = StudentGoalRepo(db)

    activity_ids = [a.activity_id for a in request.activities]
    goals = repo.create_goals_bulk(current_user.id, activity_ids)

    return {
        "total_created": len(goals),
        "goals": [{"id": g.id, "activity_id": g.activity_id} for g in goals],
    }


@router.delete("/")
def delete_goals(
    request: StudentGoalDelete,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete multiple student goals"""
    repo = StudentGoalRepo(db)

    count = repo.delete_goals_bulk(request.goal_ids)

    return {"deleted": count}


@router.delete("/{goal_id}")
def delete_single_goal(
    goal_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a single student goal"""
    repo = StudentGoalRepo(db)
    goal = repo.get_goal_by_id(goal_id)

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    if goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    repo.delete_goal(goal_id)
    return {"status": "deleted"}


@router.get("/validate")
def validate_goals(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Validate minimum goals requirement"""
    repo = StudentGoalRepo(db)
    goals = repo.get_user_goals(current_user.id)

    if len(goals) < MIN_GOALS:
        remaining = MIN_GOALS - len(goals)
        raise HTTPException(
            status_code=400,
            detail=f"Minimum {MIN_GOALS} goals required. You have {len(goals)}. Add {remaining} more.",
        )

    return {
        "valid": True,
        "total_goals": len(goals),
        "minimum_required": MIN_GOALS,
    }
