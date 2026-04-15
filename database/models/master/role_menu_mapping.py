# Role Menu Mapping model
from sqlalchemy import Column, Integer, SmallInteger, DateTime, UniqueConstraint
from database.models.base import Base
from datetime import datetime


class RoleMenuMapping(Base):
    __tablename__ = "role_menu_mapping"
    __table_args__ = (UniqueConstraint("role_id", "menu_id"),)

    id = Column(SmallInteger, primary_key=True)
    role_id = Column(Integer, nullable=False)
    menu_id = Column(Integer, nullable=False)
    is_acitve = Column(SmallInteger, default=1)  # Note: typo as per original schema
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
