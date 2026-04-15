# Program/Department master model
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime
from database.models.base import Base
from datetime import datetime


class ProgramDeptMaster(Base):
    __tablename__ = "program_dept_master"

    id = Column(Integer, primary_key=True)
    program = Column(String(50), nullable=False)  # B.E, B.Tech, M.E, MBA, Ph.D
    branch = Column(String(100), nullable=False)
    is_active = Column(SmallInteger, default=1)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
