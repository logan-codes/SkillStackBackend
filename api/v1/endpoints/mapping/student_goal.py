# Student Goal endpoints - CREATE, DELETE, VIEW only
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.init_db import get_db
from database.crud.mapping.student_goal import StudentGoalRepo
from schemas.mapping.student_goal import (
    StudentGoalCreate,
    StudentGoalDelete,
    PlannedActivity,
    StudentGoalResponse,
)
from core.auth import get_current_user, require_staff

router = APIRouter()


@router.get("/activities", response_model=List[dict])
def get_available_activities_for_goals(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all activities available for student goals"""
    from database.models.master.student_goal_master import StudentGoalMaster

    activities = (
        db.query(StudentGoalMaster).filter(StudentGoalMaster.is_active == 1).all()
    )
    return [
        {"id": a.id, "activity_name": a.activity_name, "token": a.token}
        for a in activities
    ]


@router.get("/", response_model=List[StudentGoalResponse])
def get_my_goals(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = StudentGoalRepo(db)
    return repo.get_user_goals(current_user.id)


@router.post(
    "/", response_model=List[StudentGoalResponse], status_code=status.HTTP_201_CREATED
)
def create_goals(
    request: StudentGoalCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = StudentGoalRepo(db)

    # Calculate total tokens from activities
    total_tokens = sum(a.tokens for a in request.activities)
    if total_tokens < 16:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Minimum 16 tokens required"
        )

    # Create separate goal for each activity
    goals = []
    for activity in request.activities:
        goal = repo.create_goal(
            user_id=current_user.id,
            activity_id=activity.activity_id,
            goal_name=activity.activity_name,
            target_tokens=activity.tokens,
            deadline=activity.deadline,  # Individual deadline
        )
        goals.append(goal)

    return goals


@router.delete("/")
def delete_and_create_goals(
    request: StudentGoalDelete,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete multiple goals and optionally create new ones in a single request.

    Request body:
    {
        "goal_ids": [1, 2, 3],  // List of goal IDs to delete
        "new_activities": [...]   // Optional: new activities to create
    }
    """
    repo = StudentGoalRepo(db)

    # Get goal_ids from request - support both single goal_id and list
    goal_ids = getattr(request, "goal_ids", None)

    # If no goal_ids in request, check if it's using old format with new_activities only
    # This handles backward compatibility
    if goal_ids is None:
        # If new_activities provided without goal_ids, return error
        if request.new_activities is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide goal_ids to delete",
            )
        # Old format - single goal deletion with replacement
        goal_ids = []

    # Validate all goal_ids belong to user
    for goal_id in goal_ids:
        goal = repo.get_goal_by_id(goal_id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Goal {goal_id} not found",
            )
        if goal.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for goal {goal_id}",
            )

    # Get other active goals total (excluding the ones being deleted)
    all_goals = repo.get_user_goals(current_user.id)
    other_goals = [g for g in all_goals if g.id not in goal_ids]
    other_total = sum(g.target_tokens for g in other_goals)

    # Calculate new activities total
    new_total = (
        sum(a.tokens for a in request.new_activities) if request.new_activities else 0
    )

    # Validate: must have at least 16 tokens after delete
    if (other_total + new_total) < 16:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must maintain at least 16 tokens total",
        )

    # Delete all specified goals
    for goal_id in goal_ids:
        repo.delete_goal(goal_id)

    # Create new goals if activities provided
    created_goals = []
    if request.new_activities:
        for activity in request.new_activities:
            goal = repo.create_goal(
                user_id=current_user.id,
                activity_id=activity.activity_id,
                goal_name=activity.activity_name,
                target_tokens=activity.tokens,
                deadline=activity.deadline,
            )
            created_goals.append(goal)

    return {
        "deleted_count": len(goal_ids),
        "deleted_ids": goal_ids,
        "created": created_goals,
    }


@router.get("/all/students")
def get_all_student_goals(
    current_user=Depends(require_staff),
    db: Session = Depends(get_db),
):
    repo = StudentGoalRepo(db)
    return repo.get_all_goals()
