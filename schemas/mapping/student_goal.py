# Student Goal schemas
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


class PlannedActivity(BaseModel):
    activity_id: int
    activity_name: str
    tokens: int
    deadline: Optional[date] = None


class StudentGoalCreate(BaseModel):
    activities: List[PlannedActivity]
    deadline: Optional[date] = None  # Optional common deadline


class StudentGoalDelete(BaseModel):
    new_activities: Optional[List[PlannedActivity]] = None


class StudentGoalResponse(BaseModel):
    id: int
    user_id: int
    activity_id: int
    goal_name: str
    target_tokens: int
    current_tokens: int
    deadline: Optional[date] = None
    is_active: int
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None

    class Config:
        from_attributes = True
