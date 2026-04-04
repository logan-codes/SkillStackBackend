# Base model - all models inherit from this
from sqlalchemy import Column, BigInteger, SmallInteger, DateTime
from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    id = Column(BigInteger, primary_key=True, index=True)
    is_active = Column(SmallInteger, default=1, nullable=False)
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_date = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
