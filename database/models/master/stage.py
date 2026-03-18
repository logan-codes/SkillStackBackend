# database/models/master/stage.py

from sqlalchemy import Column, Integer, String, SmallInteger, Boolean
from database.models.base import Base

class Stage(Base):
    __tablename__ = "stage_master"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    is_active = Column(SmallInteger, default=1, nullable=False)
    
    # Permissions
    permission_upload = Column(Boolean, default=False)
    ai_permission_verification = Column(Boolean, default=False)
    manual_permission_verification = Column(Boolean, default=False)
    event_progress = Column(Boolean, default=False)
    ai_proof_verification = Column(Boolean, default=False)
    manual_proof_verification = Column(Boolean, default=False)
    activity_completed = Column(Boolean, default=False)
