# User activity CRUD operations
from sqlalchemy.orm import Session
from database.models.mapping.user_activity_mapping import UserActivityMapping
from database.models.mapping.activity import Activity


def start_activity(
    db: Session,
    user_id: int,
    activity_id: int,
    custom_name: str,
    permission_proof: str = None,
    start_date=None,
    end_date=None,
):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        return None

    existing = (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.user_id == user_id,
            UserActivityMapping.activity_id == activity_id,
        )
        .first()
    )
    if existing:
        return "already_started"

    user_activity = UserActivityMapping(
        user_id=user_id,
        activity_id=activity_id,
        custom_name=custom_name,
        status_id=1,  # PENDING
        permission_proof=permission_proof,
        start_date=start_date,
        end_date=end_date,
    )
    db.add(user_activity)
    db.commit()
    db.refresh(user_activity)
    return user_activity


def submit_proof(
    db: Session,
    user_activity_id: int,
    user_id: int,
    proof: str,
    proof_description: str = None,
):
    user_activity = (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.id == user_activity_id,
            UserActivityMapping.user_id == user_id,
        )
        .first()
    )
    if not user_activity:
        return None

    if user_activity.status_id != 2:  # Not ONGOING
        return "invalid_status"

    user_activity.proof_document = proof
    user_activity.proof_description = proof_description
    user_activity.status_id = 3  # SUBMITTED
    db.commit()
    db.refresh(user_activity)
    return user_activity


def delete_user_activity(db: Session, user_activity_id: int, user_id: int):
    user_activity = (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.id == user_activity_id,
            UserActivityMapping.user_id == user_id,
        )
        .first()
    )
    if not user_activity:
        return None

    if user_activity.status_id != 1:  # Not PENDING
        return "invalid_status"

    db.delete(user_activity)
    db.commit()
    return "deleted"


def get_user_activities(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return (
        db.query(UserActivityMapping)
        .filter(UserActivityMapping.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_activity_by_id(db: Session, user_activity_id: int, user_id: int):
    return (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.id == user_activity_id,
            UserActivityMapping.user_id == user_id,
        )
        .first()
    )
