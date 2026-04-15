# Stage master model
from sqlalchemy import Column, SmallInteger, String
from database.models.base import Base


class Stage(Base):
    __tablename__ = "stage"

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    is_active = Column(SmallInteger, default=1)

    created_date = None
    updated_date = None
    created_by = None
    updated_by = None
