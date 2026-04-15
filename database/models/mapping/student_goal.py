# Student Goal - Student's self-set activity goals
from sqlalchemy import Column, Integer, SmallInteger, DateTime
from database.models.base import Base
from datetime import datetime


class StudentGoal(Base):
    __tablename__ = "student_goal"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    activity_id = Column(Integer, nullable=False)
    target_month = Column(Integer, nullable=True)
    is_active = Column(SmallInteger, default=1)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
