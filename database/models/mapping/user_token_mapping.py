# database/models/mapping/user_token_mapping.py
# Tracks user token transactions (earned, deducted, bonuses)

from sqlalchemy import Column, Integer, SmallInteger, DateTime, Text, String, ForeignKey
from database.models.base import Base
from datetime import datetime

class UserTokenMapping(Base):
    __tablename__ = "user_token_mapping"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_amount = Column(Integer, nullable=False)  # Positive=earned, Negative=deducted
    transaction_type = Column(String(50), nullable=False)  # earned, deducted, bonus, malpractice
    description = Column(Text, nullable=True)
    reference_id = Column(Integer, nullable=True)  # Link to activity/malpractice
    is_active = Column(SmallInteger, default=1, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
