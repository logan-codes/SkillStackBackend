# schemas/mapping/user_social_links.py
# User Social Links schemas - request/response validation

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserSocialLinkBase(BaseModel):
    platform: str
    profile_url: str


class UserSocialLinkCreate(UserSocialLinkBase):
    pass


class UserSocialLinkUpdate(BaseModel):
    platform: Optional[str] = None
    profile_url: Optional[str] = None


class UserSocialLinkResponse(UserSocialLinkBase):
    id: int
    user_id: int
    is_active: int
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserSocialLinksResponse(BaseModel):
    github: Optional[str] = None
    linkedin: Optional[str] = None
    leetcode: Optional[str] = None
    hackerrank: Optional[str] = None
    codechef: Optional[str] = None
