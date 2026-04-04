# Student Goal model
from sqlalchemy import Column, Integer, Date, String, ForeignKey
from database.models.base import Base


class StudentGoal(Base):
    __tablename__ = "student_goal"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_name = Column(String(200), nullable=False)
    target_tokens = Column(Integer, nullable=False)
    current_tokens = Column(Integer, default=0)
    deadline = Column(Date, nullable=True)
    status_id = Column(Integer, ForeignKey("status_master.id"), nullable=False)
