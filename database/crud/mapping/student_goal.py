# Student Goal CRUD operations
from sqlalchemy.orm import Session
from database.models.mapping.student_goal import StudentGoal
from typing import List, Optional
from datetime import datetime


class StudentGoalRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_user_goals(self, user_id: int) -> List[StudentGoal]:
        return (
            self.db.query(StudentGoal)
            .filter(StudentGoal.user_id == user_id, StudentGoal.is_active == 1)
            .all()
        )

    def get_goal_by_id(self, goal_id: int) -> Optional[StudentGoal]:
        return (
            self.db.query(StudentGoal)
            .filter(StudentGoal.id == goal_id, StudentGoal.is_active == 1)
            .first()
        )

    def get_goal_by_name(self, user_id: int, goal_name: str) -> Optional[StudentGoal]:
        return (
            self.db.query(StudentGoal)
            .filter(
                StudentGoal.user_id == user_id,
                StudentGoal.goal_name == goal_name,
                StudentGoal.is_active == 1,
            )
            .first()
        )

    def create_goal(
        self,
        user_id: int,
        activity_id: int,
        goal_name: str,
        target_tokens: int,
        deadline=None,
        status_id: int = 1,
    ) -> StudentGoal:
        goal = StudentGoal(
            user_id=user_id,
            activity_id=activity_id,
            goal_name=goal_name,
            target_tokens=target_tokens,
            current_tokens=0,
            deadline=deadline,
            status_id=status_id,
            is_active=1,
        )
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def update_goal(
        self,
        goal_id: int,
        goal_name=None,
        target_tokens=None,
        current_tokens=None,
        deadline=None,
        status_id=None,
    ) -> StudentGoal:
        goal = self.get_goal_by_id(goal_id)
        if not goal:
            return None
        if goal_name is not None:
            goal.goal_name = goal_name
        if target_tokens is not None:
            goal.target_tokens = target_tokens
        if current_tokens is not None:
            goal.current_tokens = current_tokens
        if deadline is not None:
            goal.deadline = deadline
        if status_id is not None:
            goal.status_id = status_id
        goal.updated_date = datetime.now()
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def delete_goal(self, goal_id: int) -> bool:
        goal = self.get_goal_by_id(goal_id)
        if not goal:
            return False
        goal.is_active = 0
        goal.updated_date = datetime.now()
        self.db.commit()
        return True

    def get_all_goals(self) -> List[StudentGoal]:
        return self.db.query(StudentGoal).filter(StudentGoal.is_active == 1).all()

    # For lazy loading / pagination
    def get_user_goals_paginated(
        self, user_id: int, skip: int = 0, limit: int = 10
    ) -> List[StudentGoal]:
        return (
            self.db.query(StudentGoal)
            .filter(StudentGoal.user_id == user_id, StudentGoal.is_active == 1)
            .offset(skip)
            .limit(limit)
            .all()
        )

    # Count total goals (for checking if more data exists)
    def count_user_goals(self, user_id: int) -> int:
        return (
            self.db.query(StudentGoal)
            .filter(StudentGoal.user_id == user_id, StudentGoal.is_active == 1)
            .count()
        )
