# Activity CRUD operations
from sqlalchemy.orm import Session
from database.models.mapping.activity import Activity
from typing import List, Optional


class ActivityRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Activity]:
        return self.db.query(Activity).filter(Activity.is_active == 1).all()

    def get_by_id(self, activity_id: int) -> Optional[Activity]:
        return (
            self.db.query(Activity)
            .filter(Activity.id == activity_id, Activity.is_active == 1)
            .first()
        )

    def create(
        self,
        activity_name: str,
        token: int = 0,
        activity_limit: int = None,
        description: str = None,
        activity_type_id: int = None,
        workflow_id: int = None,
    ) -> Activity:
        activity = Activity(
            activity_name=activity_name,
            token=token,
            activity_limit=activity_limit,
            description=description,
            activity_type_id=activity_type_id,
            workflow_id=workflow_id,
        )
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def update(
        self,
        activity_id: int,
        activity_name: str = None,
        token: int = None,
        activity_limit: int = None,
        description: str = None,
    ) -> Optional[Activity]:
        activity = self.get_by_id(activity_id)
        if not activity:
            return None

        if activity_name is not None:
            activity.activity_name = activity_name
        if token is not None:
            activity.token = token
        if activity_limit is not None:
            activity.activity_limit = activity_limit
        if description is not None:
            activity.description = description

        self.db.commit()
        self.db.refresh(activity)
        return activity

    def delete(self, activity_id: int) -> bool:
        activity = self.get_by_id(activity_id)
        if not activity:
            return False
        activity.is_active = 0
        self.db.commit()
        return True
