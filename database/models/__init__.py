# database/models/__init__.py
# This folder contains SQLAlchemy ORM models for all database tables

from database.models.mapping.users import User

__all__ = [
    "User",
]
