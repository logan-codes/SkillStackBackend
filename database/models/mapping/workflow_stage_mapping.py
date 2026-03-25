# database/models/mapping/workflow_stage_mapping.py
# TODO: Implement WorkflowStageMapping model
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime

class WorkflowStageMapping():
    __tablename__ = "workflow_stage_mapping"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, nullable=False)  # Foreign key to workflow_master table
    stage_id = Column(Integer, nullable=False)  # Foreign key to stage_master table
    is_active = Column(Integer, default=1, nullable=False)
    created_date = Column(DateTime, default=datetime.now(datetime.timezone.utc))
    updated_date = Column(DateTime, default=datetime.now(datetime.timezone.utc), onupdate=datetime.now(datetime.timezone.utc))
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
