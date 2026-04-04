# Application config master model
from sqlalchemy import Column, String, Text
from database.models.base import Base


class ApplicationConfig(Base):
    __tablename__ = "application_config"

    config_name = Column(String(100), nullable=False)
    config_value = Column(Text, nullable=True)
