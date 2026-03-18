# database/models/master/status.py

from sqlalchemy import Column, Integer, String, SmallInteger, DateTime
from database.models.base import Base
from datetime import datetime

class Status(Base):
    __tablename__ = "status_master"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)  # Yet To Start, In Progress, Completed, Failure
    is_active = Column(SmallInteger, default=1, nullable=False)
