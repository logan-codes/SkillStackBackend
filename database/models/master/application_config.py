# Application config master model
from sqlalchemy import Column, BigInteger, String, Text, SmallInteger, DateTime
from database.models.base import Base
from datetime import datetime


class ApplicationConfig(Base):
    __tablename__ = "application_config"

    id = Column(BigInteger, primary_key=True)
    config_name = Column(String(100), nullable=False)
    config_value = Column(Text, nullable=True)
    is_active = Column(SmallInteger, default=1)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
