# database/models/master/program_dept_master.py

from sqlalchemy import Column, Integer, String, SmallInteger, DateTime
from database.models.base import Base
from datetime import datetime, timezone

class ProgramDeptMaster(Base):
    __tablename__ = "program_dept_master"
    
    id = Column(Integer, primary_key=True, index=True)
    program = Column(String(100), nullable=False)  # e.g., B.Tech, M.Tech
    branch = Column(String(100), nullable=False)     # e.g., Computer Science, Electronics
    is_active = Column(SmallInteger, default=1, nullable=False)
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
