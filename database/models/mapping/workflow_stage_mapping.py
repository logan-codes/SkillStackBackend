# Workflow Stage Mapping - Ordered stages within a workflow
from sqlalchemy import Column, Integer, SmallInteger, DateTime, UniqueConstraint
from database.models.base import Base
from datetime import datetime


class WorkflowStageMapping(Base):
    __tablename__ = "workflow_stage_mapping"
    __table_args__ = (UniqueConstraint("workflow_id", "stage_order"),)

    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, nullable=False)  # FK to workflow
    stage_order = Column(Integer, nullable=False)
    stage_id = Column(Integer, nullable=False)  # FK to stage
    is_active = Column(SmallInteger, default=1)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
