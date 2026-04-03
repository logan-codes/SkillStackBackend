# api/v1/endpoints/mapping/user_social_links.py
# User Social Links endpoints - CRUD operations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict

from database.init_db import get_db
from database.crud.mapping.user_social_links import UserSocialLinkRepo
from schemas.mapping.user_social_links import (
    UserSocialLinkCreate,
    UserSocialLinkUpdate,
    UserSocialLinkResponse,
    UserSocialLinksResponse
)
from core.auth import get_current_user

router = APIRouter()


# ──────────────────────────────────────────────────────────────
# STUDENT ROUTES — any authenticated user
# ──────────────────────────────────────────────────────────────

@router.get("/", response_model=List[UserSocialLinkResponse])
def get_my_social_links(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all social links for the current user.
    """
    repo = UserSocialLinkRepo(db)
    return repo.get_user_links(current_user.id)


@router.get("/all", response_model=UserSocialLinksResponse)
def get_my_social_links_formatted(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all social links formatted by platform.
    """
    repo = UserSocialLinkRepo(db)
    links = repo.get_user_links_as_dict(current_user.id)
    return UserSocialLinksResponse(
        github=links.get("github"),
        linkedin=links.get("linkedin"),
        leetcode=links.get("leetcode"),
        hackerrank=links.get("hackerrank"),
        codechef=links.get("codechef")
    )


@router.post("/", response_model=UserSocialLinkResponse, status_code=status.HTTP_201_CREATED)
def add_social_link(
    request: UserSocialLinkCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new social link.
    """
    repo = UserSocialLinkRepo(db)
    
    # Check if platform already exists
    existing = repo.get_link_by_platform(current_user.id, request.platform)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Link for {request.platform} already exists. Use PUT to update."
        )
    
    return repo.create_link(
        user_id=current_user.id,
        platform=request.platform,
        profile_url=request.profile_url
    )


@router.put("/{link_id}", response_model=UserSocialLinkResponse)
def update_social_link(
    link_id: int,
    request: UserSocialLinkUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing social link.
    """
    repo = UserSocialLinkRepo(db)
    link = repo.get_link_by_id(link_id)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    if link.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this link"
        )
    
    return repo.update_link(
        link_id=link_id,
        platform=request.platform,
        profile_url=request.profile_url
    )


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_social_link(
    link_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a social link (soft delete).
    """
    repo = UserSocialLinkRepo(db)
    link = repo.get_link_by_id(link_id)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    if link.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this link"
        )
    
    repo.delete_link(link_id)
    return None


@router.put("/platform/{platform}", response_model=UserSocialLinkResponse)
def upsert_social_link(
    platform: str,
    request: UserSocialLinkUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update or create a social link by platform.
    """
    repo = UserSocialLinkRepo(db)
    return repo.upsert_link(
        user_id=current_user.id,
        platform=platform,
        profile_url=request.profile_url
    )
