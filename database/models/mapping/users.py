# User model
from sqlalchemy import Column, Integer, BigInteger, SmallInteger, String, Date, Numeric
from database.models.base import Base


class User(Base):
    __tablename__ = "users"

    role_id = Column(BigInteger, nullable=False)
    gender_id = Column(SmallInteger, nullable=False)
    register_no = Column(Integer, nullable=True)
    staff_id = Column(String(20), nullable=True)
    program_dept_id = Column(BigInteger, nullable=True)
    year = Column(SmallInteger, nullable=True)
    semester = Column(SmallInteger, nullable=True)
    cgpa = Column(Numeric(3, 2), nullable=True)
    batch_start_year = Column(SmallInteger, nullable=True)
    batch_end_year = Column(SmallInteger, nullable=True)
    email_id = Column(String(100), unique=True, index=True, nullable=False)
    contact_no = Column(String(15), nullable=True)
    name = Column(String(100), nullable=False)
    nationality = Column(String(50), nullable=True)
    mother_tongue = Column(String(50), nullable=True)
    religion = Column(String(50), nullable=True)
    community = Column(String(50), nullable=True)
    blood_grp = Column(String(5), nullable=True)
    birthdate = Column(Date, nullable=True)
    total_tokens = Column(Integer, default=0)
    github_url = Column(String(255), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    leetcode_url = Column(String(255), nullable=True)
    codeforces_url = Column(String(255), nullable=True)
    hackerrank_url = Column(String(255), nullable=True)
