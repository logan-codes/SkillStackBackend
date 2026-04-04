# Malpractice master model
from sqlalchemy import Column, Integer, String
from database.models.base import Base


class MalpracticeMaster(Base):
    __tablename__ = "malpractice_master"

    name = Column(String(200), nullable=False)
    token_deduction = Column(Integer, default=0)
