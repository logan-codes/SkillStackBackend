# Base model - all models inherit from this
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, SmallInteger, DateTime
from datetime import datetime, timezone

Base = declarative_base()


# CommonFields - mixin with common fields
class CommonFields:
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
