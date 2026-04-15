# Status master model
from sqlalchemy import Column, SmallInteger, String
from database.models.base import Base


class Status(Base):
    __tablename__ = "status"

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    is_active = Column(SmallInteger, default=1)

    # Override Base columns - status table doesn't have these
    created_date = None
    updated_date = None
    created_by = None
    updated_by = None
