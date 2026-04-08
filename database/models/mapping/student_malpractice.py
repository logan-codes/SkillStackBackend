# Student Malpractice - Track malpractice incidents
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, SmallInteger
from database.models.base import Base
from datetime import datetime


class StudentMalpractice(Base):
    __tablename__ = "student_malpractice"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    malpractice_id = Column(
        Integer, ForeignKey("malpractice_master.id"), nullable=False
    )
    token_deducted = Column(Integer, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(String(500), nullable=True)
    is_reversed = Column(SmallInteger, default=0)
    created_date = Column(DateTime, default=datetime.utcnow)
