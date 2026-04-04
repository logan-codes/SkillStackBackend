# Role master model
from sqlalchemy import Column, String
from database.models.base import Base


class Role(Base):
    __tablename__ = "roles_master"

    role_name = Column(String(50), nullable=False)
