# Status master model
from sqlalchemy import Column, String
from database.models.base import Base


class Status(Base):
    __tablename__ = "status_master"

    name = Column(String(50), nullable=False)
