# Workflow master model
from sqlalchemy import Column, String
from database.models.base import Base


class Workflow(Base):
    __tablename__ = "workflow_master"

    name = Column(String(100), nullable=False)
