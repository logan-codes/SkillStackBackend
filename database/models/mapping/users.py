# database/models/mapping/users.py

from sqlalchemy import Column, Integer, BigInteger, SmallInteger, String, DateTime, Date, Numeric
from database.models.base import Base
from datetime import datetime, timezone


class User(Base):
    __tablename__ = "users"

    # --- Identity ---
    id                  = Column(BigInteger, primary_key=True, index=True)
    role_id             = Column(BigInteger, nullable=False)
    gender_id           = Column(SmallInteger, nullable=False)
    register_no         = Column(Integer, nullable=True)
    staff_id            = Column(String(20), nullable=True)
    program_dept_id     = Column(BigInteger, nullable=True)
    year                = Column(SmallInteger, nullable=True)
    semester            = Column(SmallInteger, nullable=True)
    cgpa                = Column(Numeric(3, 2), nullable=True)
    batch_start_year    = Column(SmallInteger, nullable=True)
    batch_end_year      = Column(SmallInteger, nullable=True)

    # --- Contact ---
    email_id            = Column(String(100), unique=True, index=True, nullable=False)
    contact_no          = Column(String(15), nullable=True)

    # --- Personal Info ---
    name                = Column(String(100), nullable=False)
    nationality         = Column(String(50), nullable=True)
    mother_tongue       = Column(String(50), nullable=True)
    religion            = Column(String(50), nullable=True)
    community           = Column(String(50), nullable=True)
    blood_grp           = Column(String(5), nullable=True)
    birthdate           = Column(Date, nullable=True)
    hostel              = Column(SmallInteger, nullable=True)  # 1=Hostel, 0=Day Scholar

    # --- Status ---
    total_tokens        = Column(Integer, default=0)
    is_active           = Column(SmallInteger, nullable=False, default=1)

    # --- Timestamps ---
    created_date        = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_date        = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by          = Column(BigInteger, nullable=True)
    updated_by          = Column(BigInteger, nullable=True)
