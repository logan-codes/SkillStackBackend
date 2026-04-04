# Activity type master model
from sqlalchemy import Column, String
from database.models.base import Base


class ActivityTypeMaster(Base):
    __tablename__ = "activity_type_master"

    type_name = Column(String(100), nullable=False)
