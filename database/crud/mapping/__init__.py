# database/crud/mapping/__init__.py
# Mapping table CRUD operations

from database.crud.mapping.users import get_user_by_email, get_user_by_id

__all__ = [
    "get_user_by_email",
    "get_user_by_id",
]
