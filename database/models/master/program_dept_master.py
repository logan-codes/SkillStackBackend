# Program/Department master model
from sqlalchemy import Column, String
from database.models.base import Base


class ProgramDeptMaster(Base):
    __tablename__ = "program_dept_master"

    program = Column(String(100), nullable=False)
    branch = Column(String(100), nullable=False)
