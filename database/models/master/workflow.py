# Workflow master model
from sqlalchemy import Column, SmallInteger, String, DateTime
from database.models.base import Base
from datetime import datetime


class Workflow(Base):
    __tablename__ = "workflow"

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    is_active = Column(SmallInteger, default=1)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(SmallInteger, nullable=True)
    updated_by = Column(SmallInteger, nullable=True)
