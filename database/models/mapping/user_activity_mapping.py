# User Activity Mapping - Student activity submissions (core transaction table)
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    SmallInteger,
    DateTime,
    BigInteger,
)
from database.models.base import Base
from datetime import datetime


class UserActivityMapping(Base):
    __tablename__ = "user_activity_mapping"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    activity_id = Column(BigInteger, nullable=False)
    title = Column(String(200), nullable=False)
    activity_details = Column(Text, nullable=True)
    event_type = Column(BigInteger, nullable=True)
    stage_id = Column(BigInteger, nullable=True)
    status = Column(BigInteger, nullable=True)
    permission_score = Column(Integer, default=0)
    proof_score = Column(Integer, default=0)
    activity_start_date = Column(Date, nullable=True)
    activity_end_date = Column(Date, nullable=True)
    is_active = Column(SmallInteger, default=1)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
