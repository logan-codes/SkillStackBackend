# Student Malpractice schemas
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MalpracticeApply(BaseModel):
    malpractice_id: int
    description: Optional[str] = None


class MalpracticeReverse(BaseModel):
    record_ids: List[int]


class StudentMalpracticeResponse(BaseModel):
    id: int
    student_id: int
    malpractice_id: int
    token_deducted: int
    teacher_id: int
    description: Optional[str]
    is_reversed: int
    created_date: datetime
    malpractice_name: str

    class Config:
        from_attributes = True
