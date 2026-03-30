# schemas/mapping/student_goal.py
# Student Goal schemas - request/response validation

from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class StudentGoalBase(BaseModel):
    goal_name: str
    target_tokens: int


class StudentGoalCreate(StudentGoalBase):
    deadline: Optional[date] = None


class StudentGoalUpdate(BaseModel):
    goal_name: Optional[str] = None
    target_tokens: Optional[int] = None
    current_tokens: Optional[int] = None
    deadline: Optional[date] = None
    status_id: Optional[int] = None


class StudentGoalResponse(StudentGoalBase):
    id: int
    user_id: int
    current_tokens: int
    deadline: Optional[date] = None
    status_id: int
    is_active: int
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True
