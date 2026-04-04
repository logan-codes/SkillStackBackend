# Gender master model
from sqlalchemy import Column, String
from database.models.base import Base


class Gender(Base):
    __tablename__ = "gender_master"

    name = Column(String(50), nullable=False)
