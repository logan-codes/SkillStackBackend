# Event master model
from sqlalchemy import Column, SmallInteger, String
from database.models.base import Base


class EventMaster(Base):
    __tablename__ = "event_master"

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    is_active = Column(SmallInteger, default=1)
