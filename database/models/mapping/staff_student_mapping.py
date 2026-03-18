# database/models/mapping/staff_student_mapping.py
# Staff-Student relationships (mentor, advisor, guide)

from sqlalchemy import Column, Integer, SmallInteger, DateTime, String, ForeignKey
from database.models.base import Base
from datetime import datetime, timezone

class StaffStudentMapping(Base):
    __tablename__ = "staff_student_mapping"
    
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Staff user
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Student user
    mapping_type = Column(String(50), nullable=False)  # mentor, advisor, guide
    is_active = Column(SmallInteger, default=1, nullable=False)
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
