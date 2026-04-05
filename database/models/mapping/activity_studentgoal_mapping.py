# Activity Student Goal Mapping - Maps generic activities to goal activities
from sqlalchemy import Column, Integer, String, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship
from database.models.base import Base


class ActivityStudentGoalMapping(Base):
    __tablename__ = "activity_studentgoalmapping"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activity_master.id"), nullable=False)
    student_goal_id = Column(
        Integer, ForeignKey("student_goal_master.id"), nullable=False
    )
    is_active = Column(SmallInteger, default=1)

    # Relationships - reference master tables
    activity = relationship("ActivityMaster", back_populates="student_goal_mappings")
    student_goal_master = relationship(
        "StudentGoalMaster", back_populates="activity_mappings"
    )
