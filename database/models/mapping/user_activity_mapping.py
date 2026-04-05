# User activity mapping model
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    ForeignKey,
    SmallInteger,
    DateTime,
)
from database.models.base import Base
from datetime import datetime


class UserActivityMapping(Base):
    __tablename__ = "user_activity_mapping"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activity_master.id"), nullable=False)
    student_goal_id = Column(
        Integer, ForeignKey("student_goal_master.id"), nullable=True
    )
    status_id = Column(Integer, ForeignKey("status_master.id"), nullable=False)
    current_stage_id = Column(Integer, ForeignKey("stage_master.id"), nullable=True)
    proof_document = Column(String(500), nullable=True)
    proof_description = Column(String(255), nullable=True)
    custom_name = Column(String(200), nullable=True)
    permission_proof = Column(String(500), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    ai_verification_result = Column(Text, nullable=True)
    tokens_earned = Column(Integer, default=0)
    is_active = Column(SmallInteger, default=1)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
