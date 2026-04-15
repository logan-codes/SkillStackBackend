# Student Goal Master - Activities for student goals (16+ token selection)
# Note: student_goal_master table doesn't exist in PostgreSQL
from sqlalchemy import Column, Integer, String, Text, ForeignKey, SmallInteger
from database.models.base import Base


class StudentGoalMaster(Base):
    __tablename__ = "student_goal_master"

    id = Column(Integer, primary_key=True, index=True)
    activity_name = Column(String(200), nullable=False)
    activity_type_id = Column(
        Integer, ForeignKey("activity_type_master.id"), nullable=True
    )
    description = Column(Text, nullable=True)
    token = Column(Integer, default=0)
    workflow_id = Column(Integer, ForeignKey("workflow.id"), nullable=True)
    is_active = Column(SmallInteger, default=1)
