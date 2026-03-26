# database/models/master/application_config.py

from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, Text
from database.models.base import Base
from datetime import datetime, timezone

class ApplicationConfig(Base):
    __tablename__ = "application_config"
    
    id = Column(Integer, primary_key=True, index=True)
    config_name = Column(String(100), nullable=False)
    config_value = Column(Text, nullable=True)
    is_active = Column(SmallInteger, default=1, nullable=False)
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
