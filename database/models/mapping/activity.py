# Activity model
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database.models.base import Base


class Activity(Base):
    __tablename__ = "activity_master"

    activity_name = Column(String(200), nullable=False)
    activity_limit = Column(Integer, nullable=True)
    activity_type_id = Column(
        Integer, ForeignKey("activity_type_master.id"), nullable=True
    )
    description = Column(Text, nullable=True)
    token = Column(Integer, default=0)
    workflow_id = Column(Integer, ForeignKey("workflow_master.id"), nullable=True)
