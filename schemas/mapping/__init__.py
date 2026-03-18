# schemas/mapping/__init__.py
# Mapping table schemas

from schemas.user import LoginRequest, LoginResponse, UserInfo

__all__ = [
    "LoginRequest",
    "LoginResponse",
    "UserInfo",
]
