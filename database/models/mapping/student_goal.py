# database/models/mapping/student_goal.py
# Student goals and targets

from sqlalchemy import Column, Integer, SmallInteger, DateTime, Date, String, ForeignKey
from database.models.base import Base
from datetime import datetime, timezone

class StudentGoal(Base):
    __tablename__ = "student_goal"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_name = Column(String(200), nullable=False)
    target_tokens = Column(Integer, nullable=False)
    current_tokens = Column(Integer, default=0)
    deadline = Column(Date, nullable=True)
    status_id = Column(Integer, ForeignKey("status_master.id"), nullable=False)
    is_active = Column(SmallInteger, default=1, nullable=False)
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
