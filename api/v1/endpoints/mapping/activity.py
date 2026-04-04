# Activity endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.init_db import get_db
from database.crud.mapping.activity import ActivityRepo
from schemas.mapping.activity import ActivityCreate, ActivityUpdate, ActivityResponse
from core.auth import get_current_user, require_staff

router = APIRouter()


@router.get("/", response_model=List[ActivityResponse])
def get_activities(db: Session = Depends(get_db)):
    repo = ActivityRepo(db)
    return repo.get_all()

# Get activity by ID
@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    repo = ActivityRepo(db)
    activity = repo.get_by_id(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    request: ActivityCreate,
    current_user=Depends(require_staff),
    db: Session = Depends(get_db),
):
    repo = ActivityRepo(db)
    return repo.create(
        activity_name=request.activity_name,
        token=request.token,
        activity_limit=request.activity_limit,
        description=request.description,
        activity_type_id=request.activity_type_id,
        workflow_id=request.workflow_id,
    )


@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    request: ActivityUpdate,
    current_user=Depends(require_staff),
    db: Session = Depends(get_db),
):
    repo = ActivityRepo(db)
    activity = repo.get_by_id(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return repo.update(
        activity_id=activity_id,
        activity_name=request.activity_name,
        token=request.token,
        activity_limit=request.activity_limit,
        description=request.description,
    )


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: int, current_user=Depends(require_staff), db: Session = Depends(get_db)
):
    repo = ActivityRepo(db)
    activity = repo.get_by_id(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    repo.delete(activity_id)
    return None
