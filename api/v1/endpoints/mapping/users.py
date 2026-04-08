# User endpoints - login, profile, authentication
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from database.init_db import get_db
from database.crud.mapping.users import (
    get_user_by_email,
    get_user_by_id,
    get_leaderboard,
    get_user_rank,
)
from schemas.mapping.user import (
    LoginRequest,
    LoginResponse,
    UserInfo,
    LeaderboardEntry,
    LeaderboardResponse,
)
from schemas.mapping.user_token_mapping import (
    TokenSummaryResponse,
    TokenHistoryResponse,
    TokenTransactionResponse,
)
from core.auth import (
    create_access_token,
    get_current_user,
    require_admin,
    require_staff,
)

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
def login(request: Request, login_request: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email_id=login_request.email_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user.is_active == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive"
        )

    access_token = create_access_token(
        data={"user_id": user.id, "role_id": user.role_id}
    )
    return LoginResponse(
        access_token=access_token,
        user=UserInfo(
            id=user.id,
            name=user.name,
            email_id=user.email_id,
            role_id=user.role_id,
            is_active=user.is_active,
        ),
    )


@router.get("/me", response_model=UserInfo)
def get_my_profile(current_user=Depends(get_current_user)):
    return UserInfo(
        id=current_user.id,
        name=current_user.name,
        email_id=current_user.email_id,
        role_id=current_user.role_id,
        is_active=current_user.is_active,
    )


@router.get("/profile/full")
def get_my_full_profile(
    current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    user = get_user_by_id(db, user_id=current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {
        "id": user.id,
        "email_id": user.email_id,
        "name": user.name,
        "role_id": user.role_id,
        "gender_id": user.gender_id,
        "register_no": user.register_no,
        "staff_id": user.staff_id,
        "program_dept_id": user.program_dept_id,
        "year": user.year,
        "semester": user.semester,
        "cgpa": user.cgpa,
        "batch_start_year": user.batch_start_year,
        "batch_end_year": user.batch_end_year,
        "section": user.section,
        "contact_no": user.contact_no,
        "nationality": user.nationality,
        "mother_tongue": user.mother_tongue,
        "religion": user.religion,
        "community": user.community,
        "blood_grp": user.blood_grp,
        "birthdate": user.birthdate,
        "total_tokens": user.total_tokens,
        "github_url": user.github_url,
        "linkedin_url": user.linkedin_url,
        "leetcode_url": user.leetcode_url,
        "codeforces_url": user.codeforces_url,
        "hackerrank_url": user.hackerrank_url,
        "is_active": user.is_active,
    }


@router.get("/all")
def get_all_users(current_user=Depends(require_admin), db: Session = Depends(get_db)):
    from database.models.mapping.users import User

    users = db.query(User).filter(User.is_active == 1).all()
    return [
        UserInfo(
            id=u.id,
            name=u.name,
            email_id=u.email_id,
            role_id=u.role_id,
            is_active=u.is_active,
        )
        for u in users
    ]


# ============================================================================
# TOKEN ENDPOINTS
# ============================================================================


@router.get("/tokens", response_model=TokenSummaryResponse)
def get_my_token_summary(
    current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's token summary"""
    from database.models.mapping.user_token_mapping import UserTokenMapping
    from database.models.mapping.users import User

    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    transactions = (
        db.query(UserTokenMapping)
        .filter(UserTokenMapping.user_id == current_user.id)
        .all()
    )

    earned = sum(t.token_amount for t in transactions if t.token_amount > 0)
    spent = abs(sum(t.token_amount for t in transactions if t.token_amount < 0))

    breakdown = {
        "activity_completed": sum(
            t.token_amount
            for t in transactions
            if t.transaction_type == "Activity Completed"
        ),
        "malpractice_deducted": abs(
            sum(
                t.token_amount
                for t in transactions
                if t.transaction_type == "Malpractice Deduction"
            )
        ),
        "malpractice_reversed": sum(
            t.token_amount
            for t in transactions
            if t.transaction_type == "Malpractice Reversed"
        ),
    }

    return TokenSummaryResponse(
        total_tokens=user.total_tokens,
        earned=earned,
        spent=spent,
        breakdown=breakdown,
    )


@router.get("/tokens/transactions", response_model=TokenHistoryResponse)
def get_my_token_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's token transaction history"""
    from database.models.mapping.user_token_mapping import UserTokenMapping

    query = (
        db.query(UserTokenMapping)
        .filter(UserTokenMapping.user_id == current_user.id)
        .order_by(UserTokenMapping.created_date.desc())
    )

    total_count = query.count()
    offset = (page - 1) * limit
    transactions = query.offset(offset).limit(limit).all()

    return TokenHistoryResponse(
        transactions=[
            TokenTransactionResponse(
                id=t.id,
                user_id=t.user_id,
                token_amount=t.token_amount,
                transaction_type=t.transaction_type,
                description=t.description,
                reference_id=t.reference_id,
                created_date=t.created_date,
            )
            for t in transactions
        ],
        total_count=total_count,
        page=page,
        limit=limit,
    )


# ============================================================================
# TEACHER: GET STUDENT TOKEN HISTORY
# ============================================================================


@router.get("/students/{student_id}/tokens", response_model=TokenSummaryResponse)
def get_student_token_summary(
    student_id: int,
    current_user=Depends(require_staff),
    db: Session = Depends(get_db),
):
    """Get assigned student's token summary (teacher only)"""
    from database.models.mapping.user_token_mapping import UserTokenMapping
    from database.models.mapping.users import User
    from database.crud.mapping.user_activity_mapping import validate_teacher_access

    valid, msg = validate_teacher_access(db, current_user.id, student_id)
    if not valid:
        raise HTTPException(status_code=403, detail=msg)

    user = db.query(User).filter(User.id == student_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    transactions = (
        db.query(UserTokenMapping).filter(UserTokenMapping.user_id == student_id).all()
    )

    earned = sum(t.token_amount for t in transactions if t.token_amount > 0)
    spent = abs(sum(t.token_amount for t in transactions if t.token_amount < 0))

    breakdown = {
        "activity_completed": sum(
            t.token_amount
            for t in transactions
            if t.transaction_type == "Activity Completed"
        ),
        "malpractice_deducted": abs(
            sum(
                t.token_amount
                for t in transactions
                if t.transaction_type == "Malpractice Deduction"
            )
        ),
        "malpractice_reversed": sum(
            t.token_amount
            for t in transactions
            if t.transaction_type == "Malpractice Reversed"
        ),
    }

    return TokenSummaryResponse(
        total_tokens=user.total_tokens,
        earned=earned,
        spent=spent,
        breakdown=breakdown,
    )


@router.get(
    "/students/{student_id}/tokens/transactions", response_model=TokenHistoryResponse
)
def get_student_token_transactions(
    student_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user=Depends(require_staff),
    db: Session = Depends(get_db),
):
    """Get assigned student's token transaction history (teacher only)"""
    from database.models.mapping.user_token_mapping import UserTokenMapping
    from database.crud.mapping.user_activity_mapping import validate_teacher_access

    valid, msg = validate_teacher_access(db, current_user.id, student_id)
    if not valid:
        raise HTTPException(status_code=403, detail=msg)

    query = (
        db.query(UserTokenMapping)
        .filter(UserTokenMapping.user_id == student_id)
        .order_by(UserTokenMapping.created_date.desc())
    )

    total_count = query.count()
    offset = (page - 1) * limit
    transactions = query.offset(offset).limit(limit).all()

    return TokenHistoryResponse(
        transactions=[
            TokenTransactionResponse(
                id=t.id,
                user_id=t.user_id,
                token_amount=t.token_amount,
                transaction_type=t.transaction_type,
                description=t.description,
                reference_id=t.reference_id,
                created_date=t.created_date,
            )
            for t in transactions
        ],
        total_count=total_count,
        page=page,
        limit=limit,
    )


# ============================================================================
# LEADERBOARD ENDPOINTS
# ============================================================================


@router.get("/leaderboard", response_model=LeaderboardResponse)
def get_global_leaderboard(
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    year: Optional[int] = Query(None, description="Filter by year (1, 2, 3, 4)"),
    section: Optional[str] = Query(
        None, description="Filter by section (e.g., A1, B2)"
    ),
    class_coordinator_id: Optional[int] = Query(
        None, description="Filter by class coordinator (teacher) ID"
    ),
    limit: int = Query(10, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get global leaderboard with optional filters (accessible by all authenticated users)"""
    leaderboard, total_count = get_leaderboard(
        db=db,
        department_id=department_id,
        year=year,
        section=section,
        class_coordinator_id=class_coordinator_id,
        limit=limit,
        offset=offset,
    )

    return LeaderboardResponse(
        leaderboard=[LeaderboardEntry(**entry) for entry in leaderboard],
        total_count=total_count,
    )


@router.get("/leaderboard/me")
def get_my_rank(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user's rank in the leaderboard"""
    rank = get_user_rank(db, current_user.id)
    if rank is None:
        raise HTTPException(status_code=404, detail="User not found")

    user = get_user_by_id(db, current_user.id)

    return {
        "rank": rank,
        "total_tokens": user.total_tokens,
        "name": user.name,
        "section": user.section,
    }


@router.get(
    "/leaderboard/class-coordinator/{teacher_id}", response_model=LeaderboardResponse
)
def get_class_coordinator_leaderboard(
    teacher_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get leaderboard for a specific class coordinator (teacher)"""
    leaderboard, total_count = get_leaderboard(
        db=db,
        class_coordinator_id=teacher_id,
        limit=limit,
        offset=offset,
    )

    return LeaderboardResponse(
        leaderboard=[LeaderboardEntry(**entry) for entry in leaderboard],
        total_count=total_count,
    )
