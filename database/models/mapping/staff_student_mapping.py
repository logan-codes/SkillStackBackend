# Staff student mapping model
from sqlalchemy import Column, Integer, String, ForeignKey
from database.models.base import Base


class StaffStudentMapping(Base):
    __tablename__ = "staff_student_mapping"

    staff_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    section = Column(String(5), nullable=True)
    mapping_type = Column(String(50), nullable=False)
