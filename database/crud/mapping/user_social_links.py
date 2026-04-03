# database/crud/mapping/user_social_links.py
# User Social Links CRUD operations

from sqlalchemy.orm import Session
from database.models.mapping.user_social_links import UserSocialLink
from typing import List, Optional, Dict


class UserSocialLinkRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_links(self, user_id: int) -> List[UserSocialLink]:
        """Get all social links for a user"""
        return self.db.query(UserSocialLink).filter(
            UserSocialLink.user_id == user_id,
            UserSocialLink.is_active == 1
        ).all()
    
    def get_link_by_id(self, link_id: int) -> Optional[UserSocialLink]:
        """Get a specific link by ID"""
        return self.db.query(UserSocialLink).filter(
            UserSocialLink.id == link_id,
            UserSocialLink.is_active == 1
        ).first()
    
    def get_link_by_platform(self, user_id: int, platform: str) -> Optional[UserSocialLink]:
        """Get a specific platform link for a user"""
        return self.db.query(UserSocialLink).filter(
            UserSocialLink.user_id == user_id,
            UserSocialLink.platform == platform,
            UserSocialLink.is_active == 1
        ).first()
    
    def create_link(self, user_id: int, platform: str, profile_url: str) -> UserSocialLink:
        """Create a new social link"""
        link = UserSocialLink(
            user_id=user_id,
            platform=platform,
            profile_url=profile_url,
            is_active=1
        )
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link
    
    def update_link(self, link_id: int, platform: str = None, profile_url: str = None) -> Optional[UserSocialLink]:
        """Update an existing link"""
        link = self.get_link_by_id(link_id)
        if not link:
            return None
        
        if platform is not None:
            link.platform = platform
        if profile_url is not None:
            link.profile_url = profile_url
        
        self.db.commit()
        self.db.refresh(link)
        return link
    
    def delete_link(self, link_id: int) -> bool:
        """Soft delete a link"""
        link = self.get_link_by_id(link_id)
        if not link:
            return False
        
        link.is_active = 0
        self.db.commit()
        return True
    
    def upsert_link(self, user_id: int, platform: str, profile_url: str) -> UserSocialLink:
        """Update or create a link for a platform"""
        existing = self.get_link_by_platform(user_id, platform)
        if existing:
            existing.profile_url = profile_url
            self.db.commit()
            self.db.refresh(existing)
            return existing
        return self.create_link(user_id, platform, profile_url)
    
    def get_user_links_as_dict(self, user_id: int) -> Dict[str, str]:
        """Get all user links as a dictionary"""
        links = self.get_user_links(user_id)
        result = {}
        for link in links:
            result[link.platform] = link.profile_url
        return result
