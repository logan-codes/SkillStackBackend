# Activity Student Goal Mapping - Maps generic activities to goal activities
# Note: activity_studentgoalmapping table doesn't exist in PostgreSQL
from sqlalchemy import Column, Integer, String, ForeignKey, SmallInteger
from database.models.base import Base


class ActivityStudentGoalMapping(Base):
    __tablename__ = "activity_studentgoalmapping"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activity.id"), nullable=False)
    student_goal_id = Column(
        Integer, ForeignKey("student_goal_master.id"), nullable=False
    )
    is_active = Column(SmallInteger, default=1)
