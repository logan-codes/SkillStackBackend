# database/models/mapping/user_social_links.py
# User Social Links - stores social/coding platform links

from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, ForeignKey
from database.models.base import Base
from datetime import datetime, timezone


class UserSocialLink(Base):
    __tablename__ = "user_social_links"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String(50), nullable=False)  # github, linkedin, leetcode, hackerrank, codechef
    profile_url = Column(String(500), nullable=False)
    is_active = Column(SmallInteger, default=1, nullable=False)
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
