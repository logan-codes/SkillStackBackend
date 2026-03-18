# database/models/mapping/activity.py
# Activity Master - stores different activities with tokens and workflow

from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, Text, ForeignKey
from database.models.base import Base
from datetime import datetime, timezone

class Activity(Base):
    __tablename__ = "activity_master"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_name = Column(String(200), nullable=False)  # e.g., "Hackathon", "Workshop"
    activity_limit = Column(Integer, nullable=True)  # Max activities per student
    activity_type_id = Column(Integer, ForeignKey("activity_type_master.id"), nullable=True)  # FK to ActivityType
    description = Column(Text, nullable=True)
    token = Column(Integer, default=0)  # Token reward for completing activity
    workflow_id = Column(Integer, ForeignKey("workflow_master.id"), nullable=True)  # FK to Workflow
    is_active = Column(SmallInteger, default=1, nullable=False)
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
