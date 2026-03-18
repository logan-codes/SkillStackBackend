# database/models/mapping/user_activity_mapping.py
# Tracks user progress in activities through stages

from sqlalchemy import Column, Integer, SmallInteger, DateTime, Text, String, ForeignKey
from database.models.base import Base
from datetime import datetime

class UserActivityMapping(Base):
    __tablename__ = "user_activity_mapping"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activity_master.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("status_master.id"), nullable=False)
    current_stage_id = Column(Integer, ForeignKey("stage_master.id"), nullable=True)
    proof_document = Column(String(500), nullable=True)  # File path
    ai_verification_result = Column(Text, nullable=True)  # AI feedback
    tokens_earned = Column(Integer, default=0)
    is_active = Column(SmallInteger, default=1, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
