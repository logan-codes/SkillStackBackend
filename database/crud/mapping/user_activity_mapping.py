# User activity CRUD operations
from sqlalchemy.orm import Session
from typing import List
from database.models.mapping.user_activity_mapping import UserActivityMapping
from database.models.master.activity_master import ActivityMaster
from database.models.master.student_goal_master import StudentGoalMaster
from database.models.mapping.activity_studentgoal_mapping import (
    ActivityStudentGoalMapping,
)
from database.models.mapping.staff_student_mapping import StaffStudentMapping
from database.models.mapping.users import User
from database.models.mapping.user_token_mapping import UserTokenMapping


def can_start_activity(
    db: Session, user_id: int, activity_id: int, custom_name: str, student_goal_id: int
):
    # Validate student_goal_id exists and maps to this activity
    mapping = (
        db.query(ActivityStudentGoalMapping)
        .filter(
            ActivityStudentGoalMapping.activity_id == activity_id,
            ActivityStudentGoalMapping.student_goal_id == student_goal_id,
            ActivityStudentGoalMapping.is_active == 1,
        )
        .first()
    )
    if not mapping:
        return False, "Invalid category for this activity"

    # Check 1: Exact duplicate (same activity + same name + status 1/2/3)
    existing = (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.user_id == user_id,
            UserActivityMapping.activity_id == activity_id,
            UserActivityMapping.custom_name == custom_name,
            UserActivityMapping.status_id.in_([1, 2, 3]),
            UserActivityMapping.is_deleted == 0,
        )
        .first()
    )
    if existing:
        return False, "Same activity already in progress"

    # Check 2: Activity limit from activity_master (count all active: 1,2,3,4 for this activity_id)
    activity = db.query(ActivityMaster).filter(ActivityMaster.id == activity_id).first()
    if activity and activity.activity_limit:
        active_count = (
            db.query(UserActivityMapping)
            .filter(
                UserActivityMapping.user_id == user_id,
                UserActivityMapping.activity_id == activity_id,
                UserActivityMapping.status_id.in_([1, 2, 3, 4]),
                UserActivityMapping.is_deleted == 0,
            )
            .count()
        )
        if active_count >= activity.activity_limit:
            return False, "Activity limit reached"

    return True, None


def can_resubmit(db: Session, activity_id: int):
    activity = (
        db.query(UserActivityMapping)
        .filter(UserActivityMapping.id == activity_id)
        .first()
    )

    if not activity:
        return False, "Activity not found"

    if activity.is_locked:
        return False, "Activity is locked. Contact teacher."

    if activity.submission_count >= 100:
        activity.is_locked = True
        db.commit()
        return False, "Submission limit exceeded. Activity locked."

    return True, None


def validate_teacher_access(db: Session, teacher_user_id: int, student_id: int):
    # Check for section-based mapping (ClassCoordinator - teacher manages entire section)
    student = db.query(User).filter(User.id == student_id).first()
    if student and student.section:
        section_mapping = (
            db.query(StaffStudentMapping)
            .filter(
                StaffStudentMapping.staff_id == teacher_user_id,
                StaffStudentMapping.section == student.section,
                StaffStudentMapping.mapping_type.in_(["ClassCoordinator"]),
            )
            .first()
        )
        if section_mapping:
            return True, None

    # Check for student-based mapping (ClassTeacher/Mentor - teacher manages individual students)
    mapping = (
        db.query(StaffStudentMapping)
        .filter(
            StaffStudentMapping.staff_id == teacher_user_id,
            StaffStudentMapping.student_id == student_id,
            StaffStudentMapping.mapping_type.in_(["ClassTeacher", "Mentor"]),
        )
        .first()
    )

    if not mapping:
        return False, "You are not assigned to this student"

    return True, None


def start_activity(
    db: Session,
    user_id: int,
    activity_id: int,
    custom_name: str,
    student_goal_id: int,
    permission_proof: str = None,
    start_date=None,
    end_date=None,
):
    # Date validation: start_date cannot be after end_date
    if start_date and end_date and start_date > end_date:
        return "start_date cannot be after end_date"

    # Validation: Check can start
    can_start, msg = can_start_activity(
        db, user_id, activity_id, custom_name, student_goal_id
    )
    if not can_start:
        return msg

    activity = db.query(ActivityMaster).filter(ActivityMaster.id == activity_id).first()
    if not activity:
        return "activity_not_found"

    user_activity = UserActivityMapping(
        user_id=user_id,
        activity_id=activity_id,
        student_goal_id=student_goal_id,
        custom_name=custom_name,
        status_id=1,  # PENDING
        permission_proof=permission_proof,
        start_date=start_date,
        end_date=end_date,
    )
    db.add(user_activity)
    db.flush()

    # Record token transaction: Activity Started
    token_record = UserTokenMapping(
        user_id=user_id,
        token_amount=0,
        transaction_type="Activity Started",
        description=f"Activity: {custom_name}",
        reference_id=user_activity.id,
    )
    db.add(token_record)

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
    # Check submission limit
    can_submit, msg = can_resubmit(db, user_activity_id)
    if not can_submit:
        return msg

    user_activity = (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.id == user_activity_id,
            UserActivityMapping.user_id == user_id,
            UserActivityMapping.is_deleted == 0,
        )
        .first()
    )
    if not user_activity:
        return "not_found"

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
    user_activity.submission_count += 1

    # Record token transaction: Activity Submitted
    token_record = UserTokenMapping(
        user_id=user_id,
        token_amount=0,
        transaction_type="Activity Submitted",
        description=f"Activity: {user_activity.custom_name}",
        reference_id=user_activity.id,
    )
    db.add(token_record)

    db.commit()
    db.refresh(user_activity)
    return user_activity


def delete_user_activity(db: Session, user_activity_id: int, user_id: int):
    user_activity = (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.id == user_activity_id,
            UserActivityMapping.user_id == user_id,
            UserActivityMapping.is_deleted == 0,
        )
        .first()
    )
    if not user_activity:
        return "not_found"

    # Student can only delete at Pending(1)
    if user_activity.status_id != 1:
        return "invalid_status"

    user_activity.is_deleted = 1
    db.commit()
    return "deleted"


def undelete_user_activity(db: Session, user_activity_id: int, user_id: int):
    user_activity = (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.id == user_activity_id,
            UserActivityMapping.user_id == user_id,
        )
        .first()
    )
    if not user_activity:
        return "not_found"

    user_activity.is_deleted = 0
    db.commit()
    return "restored"


def teacher_review(
    db: Session,
    activity_id: int,
    teacher_user_id: int,
    action: str,
    reason: str = None,
):
    activity = (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.id == activity_id,
            UserActivityMapping.is_deleted == 0,
        )
        .first()
    )

    if not activity:
        return "not_found"

    # Validate teacher access
    valid, msg = validate_teacher_access(db, teacher_user_id, activity.user_id)
    if not valid:
        return msg

    # Check status
    if activity.status_id not in [1, 2, 3]:
        return "invalid_status"

    if action == "approve":
        # Teacher can approve:
        # - From Status 1 (Pending) → Status 2 (In Progress)
        # - From Status 3 (Submitted) → Status 4 (Completed)
        # NOT from Status 2 (must wait for student to submit first)
        if activity.status_id == 1:
            # Approve from Pending → In Progress
            activity.status_id = 2

            # Record token transaction: Activity Approved (to In Progress)
            token_record = UserTokenMapping(
                user_id=activity.user_id,
                token_amount=0,
                transaction_type="Activity Approved",
                description=f"Activity: {activity.custom_name} - Approved to In Progress",
                reference_id=activity.id,
            )
            db.add(token_record)

        elif activity.status_id == 3:
            # Approve from Submitted → Completed + Add tokens
            activity.status_id = 4

            # Add tokens (only once)
            if not activity.is_completed:
                goal = (
                    db.query(StudentGoalMaster)
                    .filter(StudentGoalMaster.id == activity.student_goal_id)
                    .first()
                )
                tokens = goal.token if goal else 0

                # Add to UserTokenMapping
                token_record = UserTokenMapping(
                    user_id=activity.user_id,
                    token_amount=tokens,
                    transaction_type="Activity Completed",
                    description=f"Activity: {activity.custom_name}",
                    reference_id=activity.id,
                )
                db.add(token_record)

                # Update user total
                user = db.query(User).filter(User.id == activity.user_id).first()
                if user:
                    user.total_tokens += tokens

                activity.tokens_earned = tokens
                activity.is_completed = True
        else:
            return "cannot_approve_without_submission"

        activity.rejection_reason = None

    elif action == "reject":
        if activity.status_id == 1:
            # Reject from Pending → Rejected (no reason needed)
            activity.status_id = 5
            activity.rejection_reason = None

            # Record token transaction: Activity Rejected
            token_record = UserTokenMapping(
                user_id=activity.user_id,
                token_amount=0,
                transaction_type="Activity Rejected",
                description=f"Activity: {activity.custom_name} - Rejected at Pending stage",
                reference_id=activity.id,
            )
            db.add(token_record)

        elif activity.status_id == 2:
            # Reject from In Progress → Rejected (no reason needed)
            activity.status_id = 5
            activity.rejection_reason = None

            # Record token transaction: Activity Rejected
            token_record = UserTokenMapping(
                user_id=activity.user_id,
                token_amount=0,
                transaction_type="Activity Rejected",
                description=f"Activity: {activity.custom_name} - Rejected at In Progress stage",
                reference_id=activity.id,
            )
            db.add(token_record)

        elif activity.status_id == 3:
            # Reject from Submitted → In Progress (reason REQUIRED)
            if not reason:
                return "rejection_reason_required"
            activity.status_id = 2
            activity.rejection_reason = reason
            activity.submission_count += 1

            # Record token transaction: Activity Rejected (sent back for revision)
            token_record = UserTokenMapping(
                user_id=activity.user_id,
                token_amount=0,
                transaction_type="Activity Rejected",
                description=f"Activity: {activity.custom_name} - Sent back for revision: {reason}",
                reference_id=activity.id,
            )
            db.add(token_record)

            # Check submission limit
            if activity.submission_count >= 100:
                activity.is_locked = True
    else:
        return "invalid_action"

    db.commit()
    db.refresh(activity)
    return activity


def get_user_activities(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    include_deleted: bool = False,
):
    query = db.query(UserActivityMapping).filter(UserActivityMapping.user_id == user_id)

    if not include_deleted:
        query = query.filter(UserActivityMapping.is_deleted == 0)

    return query.offset(skip).limit(limit).all()


def get_teacher_student_activities(
    db: Session, teacher_user_id: int, status_id: int = None
):
    """Get activities for all students assigned to a teacher"""
    student_ids = []

    # Get students from section-based mapping (ClassCoordinator)
    section_mappings = (
        db.query(StaffStudentMapping)
        .filter(
            StaffStudentMapping.staff_id == teacher_user_id,
            StaffStudentMapping.mapping_type.in_(["ClassCoordinator"]),
        )
        .all()
    )
    sections = [m.section for m in section_mappings]
    if sections:
        section_students = (
            db.query(User)
            .filter(
                User.section.in_(sections),
                User.role_id == 1,
                User.is_active == 1,
            )
            .all()
        )
        student_ids.extend([s.id for s in section_students])

    # Get students from individual mapping (ClassTeacher/Mentor)
    individual_mappings = (
        db.query(StaffStudentMapping)
        .filter(
            StaffStudentMapping.staff_id == teacher_user_id,
            StaffStudentMapping.mapping_type.in_(["ClassTeacher", "Mentor"]),
        )
        .all()
    )
    student_ids.extend([m.student_id for m in individual_mappings if m.student_id])

    if not student_ids:
        return []

    # Get activities for these students
    student_ids = list(set(student_ids))
    query = db.query(UserActivityMapping).filter(
        UserActivityMapping.user_id.in_(student_ids),
        UserActivityMapping.is_deleted == 0,
    )

    if status_id:
        query = query.filter(UserActivityMapping.status_id == status_id)

    return query.order_by(UserActivityMapping.created_date.desc()).all()


def get_user_activity_by_id(
    db: Session, user_activity_id: int, user_id: int, include_deleted: bool = False
):
    query = db.query(UserActivityMapping).filter(
        UserActivityMapping.id == user_activity_id,
        UserActivityMapping.user_id == user_id,
    )

    if not include_deleted:
        query = query.filter(UserActivityMapping.is_deleted == 0)

    return query.first()


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


# ============================================================================
# HELPER FUNCTION: Validate student is active
# ============================================================================
def validate_student_active(db: Session, student_id: int):
    """Check if student is active"""
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        return False, "student_not_found"
    if hasattr(student, "is_active") and student.is_active == 0:
        return False, "student_inactive"
    return True, None


# ============================================================================
# GET TEACHER STUDENTS
# ============================================================================
def get_teacher_students(db: Session, teacher_user_id: int):
    """Get all students assigned to teacher (only active students)"""
    student_ids = []

    # Get students from section-based mapping (ClassCoordinator)
    section_mappings = (
        db.query(StaffStudentMapping)
        .filter(
            StaffStudentMapping.staff_id == teacher_user_id,
            StaffStudentMapping.mapping_type.in_(["ClassCoordinator"]),
        )
        .all()
    )
    sections = [m.section for m in section_mappings]
    if sections:
        section_students = (
            db.query(User)
            .filter(
                User.section.in_(sections),
                User.role_id == 1,
                User.is_active == 1,
            )
            .all()
        )
        student_ids.extend([s.id for s in section_students])

    # Get students from individual mapping (ClassTeacher/Mentor)
    individual_mappings = (
        db.query(StaffStudentMapping)
        .filter(
            StaffStudentMapping.staff_id == teacher_user_id,
            StaffStudentMapping.mapping_type.in_(["ClassTeacher", "Mentor"]),
        )
        .all()
    )
    student_ids.extend([m.student_id for m in individual_mappings if m.student_id])

    if not student_ids:
        return []

    # Only return active students (unique)
    student_ids = list(set(student_ids))
    return db.query(User).filter(User.id.in_(student_ids), User.is_active == 1).all()


# ============================================================================
# GET STUDENT PROFILE
# ============================================================================
def get_student_profile(db: Session, student_id: int, teacher_user_id: int):
    """Get student profile with validation"""
    # Validate teacher access
    valid, _ = validate_teacher_access(db, teacher_user_id, student_id)
    if not valid:
        return None

    # Check student is active
    is_active, _ = validate_student_active(db, student_id)
    if not is_active:
        return None

    return db.query(User).filter(User.id == student_id).first()


# ============================================================================
# GET STUDENT ACTIVITIES BY STATUS
# ============================================================================
def get_student_activities_by_status(
    db: Session, student_id: int, teacher_user_id: int
):
    """Get activities grouped by status"""
    # Validate teacher access
    valid, _ = validate_teacher_access(db, teacher_user_id, student_id)
    if not valid:
        return None

    # Check student is active
    is_active, _ = validate_student_active(db, student_id)
    if not is_active:
        return None

    activities = (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.user_id == student_id,
            UserActivityMapping.is_deleted == 0,
        )
        .all()
    )

    result = {
        "pending": [],
        "ongoing": [],
        "submitted": [],
        "completed": [],
        "rejected": [],
    }

    for activity in activities:
        activity_data = {
            "id": activity.id,
            "custom_name": activity.custom_name,
            "activity_id": activity.activity_id,
            "student_goal_id": activity.student_goal_id,
            "tokens_earned": activity.tokens_earned,
            "status_id": activity.status_id,
            "created_date": activity.created_date,
        }

        status_map = {
            1: "pending",
            2: "ongoing",
            3: "submitted",
            4: "completed",
            5: "rejected",
        }
        result[status_map[activity.status_id]].append(activity_data)

    return result


# ============================================================================
# GET STUDENT GOALS
# ============================================================================
def get_student_goals(db: Session, student_id: int, teacher_user_id: int):
    """Get student's planned goals"""
    # Validate teacher access
    valid, _ = validate_teacher_access(db, teacher_user_id, student_id)
    if not valid:
        return None

    # Check student is active
    is_active, _ = validate_student_active(db, student_id)
    if not is_active:
        return None

    from database.models.mapping.student_goal import StudentGoal

    return (
        db.query(StudentGoal)
        .filter(StudentGoal.user_id == student_id, StudentGoal.is_active == 1)
        .all()
    )


# ============================================================================
# APPLY MALPRACTICE
# ============================================================================
def apply_malpractice(
    db: Session,
    student_id: int,
    teacher_user_id: int,
    malpractice_id: int,
    description: str = None,
):
    """Apply malpractice penalty to student"""
    # Validate teacher access
    valid, _ = validate_teacher_access(db, teacher_user_id, student_id)
    if not valid:
        return "not_assigned"

    # Check student is active
    is_active, msg = validate_student_active(db, student_id)
    if not is_active:
        return msg

    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        return "student_not_found"

    from database.models.master.malpractice_master import MalpracticeMaster

    malpractice = (
        db.query(MalpracticeMaster)
        .filter(MalpracticeMaster.id == malpractice_id)
        .first()
    )
    if not malpractice:
        return "malpractice_not_found"

    token_deduction = malpractice.token_deduction

    if student.total_tokens < token_deduction:
        return "insufficient_tokens"

    # Deduct from student total
    student.total_tokens -= token_deduction

    # Create malpractice record
    from database.models.mapping.student_malpractice import StudentMalpractice

    malpractice_record = StudentMalpractice(
        student_id=student_id,
        malpractice_id=malpractice_id,
        token_deducted=token_deduction,
        teacher_id=teacher_user_id,
        description=description,
        is_reversed=0,
    )
    db.add(malpractice_record)

    # Create negative token transaction (audit trail)
    token_record = UserTokenMapping(
        user_id=student_id,
        token_amount=-token_deduction,
        transaction_type="Malpractice Deduction",
        description=f"{malpractice.name} - {description or ''}",
        reference_id=malpractice_id,
    )
    db.add(token_record)

    db.commit()
    db.refresh(malpractice_record)
    return malpractice_record


# ============================================================================
# REVERSE SELECTED MALPRACTICE (Multiple)
# ============================================================================
def reverse_selected_malpractice(
    db: Session, student_id: int, teacher_user_id: int, record_ids: List[int]
):
    """Reverse selected malpractice records"""
    # Validate teacher access
    valid, _ = validate_teacher_access(db, teacher_user_id, student_id)
    if not valid:
        return "not_assigned"

    # Check student is active
    is_active, _ = validate_student_active(db, student_id)
    if not is_active:
        return "student_inactive"

    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        return "student_not_found"

    from database.models.mapping.student_malpractice import StudentMalpractice

    # Get all records to reverse
    records = (
        db.query(StudentMalpractice)
        .filter(
            StudentMalpractice.id.in_(record_ids),
            StudentMalpractice.student_id == student_id,
            StudentMalpractice.is_reversed == 0,
        )
        .all()
    )

    if not records:
        return "no_records_found"

    total_to_reverse = 0
    reversed_count = 0

    for record in records:
        record.is_reversed = 1
        total_to_reverse += record.token_deducted
        reversed_count += 1

        # Create positive token transaction (audit trail)
        token_record = UserTokenMapping(
            user_id=student_id,
            token_amount=record.token_deducted,
            transaction_type="Malpractice Reversed",
            description=f"Reversed: {record.token_deducted} tokens added back",
            reference_id=record.id,
        )
        db.add(token_record)

    # Add tokens back to student
    student.total_tokens += total_to_reverse

    db.commit()

    return {
        "reversed_count": reversed_count,
        "tokens_returned": total_to_reverse,
        "remaining_tokens": student.total_tokens,
    }


# ============================================================================
# GET STUDENT MALPRACTICE HISTORY
# ============================================================================
def get_student_malpractice(db: Session, student_id: int, teacher_user_id: int):
    """Get all malpractice records for student"""
    # Validate teacher access
    valid, _ = validate_teacher_access(db, teacher_user_id, student_id)
    if not valid:
        return None

    # Check student is active
    is_active, _ = validate_student_active(db, student_id)
    if not is_active:
        return None

    from database.models.mapping.student_malpractice import StudentMalpractice

    return (
        db.query(StudentMalpractice)
        .filter(StudentMalpractice.student_id == student_id)
        .order_by(StudentMalpractice.created_date.desc())
        .all()
    )
