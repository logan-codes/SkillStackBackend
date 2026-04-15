# Activity Master - Master list of trackable student activities
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    SmallInteger,
    DateTime,
    Time,
    BigInteger,
)
from database.models.base import Base
from datetime import datetime, time


class ActivityMaster(Base):
    __tablename__ = "activity"

    id = Column(BigInteger, primary_key=True)
    activity_name = Column(String(100), nullable=False)
    activity_limit = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    token = Column(Integer, default=0, nullable=False)
    workflow_id = Column(BigInteger, nullable=True)
    type = Column(SmallInteger, nullable=True)
    is_active = Column(SmallInteger, default=1, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(
        Time, default=time(0, 0, 0)
    )  # Note: PostgreSQL has time type here (known quirk)
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
