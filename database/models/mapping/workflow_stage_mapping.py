# database/models/mapping/workflow_stage_mapping.py
# Links workflows to stages in sequence

from sqlalchemy import Column, Integer, SmallInteger, DateTime, ForeignKey
from database.models.base import Base
from datetime import datetime

class WorkflowStageMapping(Base):
    __tablename__ = "workflow_stage_mapping"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflow_master.id"), nullable=False)
    stage_id = Column(Integer, ForeignKey("stage_master.id"), nullable=False)
    stage_order = Column(Integer, nullable=False)  # Sequence in workflow (1, 2, 3...)
    is_active = Column(SmallInteger, default=1, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
