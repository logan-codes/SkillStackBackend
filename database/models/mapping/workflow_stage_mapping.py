# Workflow stage mapping model
from sqlalchemy import Column, Integer, ForeignKey
from database.models.base import Base


class WorkflowStageMapping(Base):
    __tablename__ = "workflow_stage_mapping"

    workflow_id = Column(Integer, ForeignKey("workflow_master.id"), nullable=False)
    stage_id = Column(Integer, ForeignKey("stage_master.id"), nullable=False)
    stage_order = Column(Integer, nullable=False)
