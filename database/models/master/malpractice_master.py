# database/models/master/malpractice_master.py

from sqlalchemy import Column, Integer, String, SmallInteger, DateTime
from database.models.base import Base
from datetime import datetime, timezone

class MalpracticeMaster(Base):
    __tablename__ = "malpractice_master"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)  # e.g., "Plagiarism", "Copying"
    token_deduction = Column(Integer, default=0)  # Tokens to deduct
    is_active = Column(SmallInteger, default=1, nullable=False)
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
