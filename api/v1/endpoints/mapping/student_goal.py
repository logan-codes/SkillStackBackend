# Student Goal endpoints - Restored full workflow with token tracking
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from database.init_db import get_db
from database.crud.mapping.student_goal import StudentGoalRepo
from database.models.master.activity_master import ActivityMaster
from core.auth import get_current_user

router = APIRouter()

MIN_TOKENS = 16  # Minimum token goals required


class PlannedActivity(BaseModel):
    activity_id: int
    target_month: Optional[int] = None


class StudentGoalCreate(BaseModel):
    activities: List[PlannedActivity]


class StudentGoalDelete(BaseModel):
    goal_ids: List[int]


@router.get("/activities")
def get_available_activities(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all activities available for student goals (generic only)"""
    activities = db.query(ActivityMaster).filter(ActivityMaster.is_active == 1).all()

    return [
        {
            "id": a.id,
            "activity_name": a.activity_name,
            "token": a.base_token,
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

        result.append(
            {
                "id": goal.id,
                "activity_id": goal.activity_id,
                "activity_name": activity.activity_name if activity else "Unknown",
                "token": activity.base_token if activity else 0,
                "target_month": goal.target_month,
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

    # Create goals with individual target_months
    goals = []
    for activity in request.activities:
        goal = repo.create_goal(
            user_id=current_user.id,
            activity_id=activity.activity_id,
            target_month=activity.target_month,
        )
        if goal:
            goals.append(goal)

    # Validate minimum tokens after creation
    new_activity_ids = [g.activity_id for g in goals]
    activities = (
        db.query(ActivityMaster).filter(ActivityMaster.id.in_(new_activity_ids)).all()
    )
    activity_token_map = {a.id: a.base_token for a in activities}
    total_tokens = sum(activity_token_map.get(g.activity_id, 0) for g in goals)

    return {
        "total_created": len(goals),
        "total_tokens": total_tokens,
        "goals": [
            {"id": g.id, "activity_id": g.activity_id, "target_month": g.target_month}
            for g in goals
        ],
    }


@router.delete("/")
def delete_goals(
    request: StudentGoalDelete,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete multiple student goals"""
    repo = StudentGoalRepo(db)

    # Get current goals
    current_goals = repo.get_user_goals(current_user.id)
    current_activity_ids = [g.activity_id for g in current_goals]

    # Calculate total tokens of current goals
    activities = (
        db.query(ActivityMaster)
        .filter(ActivityMaster.id.in_(current_activity_ids))
        .all()
    )
    activity_token_map = {a.id: a.base_token for a in activities}
    current_tokens = sum(
        activity_token_map.get(g.activity_id, 0) for g in current_goals
    )

    # Calculate tokens after deletion (remove only the goals being deleted)
    tokens_to_remove = sum(
        activity_token_map.get(g.activity_id, 0)
        for g in current_goals
        if g.id in request.goal_ids
    )
    tokens_after_delete = current_tokens - tokens_to_remove

    if tokens_after_delete < MIN_TOKENS:
        available_activities = (
            db.query(ActivityMaster)
            .filter(
                ActivityMaster.is_active == 1,
                ~ActivityMaster.id.in_(current_activity_ids),
            )
            .all()
        )

        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Cannot delete {len(request.goal_ids)} goals: would reduce tokens to {tokens_after_delete} (minimum {MIN_TOKENS})",
                "current_tokens": current_tokens,
                "tokens_after_deletion": tokens_after_delete,
                "minimum_required": MIN_TOKENS,
                "suggestion": f"Add activities worth {MIN_TOKENS - tokens_after_delete} tokens first",
                "available_activities": [
                    {
                        "id": a.id,
                        "activity_name": a.activity_name,
                        "token": a.base_token,
                    }
                    for a in available_activities
                ],
            },
        )

    count = repo.delete_goals_bulk(request.goal_ids)

    return {"deleted": count, "remaining_tokens": tokens_after_delete}


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

    # Check if deletion would reduce tokens below minimum
    current_goals = repo.get_user_goals(current_user.id)
    current_activity_ids = [g.activity_id for g in current_goals]

    # Calculate total tokens of current goals
    activities = (
        db.query(ActivityMaster)
        .filter(ActivityMaster.id.in_(current_activity_ids))
        .all()
    )
    activity_token_map = {a.id: a.base_token for a in activities}
    current_tokens = sum(
        activity_token_map.get(g.activity_id, 0) for g in current_goals
    )

    # Calculate tokens after deletion
    tokens_to_remove = activity_token_map.get(goal.activity_id, 0)
    tokens_after_delete = current_tokens - tokens_to_remove

    if tokens_after_delete < MIN_TOKENS:
        # Get activities not already in goals
        available_activities = (
            db.query(ActivityMaster)
            .filter(
                ActivityMaster.is_active == 1,
                ~ActivityMaster.id.in_(current_activity_ids),
            )
            .all()
        )

        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Cannot delete: would reduce tokens below {MIN_TOKENS}",
                "current_tokens": current_tokens,
                "tokens_after_deletion": tokens_after_delete,
                "minimum_required": MIN_TOKENS,
                "suggestion": "Add a replacement activity first, then delete this goal",
                "available_activities": [
                    {
                        "id": a.id,
                        "activity_name": a.activity_name,
                        "token": a.base_token,
                    }
                    for a in available_activities
                ],
            },
        )

    repo.delete_goal(goal_id)
    return {"status": "deleted", "remaining_tokens": tokens_after_delete}


@router.get("/validate")
def validate_goals(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Validate minimum token requirement"""
    repo = StudentGoalRepo(db)
    goals = repo.get_user_goals(current_user.id)

    # Calculate total tokens
    activity_ids = [g.activity_id for g in goals]
    activities = (
        db.query(ActivityMaster).filter(ActivityMaster.id.in_(activity_ids)).all()
        if activity_ids
        else []
    )
    activity_token_map = {a.id: a.base_token for a in activities}
    total_tokens = sum(activity_token_map.get(g.activity_id, 0) for g in goals)

    if total_tokens < MIN_TOKENS:
        remaining = MIN_TOKENS - total_tokens
        raise HTTPException(
            status_code=400,
            detail=f"Minimum {MIN_TOKENS} tokens required. You have {total_tokens} tokens. Add {remaining} more.",
        )

    return {
        "valid": True,
        "total_tokens": total_tokens,
        "minimum_required": MIN_TOKENS,
    }
