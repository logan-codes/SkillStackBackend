# Activity Master - Generic activities for workflow
from sqlalchemy import Column, Integer, String, Text, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship
from database.models.base import Base


class ActivityMaster(Base):
    __tablename__ = "activity_master"

    id = Column(Integer, primary_key=True, index=True)
    activity_name = Column(String(200), nullable=False)
    activity_type_id = Column(
        Integer, ForeignKey("activity_type_master.id"), nullable=True
    )
    is_active = Column(SmallInteger, default=1)

    student_goal_mappings = relationship(
        "ActivityStudentGoalMapping", back_populates="activity"
    )
