# Student Goal endpoints - CRUD operations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.init_db import get_db
from database.crud.mapping.student_goal import StudentGoalRepo
from schemas.mapping.student_goal import (
    StudentGoalCreate,
    StudentGoalUpdate,
    StudentGoalResponse,
)
from core.auth import get_current_user, require_staff

router = APIRouter()


@router.get("/", response_model=List[StudentGoalResponse])
def get_my_goals(
    skip: int = 0,
    limit: int = 10,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = StudentGoalRepo(db)
    return repo.get_user_goals_paginated(current_user.id, skip=skip, limit=limit)


@router.post(
    "/", response_model=StudentGoalResponse, status_code=status.HTTP_201_CREATED
)
def create_goal(
    request: StudentGoalCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = StudentGoalRepo(db)
    return repo.create_goal(
        user_id=current_user.id,
        goal_name=request.goal_name,
        target_tokens=request.target_tokens,
        deadline=request.deadline,
    )


@router.put("/{goal_id}", response_model=StudentGoalResponse)
def update_goal(
    goal_id: int,
    request: StudentGoalUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = StudentGoalRepo(db)
    goal = repo.get_goal_by_id(goal_id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found"
        )
    if goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    return repo.update_goal(
        goal_id=goal_id,
        goal_name=request.goal_name,
        target_tokens=request.target_tokens,
        current_tokens=request.current_tokens,
        deadline=request.deadline,
        status_id=request.status_id,
    )


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    repo = StudentGoalRepo(db)
    goal = repo.get_goal_by_id(goal_id)
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found"
        )
    if goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    repo.delete_goal(goal_id)
    return None


@router.get("/all/students")
def get_all_student_goals(
    skip: int = 0,
    limit: int = 10,
    current_user=Depends(require_staff),
    db: Session = Depends(get_db),
):
    repo = StudentGoalRepo(db)
    return repo.get_all_goals()
