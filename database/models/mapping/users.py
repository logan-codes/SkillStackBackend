# User model - Unified table for students and staff
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Numeric,
    SmallInteger,
    DateTime,
    BigInteger,
)
from database.models.base import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    role_id = Column(BigInteger, nullable=False)
    gender_id = Column(SmallInteger, nullable=False)
    register_no = Column(Integer, unique=True, nullable=True)
    staff_id = Column(String(20), unique=True, nullable=True)
    program_dept_id = Column(BigInteger, nullable=True)
    year = Column(SmallInteger, nullable=True)
    semester = Column(SmallInteger, nullable=True)
    cgpa = Column(Numeric(3, 2), nullable=True)
    batch_start_year = Column(SmallInteger, nullable=True)
    batch_end_year = Column(SmallInteger, nullable=True)
    email_id = Column(String(100), unique=True, nullable=False)
    contact_no = Column(String(15), nullable=True)
    name = Column(String(100), nullable=False)
    nationality = Column(String(50), nullable=True)
    mother_tongue = Column(String(50), nullable=True)
    religion = Column(String(50), nullable=True)
    community = Column(String(50), nullable=True)
    blood_grp = Column(String(5), nullable=True)
    birthdate = Column(Date, nullable=True)
    total_tokens = Column(Integer, default=0)
    is_active = Column(SmallInteger, default=1)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
