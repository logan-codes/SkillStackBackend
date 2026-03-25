# database/models/mapping/staff_student_mapping.py
# TODO: Implement StaffStudentMapping model
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime

class StaffStudentMapping():
    __tablename__ = "staff_student_mapping"
    
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, nullable=False)  # Foreign key to staff table
    staff_role_id = Column(Integer, nullable=False)  # Foreign key to staff_role_master table
    student_id = Column(Integer, nullable=False)  # Foreign key to student table
    is_active = Column(Integer, default=1, nullable=False)
    created_date = Column(DateTime, default=datetime.now(datetime.timezone.utc))
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
