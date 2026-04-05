# Student Goal - User's selected goals (links to student_goal_master)
from sqlalchemy import Column, Integer, Date, String, ForeignKey, SmallInteger, DateTime
from sqlalchemy.orm import relationship
from database.models.base import Base
from datetime import datetime


class StudentGoal(Base):
    __tablename__ = "student_goal"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("student_goal_master.id"), nullable=False)
    goal_name = Column(String(200), nullable=False)
    target_tokens = Column(Integer, nullable=False)
    current_tokens = Column(Integer, default=0)
    deadline = Column(Date, nullable=True)
    is_active = Column(SmallInteger, default=1)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
