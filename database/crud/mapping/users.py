# User CRUD operations
from sqlalchemy.orm import Session
from database.models.mapping.users import User
from database.models.mapping.staff_student_mapping import StaffStudentMapping
from database.models.master.program_dept_master import ProgramDeptMaster
from typing import Optional


def get_user_by_email(db: Session, email_id: str):
    return db.query(User).filter(User.email_id == email_id).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def update_external_links(db: Session, user_id: int, links: dict):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    for key, value in links.items():
        if value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def get_leaderboard(
    db: Session,
    department_id: Optional[int] = None,
    year: Optional[int] = None,
    section: Optional[str] = None,
    class_coordinator_id: Optional[int] = None,
    limit: int = 10,
    offset: int = 0,
):
    query = db.query(User).filter(User.role_id == 1, User.is_active == 1)

    if department_id:
        query = query.filter(User.program_dept_id == department_id)
    if year:
        query = query.filter(User.year == year)
    if section:
        query = query.filter(User.section == section)
    if class_coordinator_id:
        section_mapping = (
            db.query(StaffStudentMapping)
            .filter(
                StaffStudentMapping.staff_id == class_coordinator_id,
                StaffStudentMapping.mapping_type == "ClassCoordinator",
            )
            .first()
        )
        if section_mapping and section_mapping.section:
            query = query.filter(User.section == section_mapping.section)
        else:
            return [], 0

    total_count = query.count()
    results = query.order_by(User.total_tokens.desc()).offset(offset).limit(limit).all()

    leaderboard = []
    for i, user in enumerate(results):
        dept = (
            db.query(ProgramDeptMaster)
            .filter(ProgramDeptMaster.id == user.program_dept_id)
            .first()
        )
        year_str = (
            f"{user.year}{'st' if user.year == 1 else 'nd' if user.year == 2 else 'rd' if user.year == 3 else 'th'} Year"
            if user.year
            else None
        )
        leaderboard.append(
            {
                "rank": offset + i + 1,
                "student_id": user.id,
                "name": user.name,
                "register_no": user.register_no,
                "section": user.section,
                "department": dept.branch if dept else None,
                "year": year_str,
                "total_tokens": user.total_tokens,
            }
        )

    return leaderboard, total_count


def get_user_rank(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    higher_rank_count = (
        db.query(User)
        .filter(
            User.role_id == 1,
            User.is_active == 1,
            User.total_tokens > user.total_tokens,
        )
        .count()
    )

    return higher_rank_count + 1
