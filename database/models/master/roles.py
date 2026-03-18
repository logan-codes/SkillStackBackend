# database/models/master/roles.py

from sqlalchemy import Column, Integer, String, SmallInteger, DateTime
from database.models.base import Base
from datetime import datetime

class Role(Base):
    __tablename__ = "roles_master"
    
    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), nullable=False)  # Admin, Staff, Student
    is_active = Column(SmallInteger, default=1, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
