# Stage master model
from sqlalchemy import Column, String, Boolean
from database.models.base import Base


class Stage(Base):
    __tablename__ = "stage_master"

    name = Column(String(100), nullable=False)
    permission_upload = Column(Boolean, default=False)
    ai_permission_verification = Column(Boolean, default=False)
    manual_permission_verification = Column(Boolean, default=False)
    event_progress = Column(Boolean, default=False)
    ai_proof_verification = Column(Boolean, default=False)
    manual_proof_verification = Column(Boolean, default=False)
    activity_completed = Column(Boolean, default=False)
