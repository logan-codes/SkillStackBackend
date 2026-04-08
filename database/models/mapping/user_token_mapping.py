# User token mapping model
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from database.models.base import Base
from datetime import datetime


class UserTokenMapping(Base):
    __tablename__ = "user_token_mapping"
    __table_args__ = (UniqueConstraint("id"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_amount = Column(Integer, nullable=False)
    transaction_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    reference_id = Column(Integer, nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow, index=True)
