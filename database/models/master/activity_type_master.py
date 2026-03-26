# database/models/master/activity_type_master.py

from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, Text, ForeignKey
from database.models.base import Base
from datetime import datetime, timezone

class ActivityTypeMaster(Base):
    __tablename__ = "activity_type_master"
    
    id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String(100), nullable=False)  # e.g., "Workshop", "Seminar"
    is_active = Column(SmallInteger, default=1, nullable=False)
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
