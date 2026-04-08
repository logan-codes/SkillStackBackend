# User activity endpoints
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from database.init_db import get_db
from database.crud.mapping.user_activity_mapping import (
    start_activity,
    submit_proof,
    delete_user_activity,
    undelete_user_activity,
    get_user_activities,
    get_user_activity_by_id,
    get_available_categories,
    teacher_review,
    can_resubmit,
    get_teacher_student_activities,
    get_teacher_students,
    get_student_profile,
    get_student_activities_by_status,
    get_student_goals,
    apply_malpractice,
    reverse_selected_malpractice,
    get_student_malpractice,
)
from schemas.mapping.user_activity_mapping import (
    UserActivityProof,
    UserActivityUpdate,
    UserActivityResponse,
    TeacherReviewRequest,
)
from schemas.mapping.student_malpractice import MalpracticeApply
from database.models.master.malpractice_master import MalpracticeMaster
from database.models.mapping.users import User
from core.auth import get_current_user, require_staff
from pathlib import Path

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_file(file: UploadFile):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Only PDF, JPG, JPEG, PNG allowed")
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 10MB)")
    return ext


class UserActivityStart(BaseModel):
    custom_name: str
    student_goal_id: int
    permission_proof: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


@router.get("/activities", response_model=List[dict])
def get_activities_for_workflow(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all generic activities available for workflow"""
    from database.models.master.activity_master import ActivityMaster

    activities = db.query(ActivityMaster).filter(ActivityMaster.is_active == 1).all()
    return [{"id": a.id, "activity_name": a.activity_name} for a in activities]


@router.get("/{activity_id}/categories", response_model=List[dict])
def get_activity_categories(
    activity_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get available categories (student goals) for an activity"""
    categories = get_available_categories(db, activity_id)
    if not categories:
        raise HTTPException(
            status_code=404, detail="No categories found for this activity"
        )
    return categories


@router.post("/{activity_id}/start", response_model=UserActivityResponse)
def start_my_activity(
    activity_id: int,
    request: UserActivityStart,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = start_activity(
        db=db,
        user_id=current_user.id,
        activity_id=activity_id,
        custom_name=request.custom_name,
        student_goal_id=request.student_goal_id,
        permission_proof=request.permission_proof,
        start_date=request.start_date,
        end_date=request.end_date,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    if result == "activity_not_found":
        raise HTTPException(status_code=404, detail="Activity not found")
    if result == "already_started":
        raise HTTPException(status_code=400, detail="Same activity already in progress")
    if result == "Same activity already in progress":
        raise HTTPException(status_code=400, detail="Same activity already in progress")
    if result == "Activity limit reached":
        raise HTTPException(status_code=400, detail="Activity limit reached")
    return result


@router.put("/{user_activity_id}", response_model=UserActivityResponse)
def update_my_activity(
    user_activity_id: int,
    request: UserActivityUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_activity = get_user_activity_by_id(db, user_activity_id, current_user.id)
    if not user_activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Date validation: start_date cannot be after end_date
    new_start = request.start_date or user_activity.start_date
    new_end = request.end_date or user_activity.end_date
    if new_start and new_end and new_start > new_end:
        raise HTTPException(
            status_code=400, detail="start_date cannot be after end_date"
        )

    # PENDING: can edit custom_name, start_date, end_date, permission_proof, proof_description
    if user_activity.status_id == 1:
        if request.custom_name is not None:
            user_activity.custom_name = request.custom_name
        if request.start_date is not None:
            user_activity.start_date = request.start_date
        if request.end_date is not None:
            user_activity.end_date = request.end_date
        if request.permission_proof is not None:
            user_activity.permission_proof = request.permission_proof
        if request.proof_description is not None:
            user_activity.proof_description = request.proof_description

    # ONGOING: can edit start_date, end_date only
    elif user_activity.status_id == 2:
        if request.start_date is not None:
            user_activity.start_date = request.start_date
        if request.end_date is not None:
            user_activity.end_date = request.end_date

    # SUBMITTED/COMPLETED: cannot edit
    else:
        raise HTTPException(
            status_code=400, detail="Cannot edit activity after submission"
        )

    db.commit()
    db.refresh(user_activity)
    return user_activity


@router.put("/{user_activity_id}/proof", response_model=UserActivityResponse)
def submit_my_proof(
    user_activity_id: int,
    request: UserActivityProof,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = submit_proof(
        db=db,
        user_activity_id=user_activity_id,
        user_id=current_user.id,
        proof=request.proof,
        proof_description=request.proof_description,
        student_goal_id=request.student_goal_id,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    if result == "not_found":
        raise HTTPException(status_code=404, detail="Activity not found")
    if result == "invalid_status":
        raise HTTPException(
            status_code=400, detail="Can only submit proof when status is ONGOING"
        )
    if result == "student_goal_required":
        raise HTTPException(
            status_code=400, detail="Please select a category (student_goal_id)"
        )
    if result == "invalid_student_goal":
        raise HTTPException(status_code=400, detail="Invalid category selected")
    if result == "invalid_mapping":
        raise HTTPException(
            status_code=400, detail="Selected category does not match this activity"
        )
    if result == "Activity is locked. Contact teacher.":
        raise HTTPException(
            status_code=400, detail="Activity is locked. Contact teacher."
        )
    if result == "Submission limit exceeded. Activity locked.":
        raise HTTPException(
            status_code=400, detail="Submission limit exceeded. Activity locked."
        )
    return result


@router.post("/upload-permission-proof/{user_activity_id}")
async def upload_permission_proof(
    user_activity_id: int,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from database.crud.mapping.user_activity_mapping import get_user_activity_by_id

    validate_file(file)

    activity = get_user_activity_by_id(db, user_activity_id, current_user.id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Only allow upload at Pending status (1)
    if activity.status_id != 1:
        raise HTTPException(
            status_code=400, detail="Can only upload permission proof at Pending status"
        )

    upload_dir = Path(f"uploads/permission_proof/{current_user.id}")
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = str(upload_dir / f"{user_activity_id}_{file.filename}")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    activity.permission_proof = file_path
    db.commit()
    db.refresh(activity)

    return {"message": "Permission proof uploaded", "file_path": file_path}


@router.post("/upload-proof/{user_activity_id}")
async def upload_proof(
    user_activity_id: int,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from database.crud.mapping.user_activity_mapping import get_user_activity_by_id

    validate_file(file)

    activity = get_user_activity_by_id(db, user_activity_id, current_user.id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    if activity.status_id != 2:
        raise HTTPException(
            status_code=400, detail="Can only submit at In Progress status"
        )

    can_submit, msg = can_resubmit(db, user_activity_id)
    if not can_submit:
        raise HTTPException(status_code=400, detail=msg)

    upload_dir = Path(f"uploads/proof/{current_user.id}")
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = str(upload_dir / f"{user_activity_id}_{file.filename}")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    activity.proof_document = file_path
    activity.status_id = 3  # Submitted
    activity.submission_count += 1
    db.commit()
    db.refresh(activity)

    return {"message": "Proof submitted", "status": "Submitted"}


@router.post("/teacher-review/{activity_id}")
async def teacher_review_endpoint(
    activity_id: int,
    request: TeacherReviewRequest,
    current_user=Depends(require_staff),
    db: Session = Depends(get_db),
):
    result = teacher_review(
        db=db,
        activity_id=activity_id,
        teacher_user_id=current_user.id,
        action=request.action,
        reason=request.reason,
    )

    if result == "not_found":
        raise HTTPException(status_code=404, detail="Activity not found")
    if result == "You are not assigned to this student":
        raise HTTPException(
            status_code=403, detail="You are not assigned to this student"
        )
    if result == "invalid_status":
        raise HTTPException(
            status_code=400, detail="Can only review Pending or Submitted activities"
        )
    if result == "cannot_approve_without_submission":
        raise HTTPException(
            status_code=400,
            detail="Cannot approve. Student must submit certificate first.",
        )
    if result == "rejection_reason_required":
        raise HTTPException(
            status_code=400,
            detail="Rejection reason is required when rejecting from Submitted status",
        )
    if result == "invalid_action":
        raise HTTPException(
            status_code=400, detail="Invalid action. Use 'approve' or 'reject'"
        )

    return {
        "message": f"Activity {request.action}d",
        "status": result.status_id,
        "rejection_reason": result.rejection_reason,
        "tokens_earned": result.tokens_earned,
    }


@router.post("/{user_activity_id}/undelete", response_model=UserActivityResponse)
def undelete_activity(
    user_activity_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = undelete_user_activity(
        db=db,
        user_activity_id=user_activity_id,
        user_id=current_user.id,
    )
    if result == "not_found":
        raise HTTPException(status_code=404, detail="Activity not found")
    if result == "restored":
        activity = get_user_activity_by_id(db, user_activity_id, current_user.id)
        return activity
    raise HTTPException(status_code=400, detail="Failed to restore activity")


@router.delete("/{user_activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_activity(
    user_activity_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = delete_user_activity(
        db=db,
        user_activity_id=user_activity_id,
        user_id=current_user.id,
    )
    if result == "not_found":
        raise HTTPException(status_code=404, detail="Activity not found")
    if result == "invalid_status":
        raise HTTPException(
            status_code=400, detail="Can only delete when status is PENDING"
        )
    return None


@router.get("/", response_model=List[UserActivityResponse])
def get_my_activities(
    skip: int = 0,
    limit: int = 10,
    include_deleted: bool = False,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_activities(
        db, current_user.id, skip=skip, limit=limit, include_deleted=include_deleted
    )


@router.get("/teacher/students-activities", response_model=List[UserActivityResponse])
def get_teacher_students_activities(
    status_id: Optional[int] = None,
    current_user=Depends(require_staff),
    db: Session = Depends(get_db),
):
    """Get activities for all students assigned to the teacher"""
    activities = get_teacher_student_activities(db, current_user.id, status_id)
    return activities


@router.get("/{user_activity_id}", response_model=UserActivityResponse)
def get_my_activity(
    user_activity_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_activity = get_user_activity_by_id(db, user_activity_id, current_user.id)
    if not user_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return user_activity


# ============================================================================
# GET ALL STUDENTS FOR TEACHER
# ============================================================================
@router.get("/teacher/students", response_model=List[dict])
def get_teacher_students_endpoint(
    current_user=Depends(require_staff), db: Session = Depends(get_db)
):
    students = get_teacher_students(db, current_user.id)
    return [
        {
            "id": s.id,
            "register_no": s.register_no,
            "name": s.name,
            "email_id": s.email_id,
            "total_tokens": s.total_tokens,
            "is_active": s.is_active,
        }
        for s in students
    ]


# ============================================================================
# GET STUDENT PROFILE
# ============================================================================
@router.get("/teacher/students/{student_id}")
def get_student_profile_endpoint(
    student_id: int,
    current_user=Depends(require_staff),
    db: Session = Depends(get_db),
):
    student = get_student_profile(db, student_id, current_user.id)
    if not student:
        raise HTTPException(
            403, "You are not assigned to this student or student is inactive"
        )

    from database.models.master.program_dept_master import ProgramDeptMaster
    from database.models.master.gender_master import GenderMaster

    dept = (
        db.query(ProgramDeptMaster)
        .filter(ProgramDeptMaster.id == student.program_dept_id)
        .first()
    )
    gender = db.query(GenderMaster).filter(GenderMaster.id == student.gender_id).first()

    return {
        "id": student.id,
        "register_no": student.register_no,
        "name": student.name,
        "email_id": student.email_id,
        "contact_no": student.contact_no,
        "department": dept.branch if dept else None,
        "program": dept.program if dept else None,
        "semester": student.semester,
        "batch": f"{student.batch_start_year}-{student.batch_end_year}",
        "gender": gender.gender_name if gender else None,
        "blood_group": student.blood_grp,
        "github_url": student.github_url,
        "linkedin_url": student.linkedin_url,
        "total_tokens": student.total_tokens,
        "is_active": student.is_active,
    }


# ============================================================================
# GET STUDENT ACTIVITIES BY STATUS
# ============================================================================
@router.get("/teacher/students/{student_id}/activities")
def get_student_activities_by_status_endpoint(
    student_id: int,
    current_user=Depends(require_staff),
    db: Session = Depends(get_db),
):
    result = get_student_activities_by_status(db, student_id, current_user.id)
    if result is None:
        raise HTTPException(
            403, "You are not assigned to this student or student is inactive"
        )
    return result


# ============================================================================
# GET STUDENT GOALS
# ============================================================================
@router.get("/teacher/students/{student_id}/goals")
def get_student_goals_endpoint(
    student_id: int,
    current_user=Depends(require_staff),
    db: Session = Depends(get_db),
):
    from schemas.mapping.student_goal import StudentGoalResponse

    goals = get_student_goals(db, student_id, current_user.id)
    if goals is None:
        raise HTTPException(
            403, "You are not assigned to this student or student is inactive"
        )
    return goals


# ============================================================================
# APPLY MALPRACTICE
# ============================================================================
@router.post("/teacher/students/{student_id}/malpractice")
def apply_malpractice_endpoint(
    student_id: int,
    request: MalpracticeApply,
    current_user=Depends(require_staff),
    db: Session = Depends(get_db),
):
    result = apply_malpractice(
        db, student_id, current_user.id, request.malpractice_id, request.description
    )

    if result == "not_assigned":
        raise HTTPException(403, "You are not assigned to this student")
    if result == "student_not_found":
        raise HTTPException(404, "Student not found")
    if result == "student_inactive":
        raise HTTPException(400, "Cannot perform operation on inactive student")
    if result == "malpractice_not_found":
        raise HTTPException(404, "Malpractice type not found")
    if result == "insufficient_tokens":
        raise HTTPException(400, "Student does not have enough tokens")

    return {
        "message": "Malpractice applied successfully",
        "token_deducted": result.token_deducted,
        "remaining_tokens": result.student.total_tokens,
    }


# ============================================================================
# REVERSE SELECTED MALPRACTICE (Multiple)
# ============================================================================
@router.post("/teacher/students/{student_id}/malpractice/reverse-selected")
def reverse_selected_malpractice_endpoint(
    student_id: int,
    request: List[int],
    current_user=Depends(require_staff),
    db: Session = Depends(get_db),
):
    result = reverse_selected_malpractice(db, student_id, current_user.id, request)

    if result == "not_assigned":
        raise HTTPException(403, "You are not assigned to this student")
    if result == "student_not_found":
        raise HTTPException(404, "Student not found")
    if result == "student_inactive":
        raise HTTPException(400, "Cannot perform operation on inactive student")
    if result == "no_records_found":
        raise HTTPException(404, "No valid malpractice records found to reverse")

    return {
        "message": f"Successfully reversed {result['reversed_count']} malpractice record(s)",
        "tokens_returned": result["tokens_returned"],
        "remaining_tokens": result["remaining_tokens"],
    }


# ============================================================================
# GET STUDENT MALPRACTICE HISTORY
# ============================================================================
@router.get("/teacher/students/{student_id}/malpractice")
def get_student_malpractice_endpoint(
    student_id: int,
    current_user=Depends(require_staff),
    db: Session = Depends(get_db),
):
    incidents = get_student_malpractice(db, student_id, current_user.id)
    if incidents is None:
        raise HTTPException(
            403, "You are not assigned to this student or student is inactive"
        )

    result = []
    for incident in incidents:
        malpractice = (
            db.query(MalpracticeMaster)
            .filter(MalpracticeMaster.id == incident.malpractice_id)
            .first()
        )
        result.append(
            {
                "id": incident.id,
                "malpractice_name": malpractice.name if malpractice else "Unknown",
                "token_deducted": incident.token_deducted,
                "description": incident.description,
                "is_reversed": incident.is_reversed,
                "created_date": incident.created_date,
            }
        )

    return result
