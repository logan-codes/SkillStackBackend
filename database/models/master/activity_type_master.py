# Activity type master model
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime
from database.models.base import Base
from datetime import datetime


class ActivityTypeMaster(Base):
    __tablename__ = "activity_type_master"

    id = Column(Integer, primary_key=True)
    type_name = Column(String(100), nullable=False)
    is_active = Column(SmallInteger, default=1)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
