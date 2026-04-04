import argparse
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from tqdm import tqdm

    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    tqdm = lambda x, **kwargs: x

from database.init_db import SessionLocal, engine
from database.models.base import Base
from database.models.master.activity_type_master import ActivityTypeMaster
from database.models.master.application_config import ApplicationConfig
from database.models.master.event_master import EventMaster
from database.models.master.gender import Gender
from database.models.master.malpractice_master import MalpracticeMaster
from database.models.master.program_dept_master import ProgramDeptMaster
from database.models.master.roles import Role
from database.models.master.stage import Stage
from database.models.master.status import Status
from database.models.master.workflow import Workflow
from database.models.mapping.activity import Activity
from database.models.mapping.staff_student_mapping import StaffStudentMapping
from database.models.mapping.student_goal import StudentGoal
from database.models.mapping.user_activity_mapping import UserActivityMapping
from database.models.mapping.user_token_mapping import UserTokenMapping
from database.models.mapping.users import User
from database.models.mapping.workflow_stage_mapping import WorkflowStageMapping


DELETE_ORDER = [
    UserActivityMapping,
    StudentGoal,
    UserTokenMapping,
    StaffStudentMapping,
    User,
    Activity,
    WorkflowStageMapping,
    Stage,
    Workflow,
    Status,
    ActivityTypeMaster,
    EventMaster,
    MalpracticeMaster,
    ApplicationConfig,
    ProgramDeptMaster,
    Gender,
    Role,
]

SEED_FUNCTIONS = []


def register_seed(model_name: str):
    def decorator(func):
        func._model_name = model_name
        SEED_FUNCTIONS.append(func)
        return func

    return decorator


@register_seed("roles_master")
def seed_roles(db):
    roles = [
        Role(role_name="Student"),
        Role(role_name="Staff"),
        Role(role_name="Admin"),
    ]
    for role in roles:
        db.add(role)
    db.commit()
    return roles


@register_seed("gender_master")
def seed_gender(db):
    genders = [
        Gender(name="Male"),
        Gender(name="Female"),
    ]
    for gender in genders:
        db.add(gender)
    db.commit()
    return genders


@register_seed("program_dept_master")
def seed_program_dept(db):
    programs = [
        ProgramDeptMaster(program="B.Tech", branch="Computer Science"),
        ProgramDeptMaster(program="B.Tech", branch="Electronics and Communication"),
        ProgramDeptMaster(program="B.Sc", branch="Mathematics"),
    ]
    for program in programs:
        db.add(program)
    db.commit()
    return programs


@register_seed("activity_type_master")
def seed_activity_types(db):
    types = [
        ActivityTypeMaster(type_name="Technical"),
        ActivityTypeMaster(type_name="Cultural"),
        ActivityTypeMaster(type_name="Sports"),
    ]
    for t in types:
        db.add(t)
    db.commit()
    return types


@register_seed("workflow_master")
def seed_workflows(db):
    workflows = [
        Workflow(name="Standard"),
        Workflow(name="Fast-Track"),
    ]
    for w in workflows:
        db.add(w)
    db.commit()
    return workflows


@register_seed("stage_master")
def seed_stages(db):
    standard_wf = db.query(Workflow).filter(Workflow.name == "Standard").first()
    fasttrack_wf = db.query(Workflow).filter(Workflow.name == "Fast-Track").first()

    stages = [
        Stage(
            name="Submission",
            permission_upload=True,
            ai_proof_verification=True,
            manual_proof_verification=True,
        ),
        Stage(
            name="Review",
            ai_permission_verification=True,
            manual_permission_verification=True,
            event_progress=True,
        ),
        Stage(name="Approved", activity_completed=True),
    ]

    standard_stages = []
    fasttrack_stages = []

    for i, stage in enumerate(stages):
        stage_copy_1 = Stage(
            name=stage.name,
            permission_upload=stage.permission_upload,
            ai_permission_verification=stage.ai_permission_verification,
            manual_permission_verification=stage.manual_permission_verification,
            event_progress=stage.event_progress,
            ai_proof_verification=stage.ai_proof_verification,
            manual_proof_verification=stage.manual_proof_verification,
            activity_completed=stage.activity_completed,
        )
        stage_copy_2 = Stage(
            name=stage.name,
            permission_upload=stage.permission_upload,
            ai_permission_verification=stage.ai_permission_verification,
            manual_permission_verification=stage.manual_permission_verification,
            event_progress=stage.event_progress,
            ai_proof_verification=stage.ai_proof_verification,
            manual_proof_verification=stage.manual_proof_verification,
            activity_completed=stage.activity_completed,
        )
        db.add(stage_copy_1)
        db.add(stage_copy_2)
        standard_stages.append(stage_copy_1)
        fasttrack_stages.append(stage_copy_2)

    db.commit()

    wf_stages = []
    for i, (s, f) in enumerate(zip(standard_stages, fasttrack_stages)):
        wf_stages.append((standard_wf, s, i + 1))
        wf_stages.append((fasttrack_wf, f, i + 1))

    return standard_stages, fasttrack_stages, wf_stages


@register_seed("status_master")
def seed_status(db):
    statuses = [
        Status(name="Pending"),
        Status(name="In Progress"),
        Status(name="Approved"),
        Status(name="Rejected"),
    ]
    for status in statuses:
        db.add(status)
    db.commit()
    return statuses


@register_seed("event_master")
def seed_events(db):
    events = [
        EventMaster(name="Tech Fest 2026"),
        EventMaster(name="Cultural Week"),
    ]
    for event in events:
        db.add(event)
    db.commit()
    return events


@register_seed("malpractice_master")
def seed_malpractice(db):
    malpractice = [
        MalpracticeMaster(name="Plagiarism", token_deduction=10),
        MalpracticeMaster(name="Fake Evidence", token_deduction=15),
    ]
    for m in malpractice:
        db.add(m)
    db.commit()
    return malpractice


@register_seed("application_config")
def seed_config(db):
    config = ApplicationConfig(config_name="app_name", config_value="SkillStack")
    db.add(config)
    db.commit()
    return config


@register_seed("users")
def seed_users(db):
    role_student = db.query(Role).filter(Role.role_name == "Student").first()
    role_staff = db.query(Role).filter(Role.role_name == "Staff").first()
    gender_male = db.query(Gender).filter(Gender.name == "Male").first()
    gender_female = db.query(Gender).filter(Gender.name == "Female").first()
    program_cs = (
        db.query(ProgramDeptMaster)
        .filter(
            ProgramDeptMaster.program == "B.Tech",
            ProgramDeptMaster.branch == "Computer Science",
        )
        .first()
    )
    program_ece = (
        db.query(ProgramDeptMaster)
        .filter(
            ProgramDeptMaster.program == "B.Tech",
            ProgramDeptMaster.branch == "Electronics and Communication",
        )
        .first()
    )

    users = [
        User(
            role_id=role_student.id,
            gender_id=gender_male.id,
            register_no=1001,
            program_dept_id=program_cs.id,
            year=3,
            semester=6,
            batch_start_year=2023,
            batch_end_year=2027,
            email_id="arun.kumar@college.edu",
            contact_no="9876543210",
            name="Arun Kumar",
            nationality="Indian",
            birthdate=date(2003, 5, 15),
            total_tokens=0,
        ),
        User(
            role_id=role_student.id,
            gender_id=gender_female.id,
            register_no=1002,
            program_dept_id=program_cs.id,
            year=3,
            semester=6,
            batch_start_year=2023,
            batch_end_year=2027,
            email_id="priya.sharma@college.edu",
            contact_no="9876543211",
            name="Priya Sharma",
            nationality="Indian",
            birthdate=date(2004, 8, 22),
            total_tokens=0,
        ),
        User(
            role_id=role_student.id,
            gender_id=gender_male.id,
            register_no=1003,
            program_dept_id=program_ece.id,
            year=2,
            semester=4,
            batch_start_year=2024,
            batch_end_year=2028,
            email_id="rahul.verma@college.edu",
            contact_no="9876543212",
            name="Rahul Verma",
            nationality="Indian",
            birthdate=date(2004, 1, 10),
            total_tokens=0,
        ),
        User(
            role_id=role_student.id,
            gender_id=gender_female.id,
            register_no=1004,
            program_dept_id=program_cs.id,
            year=4,
            semester=8,
            batch_start_year=2022,
            batch_end_year=2026,
            email_id="sneha.reddy@college.edu",
            contact_no="9876543213",
            name="Sneha Reddy",
            nationality="Indian",
            birthdate=date(2002, 11, 3),
            total_tokens=0,
        ),
        User(
            role_id=role_staff.id,
            gender_id=gender_male.id,
            staff_id="FAC001",
            email_id="dr.ravi.krishna@college.edu",
            contact_no="9876543214",
            name="Dr. Ravi Krishna",
            nationality="Indian",
            total_tokens=0,
        ),
        User(
            role_id=role_staff.id,
            gender_id=gender_female.id,
            staff_id="FAC002",
            email_id="prof.meera.sen@college.edu",
            contact_no="9876543215",
            name="Prof. Meera Sen",
            nationality="Indian",
            total_tokens=0,
        ),
    ]

    for user in users:
        db.add(user)
    db.commit()
    return users


@register_seed("activity_master")
def seed_activities(db):
    type_technical = (
        db.query(ActivityTypeMaster)
        .filter(ActivityTypeMaster.type_name == "Technical")
        .first()
    )
    type_cultural = (
        db.query(ActivityTypeMaster)
        .filter(ActivityTypeMaster.type_name == "Cultural")
        .first()
    )
    type_sports = (
        db.query(ActivityTypeMaster)
        .filter(ActivityTypeMaster.type_name == "Sports")
        .first()
    )
    workflow = db.query(Workflow).filter(Workflow.name == "Standard").first()

    activities = [
        Activity(
            activity_name="NPTEL-Pass",
            token=2,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="NPTEL-Elite+Silver",
            token=3,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="NPTEL-Elite+Gold",
            token=4,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Coursera",
            token=4,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Udemy",
            token=3,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Workshop",
            token=2,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Hackathon-Participate",
            token=3,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Hackathon(Internal)-Win",
            token=4,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Hackathon(External)-Win",
            token=6,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Other College Events",
            token=3,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Organizing Events",
            token=2,
            activity_type_id=type_cultural.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Cultural",
            token=3,
            activity_type_id=type_cultural.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Sports/Music",
            token=3,
            activity_type_id=type_sports.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="NCC/NSS Activities",
            token=3,
            activity_type_id=type_sports.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Volunteer Activities",
            token=3,
            activity_type_id=type_cultural.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Value Added Courses",
            token=4,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Internship-Online",
            token=4,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Internship-InOffice",
            token=6,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Certification-Internal/Local",
            token=4,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Certification-Global",
            token=6,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Research Working Prototype",
            token=6,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Coding-Contest-Participation",
            token=3,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Coding-Contest-Winner",
            token=5,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Research-paper",
            token=4,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Best Paper Award",
            token=6,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Research Resource Person(Internal)",
            token=3,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Research Resource Person(External)",
            token=5,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Study Abroad",
            token=6,
            activity_type_id=type_cultural.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Seed Funding Project",
            token=8,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="Startup",
            token=12,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        Activity(
            activity_name="CGPA 8.5 And Above",
            token=4,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
    ]

    for activity in activities:
        db.add(activity)
    db.commit()
    return activities


@register_seed("workflow_stage_mapping")
def seed_workflow_stages(db, wf_stages_data):
    mappings = []
    for wf, stage, order in wf_stages_data:
        mapping = WorkflowStageMapping(
            workflow_id=wf.id,
            stage_id=stage.id,
            stage_order=order,
        )
        db.add(mapping)
        mappings.append(mapping)
    db.commit()
    return mappings


@register_seed("staff_student_mapping")
def seed_staff_student(db):
    staff = db.query(User).filter(User.staff_id == "FAC001").first()
    student = db.query(User).filter(User.register_no == 1001).first()

    mapping = StaffStudentMapping(
        staff_id=staff.id,
        student_id=student.id,
        mapping_type="Mentor",
    )
    db.add(mapping)
    db.commit()
    return mapping


@register_seed("user_activity_mapping")
def seed_user_activities(db):
    student1 = db.query(User).filter(User.email_id == "arun.kumar@college.edu").first()
    student2 = (
        db.query(User).filter(User.email_id == "priya.sharma@college.edu").first()
    )
    student3 = db.query(User).filter(User.email_id == "rahul.verma@college.edu").first()
    student4 = db.query(User).filter(User.email_id == "sneha.reddy@college.edu").first()

    nptel_pass = (
        db.query(Activity).filter(Activity.activity_name == "NPTEL-Pass").first()
    )
    nptel_gold = (
        db.query(Activity).filter(Activity.activity_name == "NPTEL-Elite+Gold").first()
    )
    hackathon_win = (
        db.query(Activity)
        .filter(Activity.activity_name == "Hackathon(Internal)-Win")
        .first()
    )
    workshop = db.query(Activity).filter(Activity.activity_name == "Workshop").first()
    cgpa_activity = (
        db.query(Activity)
        .filter(Activity.activity_name == "CGPA 8.5 And Above")
        .first()
    )
    internship = (
        db.query(Activity)
        .filter(Activity.activity_name == "Internship-InOffice")
        .first()
    )

    status_approved = db.query(Status).filter(Status.name == "Approved").first()
    status_pending = db.query(Status).filter(Status.name == "Pending").first()

    stage_approved = db.query(Stage).filter(Stage.name == "Approved").first()
    stage_submission = db.query(Stage).filter(Stage.name == "Submission").first()

    today = date.today()

    user_activities = [
        UserActivityMapping(
            user_id=student1.id,
            activity_id=nptel_pass.id,
            status_id=status_approved.id,
            current_stage_id=stage_approved.id,
            tokens_earned=nptel_pass.token,
            start_date=today - timedelta(days=30),
            end_date=today - timedelta(days=15),
        ),
        UserActivityMapping(
            user_id=student1.id,
            activity_id=hackathon_win.id,
            status_id=status_approved.id,
            current_stage_id=stage_approved.id,
            tokens_earned=hackathon_win.token,
            start_date=today - timedelta(days=20),
            end_date=today - timedelta(days=10),
        ),
        UserActivityMapping(
            user_id=student2.id,
            activity_id=nptel_gold.id,
            status_id=status_approved.id,
            current_stage_id=stage_approved.id,
            tokens_earned=nptel_gold.token,
            start_date=today - timedelta(days=45),
            end_date=today - timedelta(days=20),
        ),
        UserActivityMapping(
            user_id=student3.id,
            activity_id=workshop.id,
            status_id=status_pending.id,
            current_stage_id=stage_submission.id,
            tokens_earned=0,
            start_date=today - timedelta(days=5),
            end_date=None,
        ),
    ]

    for ua in user_activities:
        db.add(ua)
    db.commit()
    return user_activities


@register_seed("user_token_mapping")
def seed_user_tokens(db):
    user1 = db.query(User).filter(User.email_id == "arun.kumar@college.edu").first()
    user2 = db.query(User).filter(User.email_id == "priya.sharma@college.edu").first()

    ua1 = (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.user_id == user1.id,
            UserActivityMapping.tokens_earned > 0,
        )
        .first()
    )
    ua2 = (
        db.query(UserActivityMapping)
        .filter(
            UserActivityMapping.user_id == user1.id, UserActivityMapping.id != ua1.id
        )
        .first()
    )
    ua3 = (
        db.query(UserActivityMapping)
        .filter(UserActivityMapping.user_id == user2.id)
        .first()
    )

    tokens = [
        UserTokenMapping(
            user_id=user1.id,
            token_amount=ua1.tokens_earned,
            transaction_type="Earned",
            description=f"Completed: {ua1.activity_id}",
            reference_id=ua1.id,
        ),
        UserTokenMapping(
            user_id=user1.id,
            token_amount=ua2.tokens_earned,
            transaction_type="Earned",
            description=f"Completed: {ua2.activity_id}",
            reference_id=ua2.id,
        ),
        UserTokenMapping(
            user_id=user2.id,
            token_amount=ua3.tokens_earned,
            transaction_type="Earned",
            description=f"Completed: {ua3.activity_id}",
            reference_id=ua3.id,
        ),
    ]

    for token in tokens:
        db.add(token)
    db.commit()
    return tokens


@register_seed("student_goal")
def seed_student_goals(db):
    student = db.query(User).filter(User.email_id == "arun.kumar@college.edu").first()
    hackathon = (
        db.query(Activity)
        .filter(Activity.activity_name == "Hackathon(External)-Win")
        .first()
    )
    internship = (
        db.query(Activity)
        .filter(Activity.activity_name == "Internship-InOffice")
        .first()
    )
    status_pending = db.query(Status).filter(Status.name == "Pending").first()

    goals = [
        StudentGoal(
            user_id=student.id,
            activity_id=hackathon.id,
            goal_name="Win External Hackathon",
            target_tokens=6,
            current_tokens=0,
            deadline=date(2026, 12, 31),
            status_id=status_pending.id,
        ),
        StudentGoal(
            user_id=student.id,
            activity_id=internship.id,
            goal_name="Complete In-Office Internship",
            target_tokens=6,
            current_tokens=0,
            deadline=date(2026, 6, 30),
            status_id=status_pending.id,
        ),
    ]

    for goal in goals:
        db.add(goal)
    db.commit()
    return goals


def update_user_totals(db):
    users = db.query(User).all()
    for user in tqdm(users, desc="Updating user totals"):
        total = (
            db.query(UserTokenMapping).filter(UserTokenMapping.user_id == user.id).all()
        )
        total_tokens = sum(t.token_amount for t in total)
        user.total_tokens = total_tokens
    db.commit()


def reset_database(db):
    print("Resetting database...")
    for table in DELETE_ORDER:
        db.query(table).delete()
        db.commit()
    print("Database reset complete.\n")


def main():
    parser = argparse.ArgumentParser(description="Seed the database with initial data")
    parser.add_argument(
        "--fresh", action="store_true", help="Clear all tables before seeding"
    )
    args = parser.parse_args()

    db = SessionLocal()

    try:
        if args.fresh:
            reset_database(db)

        print(f"Seeding {len(SEED_FUNCTIONS)} tables...\n")

        for func in tqdm(SEED_FUNCTIONS, desc="Seeding tables"):
            func(db)

        update_user_totals(db)

        print("\nSeeding complete!")
        print(
            "\nSeeded tables: " + ", ".join(func._model_name for func in SEED_FUNCTIONS)
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()
