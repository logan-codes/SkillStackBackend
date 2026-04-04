# Event master model
from sqlalchemy import Column, String
from database.models.base import Base


class EventMaster(Base):
    __tablename__ = "event_master"

    name = Column(String(100), nullable=False)
