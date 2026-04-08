# User activity schemas
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class UserActivityStart(BaseModel):
    custom_name: str
    permission_proof: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class UserActivityProof(BaseModel):
    proof: str
    proof_description: Optional[str] = None
    student_goal_id: int


class UserActivityUpdate(BaseModel):
    custom_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    permission_proof: Optional[str] = None
    proof_description: Optional[str] = None


class TeacherReviewRequest(BaseModel):
    action: str
    reason: Optional[str] = None


class UserActivityResponse(BaseModel):
    id: int
    user_id: int
    activity_id: int
    student_goal_id: Optional[int] = None
    custom_name: Optional[str]
    status_id: int
    current_stage_id: Optional[int]
    proof_document: Optional[str]
    proof_description: Optional[str]
    permission_proof: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    ai_verification_result: Optional[str]
    tokens_earned: int
    is_active: int
    created_date: Optional[datetime]
    updated_date: Optional[datetime]
    rejection_reason: Optional[str] = None
    submission_count: int = 0
    is_locked: int = 0
    is_completed: int = 0
    is_deleted: int = 0

    class Config:
        from_attributes = True
