# database/models/master/gender.py

from sqlalchemy import Column, Integer, String, SmallInteger, DateTime
from database.models.base import Base
from datetime import datetime

class Gender(Base):
    __tablename__ = "gender_master"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)  # Male, Female, Other
    is_active = Column(SmallInteger, default=1, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
