# User activity CRUD operations - Fixed for PostgreSQL database
from sqlalchemy.orm import Session
from typing import List, Optional
from database.models.mapping.user_activity_mapping import UserActivityMapping
from database.models.master.activity_master import ActivityMaster
from database.models.master.status import Status
from database.models.mapping.staff_student_mapping import StaffStudentMapping
from database.models.mapping.users import User
from database.models.mapping.user_token_mapping import UserTokenMapping
from database.models.mapping.student_goal import StudentGoal


def can_start_activity(db: Session, user_id: int, activity_id: int, title: str):
    """Validate if user can start an activity"""
    activity = db.query(ActivityMaster).filter(ActivityMaster.id == activity_id).first()
    if not activity:
        return False, "Activity not found"

    # Check for duplicate (same activity + same title + status Yet To Start/In Progress/Completed)
    existing = (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.user_id == user_id,
            UserActivityMapping.activity_id == activity_id,
            UserActivityMapping.title == title,
            UserActivityMapping.status.in_([1, 2, 3]),
            UserActivityMapping.is_active == 1,
        )
        .first()
    )
    if existing:
        return False, "Same activity already in progress"

    return True, None


def start_activity(
    db: Session,
    user_id: int,
    activity_id: int,
    title: str,
    activity_details: str = None,
    event_type: int = None,
    activity_start_date=None,
    activity_end_date=None,
):
    """Start a new activity for a user"""
    if (
        activity_start_date
        and activity_end_date
        and activity_start_date > activity_end_date
    ):
        return "start_date cannot be after end_date"

    can_start, msg = can_start_activity(db, user_id, activity_id, title)
    if not can_start:
        return msg

    activity = db.query(ActivityMaster).filter(ActivityMaster.id == activity_id).first()
    if not activity:
        return "activity_not_found"

    user_activity = UserActivityMapping(
        user_id=user_id,
        activity_id=activity_id,
        title=title,
        activity_details=activity_details,
        event_type=event_type,
        status=1,  # Yet To Start
        activity_start_date=activity_start_date,
        activity_end_date=activity_end_date,
    )
    db.add(user_activity)
    db.flush()

    return user_activity


def submit_proof(
    db: Session,
    activity_id: int,
    user_id: int,
    activity_details: str = None,
):
    """Submit proof for an activity (move from In Progress to Submitted)"""
    user_activity = (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.id == activity_id,
            UserActivityMapping.user_id == user_id,
            UserActivityMapping.is_active == 1,
        )
        .first()
    )
    if not user_activity:
        return "not_found"

    if user_activity.status != 2:  # Not In Progress
        return "invalid_status"

    # Update activity details and move to status 3 (Submitted)
    if activity_details:
        user_activity.activity_details = activity_details
    user_activity.status = 3

    db.commit()
    db.refresh(user_activity)
    return user_activity


def delete_user_activity(db: Session, activity_id: int, user_id: int):
    """Soft delete user activity"""
    user_activity = (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.id == activity_id,
            UserActivityMapping.user_id == user_id,
            UserActivityMapping.is_active == 1,
        )
        .first()
    )
    if not user_activity:
        return "not_found"

    if user_activity.status != 1:  # Can only delete at status 1 (Yet To Start)
        return "cannot_delete"

    user_activity.is_active = 0
    db.commit()
    return "deleted"


def get_user_activities(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    include_inactive: bool = False,
):
    """Get activities for a user"""
    query = db.query(UserActivityMapping).filter(UserActivityMapping.user_id == user_id)

    if not include_inactive:
        query = query.filter(UserActivityMapping.is_active == 1)

    return query.offset(skip).limit(limit).all()


def get_user_activity_by_id(db: Session, activity_id: int, user_id: int = None):
    """Get a specific user activity"""
    query = db.query(UserActivityMapping).filter(UserActivityMapping.id == activity_id)

    if user_id:
        query = query.filter(UserActivityMapping.user_id == user_id)

    return query.first()


def get_available_activities(db: Session):
    """Get all available activities from activity master table"""
    activities = db.query(ActivityMaster).filter(ActivityMaster.is_active == 1).all()
    return [
        {
            "id": a.id,
            "activity_name": a.activity_name,
            "token": a.token,
            "activity_type_id": a.activity_type_id,
        }
        for a in activities
    ]


def validate_teacher_access(db: Session, teacher_user_id: int, student_id: int):
    """Validate if teacher is assigned to a student"""
    mapping = (
        db.query(StaffStudentMapping)
        .filter(
            StaffStudentMapping.staff_id == teacher_user_id,
            StaffStudentMapping.student_id == student_id,
            StaffStudentMapping.is_active == 1,
        )
        .first()
    )

    if not mapping:
        return False, "You are not assigned to this student"

    return True, None


def teacher_review(
    db: Session,
    activity_id: int,
    teacher_user_id: int,
    action: str,
    reason: str = None,
):
    """Teacher approves or rejects an activity"""
    activity = (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.id == activity_id,
            UserActivityMapping.is_active == 1,
        )
        .first()
    )

    if not activity:
        return "not_found"

    # Validate teacher access
    valid, msg = validate_teacher_access(db, teacher_user_id, activity.user_id)
    if not valid:
        return msg

    # Check valid status for review (1=Yet To Start, 2=In Progress)
    if activity.status not in [1, 2]:
        return "invalid_status"

    if action == "approve":
        if activity.status == 1:
            # Approve from Yet To Start → In Progress
            activity.status = 2
        elif activity.status == 2:
            # Approve from In Progress → Completed + Add tokens
            activity.status = 3  # Completed

            # Get activity token value
            activity_master = (
                db.query(ActivityMaster)
                .filter(ActivityMaster.id == activity.activity_id)
                .first()
            )
            tokens = activity_master.token if activity_master else 0

            if tokens > 0:
                # Record token transaction
                token_record = UserTokenMapping(
                    user_id=activity.user_id,
                    completed_activity_id=activity.id,
                    token_value=tokens,
                )
                db.add(token_record)

                # Update user total tokens
                user = db.query(User).filter(User.id == activity.user_id).first()
                if user:
                    user.total_tokens += tokens

        db.commit()
        db.refresh(activity)
        return activity

    elif action == "reject":
        if activity.status == 1:
            # Reject from Yet To Start → Failure
            activity.status = 4
        elif activity.status == 2:
            # Reject from In Progress → Failure
            activity.status = 4

        db.commit()
        db.refresh(activity)
        return activity

    return "invalid_action"


def get_teacher_students(db: Session, teacher_user_id: int):
    """Get all students assigned to a teacher"""
    mappings = (
        db.query(StaffStudentMapping)
        .filter(
            StaffStudentMapping.staff_id == teacher_user_id,
            StaffStudentMapping.is_active == 1,
        )
        .all()
    )

    students = []
    for m in mappings:
        student = db.query(User).filter(User.id == m.student_id).first()
        if student:
            students.append(
                {
                    "id": student.id,
                    "name": student.name,
                    "register_no": student.register_no,
                }
            )

    return students


def get_teacher_student_activities(
    db: Session, teacher_user_id: int, status: int = None
):
    """Get activities for all students of a teacher"""
    # Get student IDs
    mappings = (
        db.query(StaffStudentMapping)
        .filter(
            StaffStudentMapping.staff_id == teacher_user_id,
            StaffStudentMapping.is_active == 1,
        )
        .all()
    )
    student_ids = [m.student_id for m in mappings]

    if not student_ids:
        return []

    query = db.query(UserActivityMapping).filter(
        UserActivityMapping.user_id.in_(student_ids)
    )

    if status:
        query = query.filter(UserActivityMapping.status == status)

    return query.all()


def apply_malpractice(
    db: Session,
    student_id: int,
    malpractice_id: int,
    teacher_user_id: int,
):
    """Apply malpractice penalty to a student"""
    from database.models.master.malpractice_master import MalpracticeMaster

    # Validate teacher access
    valid, msg = validate_teacher_access(db, teacher_user_id, student_id)
    if not valid:
        return msg

    # Get malpractice details
    malpractice = (
        db.query(MalpracticeMaster)
        .filter(MalpracticeMaster.id == malpractice_id)
        .first()
    )
    if not malpractice:
        return "malpractice_not_found"

    # Record token deduction
    token_record = UserTokenMapping(
        user_id=student_id,
        malpractice_id=malpractice_id,
        token_value=malpractice.token_deduction,
    )
    db.add(token_record)

    # Update user tokens
    user = db.query(User).filter(User.id == student_id).first()
    if user:
        user.total_tokens += malpractice.token_deduction

    db.commit()
    return "malpractice_applied"
