# Student Goal Master - Activities for student goals (16+ token selection)
from sqlalchemy import Column, Integer, String, Text, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship
from database.models.base import Base


class StudentGoalMaster(Base):
    __tablename__ = "student_goal_master"

    id = Column(Integer, primary_key=True, index=True)
    activity_name = Column(String(200), nullable=False)
    activity_limit = Column(Integer, nullable=True)
    activity_type_id = Column(
        Integer, ForeignKey("activity_type_master.id"), nullable=True
    )
    description = Column(Text, nullable=True)
    token = Column(Integer, default=0)
    workflow_id = Column(Integer, ForeignKey("workflow_master.id"), nullable=True)
    is_active = Column(SmallInteger, default=1)

    # Relationship to mapping table
    activity_mappings = relationship(
        "ActivityStudentGoalMapping", back_populates="student_goal_master"
    )
