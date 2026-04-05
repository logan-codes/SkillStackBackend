# User activity CRUD operations
from sqlalchemy.orm import Session
from database.models.mapping.user_activity_mapping import UserActivityMapping
from database.models.master.activity_master import ActivityMaster
from database.models.master.student_goal_master import StudentGoalMaster
from database.models.mapping.activity_studentgoal_mapping import (
    ActivityStudentGoalMapping,
)


def start_activity(
    db: Session,
    user_id: int,
    activity_id: int,
    custom_name: str,
    permission_proof: str = None,
    start_date=None,
    end_date=None,
):
    activity = db.query(ActivityMaster).filter(ActivityMaster.id == activity_id).first()
    if not activity:
        return None

    existing = (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.user_id == user_id,
            UserActivityMapping.activity_id == activity_id,
            UserActivityMapping.is_active == 1,
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
    student_goal_id: int = None,
):
    user_activity = (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.id == user_activity_id,
            UserActivityMapping.user_id == user_id,
            UserActivityMapping.is_active == 1,
        )
        .first()
    )
    if not user_activity:
        return None

    if user_activity.status_id != 2:  # Not ONGOING
        return "invalid_status"

    if not student_goal_id:
        return "student_goal_required"

    # Get student goal to validate and get token value
    student_goal = (
        db.query(StudentGoalMaster)
        .filter(StudentGoalMaster.id == student_goal_id)
        .first()
    )
    if not student_goal:
        return "invalid_student_goal"

    # Validate that the student_goal maps to this activity
    mapping = (
        db.query(ActivityStudentGoalMapping)
        .filter(
            ActivityStudentGoalMapping.activity_id == user_activity.activity_id,
            ActivityStudentGoalMapping.student_goal_id == student_goal_id,
            ActivityStudentGoalMapping.is_active == 1,
        )
        .first()
    )

    if not mapping:
        return "invalid_mapping"

    user_activity.proof_document = proof
    user_activity.proof_description = proof_description
    user_activity.student_goal_id = student_goal_id
    user_activity.tokens_earned = student_goal.token
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
            UserActivityMapping.is_active == 1,
        )
        .first()
    )
    if not user_activity:
        return None

    if user_activity.status_id != 1:  # Not PENDING
        return "invalid_status"

    user_activity.is_active = 0
    db.commit()
    return "deleted"


def get_user_activities(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.user_id == user_id, UserActivityMapping.is_active == 1
        )
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
            UserActivityMapping.is_active == 1,
        )
        .first()
    )


def get_available_categories(db: Session, activity_id: int):
    """Get all student_goal_master options that map to this activity"""
    mappings = (
        db.query(ActivityStudentGoalMapping)
        .filter(
            ActivityStudentGoalMapping.activity_id == activity_id,
            ActivityStudentGoalMapping.is_active == 1,
        )
        .all()
    )

    categories = []
    for mapping in mappings:
        student_goal = (
            db.query(StudentGoalMaster)
            .filter(
                StudentGoalMaster.id == mapping.student_goal_id,
                StudentGoalMaster.is_active == 1,
            )
            .first()
        )
        if student_goal:
            categories.append(
                {
                    "id": student_goal.id,
                    "activity_name": student_goal.activity_name,
                    "token": student_goal.token,
                }
            )

    return categories
