# api/v1/endpoints/mapping/student_goal.py
# Student Goal endpoints - CRUD operations for student goals

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database.init_db import get_db
from database.crud.mapping.student_goal import StudentGoalRepo
from schemas.mapping.student_goal import (
    StudentGoalCreate,
    StudentGoalUpdate,
    StudentGoalResponse
)
from core.auth import get_current_user, require_staff

router = APIRouter()


# ──────────────────────────────────────────────────────────────
# STUDENT ROUTES — any authenticated user
# ──────────────────────────────────────────────────────────────

@router.get("/", response_model=List[StudentGoalResponse])
def get_my_goals(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's goals.
    """
    repo = StudentGoalRepo(db)
    goals = repo.get_user_goals(current_user.id)
    return goals


@router.get("/{goal_id}", response_model=StudentGoalResponse)
def get_my_goal(
    goal_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific goal by ID.
    Only returns goal if it belongs to current user.
    """
    repo = StudentGoalRepo(db)
    goal = repo.get_goal_by_id(goal_id)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    # Check if goal belongs to current user
    if goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this goal"
        )
    
    return goal


@router.post("/", response_model=StudentGoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    request: StudentGoalCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new goal for the current user.
    """
    repo = StudentGoalRepo(db)
    
    # Check if goal with same name exists
    existing = repo.get_goal_by_name(current_user.id, request.goal_name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Goal with this name already exists"
        )
    
    # Create goal
    goal = repo.create_goal(
        user_id=current_user.id,
        goal_name=request.goal_name,
        target_tokens=request.target_tokens,
        deadline=request.deadline
    )
    
    return goal


@router.put("/{goal_id}", response_model=StudentGoalResponse)
def update_goal(
    goal_id: int,
    request: StudentGoalUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing goal.
    Only the goal owner can update.
    """
    repo = StudentGoalRepo(db)
    goal = repo.get_goal_by_id(goal_id)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    if goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this goal"
        )
    
    # Update goal
    updated_goal = repo.update_goal(
        goal_id=goal_id,
        goal_name=request.goal_name,
        target_tokens=request.target_tokens,
        current_tokens=request.current_tokens,
        deadline=request.deadline,
        status_id=request.status_id
    )
    
    return updated_goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a goal (soft delete).
    Only the goal owner can delete.
    """
    repo = StudentGoalRepo(db)
    goal = repo.get_goal_by_id(goal_id)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    if goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this goal"
        )
    
    repo.delete_goal(goal_id)
    return None


# ──────────────────────────────────────────────────────────────
# STAFF ROUTES — staff and admin only
# ──────────────────────────────────────────────────────────────

@router.get("/all/students")
def get_all_student_goals(
    current_user = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """
    Get all student goals (Staff/Admin only).
    """
    repo = StudentGoalRepo(db)
    goals = repo.get_all_goals()
    return goals
