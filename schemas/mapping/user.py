# User schemas for API validation
from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    email_id: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    id: int
    name: Optional[str] = None
    email_id: str
    role_id: Optional[int] = None
    is_active: int

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class RegisterRequest(BaseModel):
    email_id: EmailStr
    name: str
    role_id: int
    gender_id: int
    password: str


class StudentProfileUpdate(BaseModel):
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    leetcode_url: Optional[str] = None
    codeforces_url: Optional[str] = None
    hackerrank_url: Optional[str] = None


class LeaderboardEntry(BaseModel):
    rank: int
    student_id: int
    name: str
    register_no: Optional[int] = None
    section: Optional[str] = None
    department: Optional[str] = None
    year: Optional[str] = None
    total_tokens: int

    class Config:
        from_attributes = True


class LeaderboardResponse(BaseModel):
    leaderboard: list[LeaderboardEntry]
    total_count: int
    user_rank: Optional[int] = None
