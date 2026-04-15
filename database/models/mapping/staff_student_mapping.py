# Staff student mapping model
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime
from database.models.base import Base
from datetime import datetime


class StaffStudentMapping(Base):
    __tablename__ = "staff_student_mapping"

    id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, nullable=False)  # FK to users
    staff_role_id = Column(Integer, nullable=False)  # FK to roles
    student_id = Column(Integer, nullable=False)  # FK to users
    is_active = Column(SmallInteger, default=1)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
