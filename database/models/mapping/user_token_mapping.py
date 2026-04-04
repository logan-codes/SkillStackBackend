# User token mapping model
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database.models.base import Base


class UserTokenMapping(Base):
    __tablename__ = "user_token_mapping"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_amount = Column(Integer, nullable=False)
    transaction_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    reference_id = Column(Integer, nullable=True)
