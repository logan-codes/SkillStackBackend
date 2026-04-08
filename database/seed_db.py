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

from sqlalchemy import text
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
from database.models.master.activity_master import ActivityMaster
from database.models.master.student_goal_master import StudentGoalMaster
from database.models.mapping.activity_studentgoal_mapping import (
    ActivityStudentGoalMapping,
)
from database.models.mapping.student_goal import StudentGoal
from database.models.mapping.user_activity_mapping import UserActivityMapping
from database.models.mapping.user_token_mapping import UserTokenMapping
from database.models.mapping.users import User
from database.models.mapping.workflow_stage_mapping import WorkflowStageMapping
from database.models.mapping.staff_student_mapping import StaffStudentMapping


DELETE_ORDER = [
    UserActivityMapping,
    StudentGoal,
    ActivityStudentGoalMapping,
    UserTokenMapping,
    StaffStudentMapping,
    User,
    StudentGoalMaster,
    ActivityMaster,
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
        Status(name="Pending"),  # 1
        Status(name="In Progress"),  # 2
        Status(name="Submitted"),  # 3 (NEW)
        Status(name="Completed"),  # 4 (was Approved)
        Status(name="Rejected"),  # 5 (was Rejected)
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
        # CSE 3rd Year Section A
        User(
            role_id=role_student.id,
            gender_id=gender_male.id,
            register_no=1001,
            program_dept_id=program_cs.id,
            year=3,
            semester=6,
            section="A",
            email_id="arun.kumar@college.edu",
            contact_no="9876543210",
            name="Arun Kumar",
            nationality="Indian",
            birthdate=date(2003, 5, 15),
            total_tokens=25,
        ),
        User(
            role_id=role_student.id,
            gender_id=gender_female.id,
            register_no=1002,
            program_dept_id=program_cs.id,
            year=3,
            semester=6,
            section="A",
            email_id="priya.sharma@college.edu",
            contact_no="9876543211",
            name="Priya Sharma",
            nationality="Indian",
            birthdate=date(2004, 8, 22),
            total_tokens=30,
        ),
        # CSE 3rd Year Section B
        User(
            role_id=role_student.id,
            gender_id=gender_male.id,
            register_no=1003,
            program_dept_id=program_cs.id,
            year=3,
            semester=6,
            section="B",
            email_id="rahul.verma@college.edu",
            contact_no="9876543212",
            name="Rahul Verma",
            nationality="Indian",
            birthdate=date(2004, 1, 10),
            total_tokens=20,
        ),
        User(
            role_id=role_student.id,
            gender_id=gender_female.id,
            register_no=1004,
            program_dept_id=program_cs.id,
            year=3,
            semester=6,
            section="B",
            email_id="sneha.reddy@college.edu",
            contact_no="9876543213",
            name="Sneha Reddy",
            nationality="Indian",
            birthdate=date(2004, 3, 25),
            total_tokens=18,
        ),
        # CSE 2nd Year Section A
        User(
            role_id=role_student.id,
            gender_id=gender_male.id,
            register_no=1005,
            program_dept_id=program_cs.id,
            year=2,
            semester=4,
            section="A",
            email_id="amit.patel@college.edu",
            contact_no="9876543214",
            name="Amit Patel",
            nationality="Indian",
            birthdate=date(2005, 6, 12),
            total_tokens=15,
        ),
        User(
            role_id=role_student.id,
            gender_id=gender_female.id,
            register_no=1006,
            program_dept_id=program_cs.id,
            year=2,
            semester=4,
            section="A",
            email_id="divya.singh@college.edu",
            contact_no="9876543215",
            name="Divya Singh",
            nationality="Indian",
            birthdate=date(2005, 9, 8),
            total_tokens=22,
        ),
        # ECE 2nd Year Section A
        User(
            role_id=role_student.id,
            gender_id=gender_male.id,
            register_no=2001,
            program_dept_id=program_ece.id,
            year=2,
            semester=4,
            section="A",
            email_id="karthik.nair@college.edu",
            contact_no="9876543216",
            name="Karthik Nair",
            nationality="Indian",
            birthdate=date(2005, 2, 18),
            total_tokens=12,
        ),
        User(
            role_id=role_student.id,
            gender_id=gender_female.id,
            register_no=2002,
            program_dept_id=program_ece.id,
            year=2,
            semester=4,
            section="A",
            email_id="neha.iyer@college.edu",
            contact_no="9876543217",
            name="Neha Iyer",
            nationality="Indian",
            birthdate=date(2005, 7, 30),
            total_tokens=28,
        ),
        # Staff - Class Coordinators
        User(
            role_id=role_staff.id,
            gender_id=gender_male.id,
            staff_id="FAC001",
            email_id="dr.ravi.krishna@college.edu",
            contact_no="9876543218",
            name="Dr. Ravi Krishna",
            nationality="Indian",
            total_tokens=0,
        ),
        User(
            role_id=role_staff.id,
            gender_id=gender_female.id,
            staff_id="FAC002",
            email_id="prof.meera.sen@college.edu",
            contact_no="9876543219",
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
    """Seed generic activities for workflow (activity_master table)"""
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

    # Generic activities for workflow with activity limits
    activities = [
        ActivityMaster(
            activity_name="NPTEL",
            activity_type_id=type_technical.id,
            activity_limit=5,
        ),
        ActivityMaster(
            activity_name="Coursera",
            activity_type_id=type_technical.id,
            activity_limit=5,
        ),
        ActivityMaster(
            activity_name="Udemy",
            activity_type_id=type_technical.id,
            activity_limit=5,
        ),
        ActivityMaster(
            activity_name="Workshop",
            activity_type_id=type_technical.id,
            activity_limit=3,
        ),
        ActivityMaster(
            activity_name="Hackathon",
            activity_type_id=type_technical.id,
            activity_limit=3,
        ),
        ActivityMaster(
            activity_name="Other College Events",
            activity_type_id=type_technical.id,
            activity_limit=3,
        ),
        ActivityMaster(
            activity_name="Organizing Events",
            activity_type_id=type_cultural.id,
            activity_limit=3,
        ),
        ActivityMaster(
            activity_name="Cultural",
            activity_type_id=type_cultural.id,
            activity_limit=2,
        ),
        ActivityMaster(
            activity_name="Sports/Music",
            activity_type_id=type_sports.id,
            activity_limit=2,
        ),
        ActivityMaster(
            activity_name="NCC/NSS Activities",
            activity_type_id=type_sports.id,
            activity_limit=2,
        ),
        ActivityMaster(
            activity_name="Volunteer Activities",
            activity_type_id=type_cultural.id,
            activity_limit=2,
        ),
        ActivityMaster(
            activity_name="Value Added Courses",
            activity_type_id=type_technical.id,
            activity_limit=3,
        ),
        ActivityMaster(
            activity_name="Internship",
            activity_type_id=type_technical.id,
            activity_limit=2,
        ),
        ActivityMaster(
            activity_name="Certification",
            activity_type_id=type_technical.id,
            activity_limit=3,
        ),
        ActivityMaster(
            activity_name="Research Working Prototype",
            activity_type_id=type_technical.id,
            activity_limit=2,
        ),
        ActivityMaster(
            activity_name="Coding-Contest",
            activity_type_id=type_technical.id,
            activity_limit=5,
        ),
        ActivityMaster(
            activity_name="Research-paper",
            activity_type_id=type_technical.id,
            activity_limit=2,
        ),
        ActivityMaster(
            activity_name="Best Paper Award",
            activity_type_id=type_technical.id,
            activity_limit=2,
        ),
        ActivityMaster(
            activity_name="Research Resource Person",
            activity_type_id=type_technical.id,
            activity_limit=2,
        ),
        ActivityMaster(
            activity_name="Study Abroad",
            activity_type_id=type_cultural.id,
            activity_limit=1,
        ),
        ActivityMaster(
            activity_name="Seed Funding Project",
            activity_type_id=type_technical.id,
            activity_limit=1,
        ),
        ActivityMaster(
            activity_name="Startup",
            activity_type_id=type_technical.id,
            activity_limit=1,
        ),
        ActivityMaster(
            activity_name="CGPA",
            activity_type_id=type_technical.id,
            activity_limit=1,
        ),
    ]

    for activity in activities:
        db.add(activity)
    db.commit()
    return activities


@register_seed("student_goal_master")
def seed_student_goal_master(db):
    """Seed activities for student goals (student_goal_master table)"""
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

    # Student goal activities (specific outcomes - tokens only)
    student_goals = [
        StudentGoalMaster(
            activity_name="NPTEL-Pass",
            token=2,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="NPTEL-Elite+Silver",
            token=3,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="NPTEL-Elite+Gold",
            token=4,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Coursera",
            token=4,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Udemy",
            token=3,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Workshop",
            token=2,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Hackathon-Participate",
            token=3,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Hackathon(Internal)-Win",
            token=4,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Hackathon(External)-Win",
            token=6,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Other College Events",
            token=3,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Organizing Events",
            token=2,
            activity_type_id=type_cultural.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Cultural",
            token=3,
            activity_type_id=type_cultural.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Sports/Music",
            token=3,
            activity_type_id=type_sports.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="NCC/NSS Activities",
            token=3,
            activity_type_id=type_sports.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Volunteer Activities",
            token=3,
            activity_type_id=type_cultural.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Value Added Courses",
            token=4,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Internship-Online",
            token=4,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Internship-InOffice",
            token=6,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Certification-Internal/Local",
            token=4,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Certification-Global",
            token=6,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Research Working Prototype",
            token=6,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Coding-Contest-Participation",
            token=3,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Coding-Contest-Winner",
            token=5,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Research-paper",
            token=4,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Best Paper Award",
            token=6,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Research Resource Person(Internal)",
            token=3,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Research Resource Person(External)",
            token=5,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Study Abroad",
            token=6,
            activity_type_id=type_cultural.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Seed Funding Project",
            token=8,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="Startup",
            token=12,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
        StudentGoalMaster(
            activity_name="CGPA 8.5 And Above",
            token=4,
            activity_type_id=type_technical.id,
            workflow_id=workflow.id,
        ),
    ]

    for goal in student_goals:
        db.add(goal)
    db.commit()
    return student_goals


@register_seed("activity_studentgoalmapping")
def seed_activity_studentgoal_mapping(db):
    """Seed mapping between generic activities and student goals"""

    # Get all activities and student goals by name
    activities = {a.activity_name: a for a in db.query(ActivityMaster).all()}
    student_goals = {s.activity_name: s for s in db.query(StudentGoalMaster).all()}

    mappings = []

    # NPTEL mapping
    if "NPTEL" in activities and "NPTEL-Pass" in student_goals:
        mappings.append(
            ActivityStudentGoalMapping(
                activity_id=activities["NPTEL"].id,
                student_goal_id=student_goals["NPTEL-Pass"].id,
            )
        )
    if "NPTEL" in activities and "NPTEL-Elite+Silver" in student_goals:
        mappings.append(
            ActivityStudentGoalMapping(
                activity_id=activities["NPTEL"].id,
                student_goal_id=student_goals["NPTEL-Elite+Silver"].id,
            )
        )
    if "NPTEL" in activities and "NPTEL-Elite+Gold" in student_goals:
        mappings.append(
            ActivityStudentGoalMapping(
                activity_id=activities["NPTEL"].id,
                student_goal_id=student_goals["NPTEL-Elite+Gold"].id,
            )
        )

    # Hackathon mapping
    if "Hackathon" in activities and "Hackathon-Participate" in student_goals:
        mappings.append(
            ActivityStudentGoalMapping(
                activity_id=activities["Hackathon"].id,
                student_goal_id=student_goals["Hackathon-Participate"].id,
            )
        )
    if "Hackathon" in activities and "Hackathon(Internal)-Win" in student_goals:
        mappings.append(
            ActivityStudentGoalMapping(
                activity_id=activities["Hackathon"].id,
                student_goal_id=student_goals["Hackathon(Internal)-Win"].id,
            )
        )
    if "Hackathon" in activities and "Hackathon(External)-Win" in student_goals:
        mappings.append(
            ActivityStudentGoalMapping(
                activity_id=activities["Hackathon"].id,
                student_goal_id=student_goals["Hackathon(External)-Win"].id,
            )
        )

    # Coding-Contest mapping
    if (
        "Coding-Contest" in activities
        and "Coding-Contest-Participation" in student_goals
    ):
        mappings.append(
            ActivityStudentGoalMapping(
                activity_id=activities["Coding-Contest"].id,
                student_goal_id=student_goals["Coding-Contest-Participation"].id,
            )
        )
    if "Coding-Contest" in activities and "Coding-Contest-Winner" in student_goals:
        mappings.append(
            ActivityStudentGoalMapping(
                activity_id=activities["Coding-Contest"].id,
                student_goal_id=student_goals["Coding-Contest-Winner"].id,
            )
        )

    # Internship mapping
    if "Internship" in activities and "Internship-Online" in student_goals:
        mappings.append(
            ActivityStudentGoalMapping(
                activity_id=activities["Internship"].id,
                student_goal_id=student_goals["Internship-Online"].id,
            )
        )
    if "Internship" in activities and "Internship-InOffice" in student_goals:
        mappings.append(
            ActivityStudentGoalMapping(
                activity_id=activities["Internship"].id,
                student_goal_id=student_goals["Internship-InOffice"].id,
            )
        )

    # Certification mapping
    if (
        "Certification" in activities
        and "Certification-Internal/Local" in student_goals
    ):
        mappings.append(
            ActivityStudentGoalMapping(
                activity_id=activities["Certification"].id,
                student_goal_id=student_goals["Certification-Internal/Local"].id,
            )
        )
    if "Certification" in activities and "Certification-Global" in student_goals:
        mappings.append(
            ActivityStudentGoalMapping(
                activity_id=activities["Certification"].id,
                student_goal_id=student_goals["Certification-Global"].id,
            )
        )

    # Research Resource Person mapping
    if (
        "Research Resource Person" in activities
        and "Research Resource Person(Internal)" in student_goals
    ):
        mappings.append(
            ActivityStudentGoalMapping(
                activity_id=activities["Research Resource Person"].id,
                student_goal_id=student_goals["Research Resource Person(Internal)"].id,
            )
        )
    if (
        "Research Resource Person" in activities
        and "Research Resource Person(External)" in student_goals
    ):
        mappings.append(
            ActivityStudentGoalMapping(
                activity_id=activities["Research Resource Person"].id,
                student_goal_id=student_goals["Research Resource Person(External)"].id,
            )
        )

    # Simple 1-to-1 mappings
    simple_mappings = [
        ("Coursera", "Coursera"),
        ("Udemy", "Udemy"),
        ("Workshop", "Workshop"),
        ("Other College Events", "Other College Events"),
        ("Organizing Events", "Organizing Events"),
        ("Cultural", "Cultural"),
        ("Sports/Music", "Sports/Music"),
        ("NCC/NSS Activities", "NCC/NSS Activities"),
        ("Volunteer Activities", "Volunteer Activities"),
        ("Value Added Courses", "Value Added Courses"),
        ("Research Working Prototype", "Research Working Prototype"),
        ("Research-paper", "Research-paper"),
        ("Best Paper Award", "Best Paper Award"),
        ("Study Abroad", "Study Abroad"),
        ("Seed Funding Project", "Seed Funding Project"),
        ("Startup", "Startup"),
        ("CGPA", "CGPA 8.5 And Above"),
    ]

    for activity_name, student_goal_name in simple_mappings:
        if activity_name in activities and student_goal_name in student_goals:
            mappings.append(
                ActivityStudentGoalMapping(
                    activity_id=activities[activity_name].id,
                    student_goal_id=student_goals[student_goal_name].id,
                )
            )

    for mapping in mappings:
        db.add(mapping)
    db.commit()
    return mappings


@register_seed("workflow_stage_mapping")
def seed_workflow_stages(db):
    from database.models.master.stage import Stage
    from database.models.master.workflow import Workflow

    standard_wf = db.query(Workflow).filter(Workflow.name == "Standard").first()
    fasttrack_wf = db.query(Workflow).filter(Workflow.name == "Fast-Track").first()

    standard_stages = db.query(Stage).filter(Stage.name == "Submission").all()
    fasttrack_stages = db.query(Stage).filter(Stage.name == "Approved").all()

    mappings = []
    for i, (s, f) in enumerate(zip(standard_stages[:3], fasttrack_stages[:3])):
        mapping1 = WorkflowStageMapping(
            workflow_id=standard_wf.id, stage_id=s.id, stage_order=i + 1
        )
        mapping2 = WorkflowStageMapping(
            workflow_id=fasttrack_wf.id, stage_id=f.id, stage_order=i + 1
        )
        db.add(mapping1)
        db.add(mapping2)
        mappings.extend([mapping1, mapping2])
    db.commit()
    return mappings


@register_seed("staff_student_mapping")
def seed_staff_student(db):
    staff1 = db.query(User).filter(User.staff_id == "FAC001").first()
    staff2 = db.query(User).filter(User.staff_id == "FAC002").first()

    mappings = []

    # Teacher 1 (FAC001 - Dr. Ravi Krishna) - ClassCoordinator for Section A
    mapping1 = StaffStudentMapping(
        staff_id=staff1.id,
        section="A",
        mapping_type="ClassCoordinator",
    )
    mappings.append(mapping1)

    # Teacher 2 (FAC002 - Prof. Meera Sen) - ClassCoordinator for Section B
    mapping2 = StaffStudentMapping(
        staff_id=staff2.id,
        section="B",
        mapping_type="ClassCoordinator",
    )
    mappings.append(mapping2)

    for m in mappings:
        db.add(m)
    db.commit()
    return mappings


@register_seed("user_activity_mapping")
def seed_user_activities(db):
    """Seed user activities - intentionally empty for manual entry"""
    pass


@register_seed("user_token_mapping")
def seed_user_tokens(db):
    """Seed user tokens - intentionally empty for manual entry"""
    pass


@register_seed("student_goal")
def seed_student_goals(db):
    """Seed student goals - intentionally empty for manual entry"""
    pass


def seed_user_activities(db):
    """Seed user activities - intentionally empty for manual entry"""
    pass


def reset_database(db):
    print("Resetting database...")

    from database.models.base import Base
    from database.init_db import engine

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db.execute(
        text("""
        DO $$
        DECLARE
            seq_name TEXT;
        BEGIN
            FOR seq_name IN SELECT sequence_name FROM information_schema.sequences LOOP
                EXECUTE 'ALTER SEQUENCE ' || seq_name || ' RESTART WITH 1';
            END LOOP;
        END $$;
    """)
    )
    db.commit()

    print("Database reset complete.\n")


def update_user_totals(db):
    """Update user total_tokens - intentionally empty since no tokens seeded"""
    pass


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
