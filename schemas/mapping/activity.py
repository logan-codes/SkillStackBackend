# Activity schemas
from pydantic import BaseModel
from typing import Optional


class ActivityBase(BaseModel):
    activity_name: str
    activity_limit: Optional[int] = None
    description: Optional[str] = None
    token: int = 0


class ActivityCreate(ActivityBase):
    activity_type_id: Optional[int] = None
    workflow_id: Optional[int] = None


class ActivityUpdate(BaseModel):
    activity_name: Optional[str] = None
    activity_limit: Optional[int] = None
    description: Optional[str] = None
    token: Optional[int] = None


class ActivityResponse(ActivityBase):
    id: int
    activity_type_id: Optional[int] = None
    workflow_id: Optional[int] = None
    is_active: int

    class Config:
        from_attributes = True
