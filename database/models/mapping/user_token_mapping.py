# User Token Mapping - Token credit/debit ledger per user
from sqlalchemy import Column, Integer, SmallInteger, DateTime
from database.models.base import Base
from datetime import datetime


class UserTokenMapping(Base):
    __tablename__ = "user_token_mapping"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    completed_activity_id = Column(Integer, nullable=True)
    malpractice_id = Column(Integer, nullable=True)
    token_value = Column(Integer, nullable=False)
    is_active = Column(SmallInteger, default=1)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
