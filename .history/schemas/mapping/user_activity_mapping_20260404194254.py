# User activity schemas
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class UserActivityStart(BaseModel):
    custom_name: str
    permission_proof: Optional[str] = None
    deadline: Optional[date] = None


class UserActivityProof(BaseModel):
    proof: str
    proof_description: Optional[str] = None


class UserActivityUpdate(BaseModel):
    custom_name: Optional[str] = None
    deadline: Optional[date] = None
    permission_proof: Optional[str] = None
    description: Optional[str] = None


class UserActivityResponse(BaseModel):
    id: int
    user_id: int
    activity_id: int
    custom_name: Optional[str]
    status_id: int
    current_stage_id: Optional[int]
    proof_document: Optional[str]
    proof_description: Optional[str]
    permission_proof: Optional[str]
    deadline: Optional[date]
    ai_verification_result: Optional[str]
    tokens_earned: int
    created_date: Optional[datetime]
    updated_date: Optional[datetime]

    class Config:
        from_attributes = True
