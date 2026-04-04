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


@router.delete("/{goal_id}")
def delete_and_create_goals(
    goal_id: int,
    request: StudentGoalDelete,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = StudentGoalRepo(db)
    old_goal = repo.get_goal_by_id(goal_id)

    if not old_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found"
        )
    if old_goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Get other active goals total
    other_goals = repo.get_user_goals(current_user.id)
    other_total = sum(
        g.target_tokens for g in other_goals if g.id != goal_id and g.is_active == 1
    )

    # Calculate new activities total
    new_total = (
        sum(a.tokens for a in request.new_activities) if request.new_activities else 0
    )

    # Validate: must have at least 16 tokens after delete
    if (other_total + new_total) < 16:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must add activities totaling at least 16 tokens",
        )

    # Delete old goal
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
                deadline=activity.deadline,  # Individual deadline
            )
            created_goals.append(goal)

        return {"deleted": True, "created": created_goals}

    return {"deleted": True}


@router.get("/all/students")
def get_all_student_goals(
    current_user=Depends(require_staff),
    db: Session = Depends(get_db),
):
    repo = StudentGoalRepo(db)
    return repo.get_all_goals()
