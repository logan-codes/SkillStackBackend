# User activity schemas
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserActivityStart(BaseModel):
    custom_name: str
    permission_proof: Optional[str] = None


class UserActivityProof(BaseModel):
    proof: str
    proof_description: Optional[str] = None


class UserActivityUpdateName(BaseModel):
    custom_name: str


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
    ai_verification_result: Optional[str]
    tokens_earned: int
    created_at: datetime

    class Config:
        from_attributes = True
