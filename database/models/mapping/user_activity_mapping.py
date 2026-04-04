# User activity mapping model
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from database.models.base import Base


class UserActivityMapping(Base):
    __tablename__ = "user_activity_mapping"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activity_master.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("status_master.id"), nullable=False)
    current_stage_id = Column(Integer, ForeignKey("stage_master.id"), nullable=True)
    proof_document = Column(String(500), nullable=True)
    proof_description = Column(String(255), nullable=True)
    custom_name = Column(String(200), nullable=True)
    permission_proof = Column(String(500), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    ai_verification_result = Column(Text, nullable=True)
    tokens_earned = Column(Integer, default=0)
