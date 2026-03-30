# database/crud/mapping/student_goal.py
# Student Goal CRUD operations

from sqlalchemy.orm import Session
from database.models.mapping.student_goal import StudentGoal
from typing import List, Optional
from datetime import datetime


class StudentGoalRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_goals(self, user_id: int) -> List[StudentGoal]:
        """Get all goals for a specific user"""
        return self.db.query(StudentGoal).filter(
            StudentGoal.user_id == user_id,
            StudentGoal.is_active == 1
        ).all()
    
    def get_goal_by_id(self, goal_id: int) -> Optional[StudentGoal]:
        """Get a specific goal by ID"""
        return self.db.query(StudentGoal).filter(
            StudentGoal.id == goal_id,
            StudentGoal.is_active == 1
        ).first()
    
    def get_goal_by_name(self, user_id: int, goal_name: str) -> Optional[StudentGoal]:
        """Check if goal with same name exists for user"""
        return self.db.query(StudentGoal).filter(
            StudentGoal.user_id == user_id,
            StudentGoal.goal_name == goal_name,
            StudentGoal.is_active == 1
        ).first()
    
    def create_goal(
        self,
        user_id: int,
        goal_name: str,
        target_tokens: int,
        deadline=None,
        status_id: int = 1  # Default to "Yet to Start"
    ) -> StudentGoal:
        """Create a new goal"""
        goal = StudentGoal(
            user_id=user_id,
            goal_name=goal_name,
            target_tokens=target_tokens,
            current_tokens=0,
            deadline=deadline,
            status_id=status_id,
            is_active=1
        )
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal
    
    def update_goal(
        self,
        goal_id: int,
        goal_name: str = None,
        target_tokens: int = None,
        current_tokens: int = None,
        deadline=None,
        status_id: int = None
    ) -> StudentGoal:
        """Update an existing goal"""
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
        """Soft delete a goal"""
        goal = self.get_goal_by_id(goal_id)
        if not goal:
            return False
        
        goal.is_active = 0
        goal.updated_date = datetime.now()
        self.db.commit()
        return True
    
    def get_all_goals(self) -> List[StudentGoal]:
        """Get all goals (for staff/admin)"""
        return self.db.query(StudentGoal).filter(
            StudentGoal.is_active == 1
        ).all()
