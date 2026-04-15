# Quick script to view all database tables (PostgreSQL)
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.init_db import SessionLocal
from database.models.mapping.users import User
from database.models.master.activity_master import ActivityMaster
from database.models.master.activity_type_master import ActivityTypeMaster
from database.models.master.malpractice_master import MalpracticeMaster
from database.models.master.program_dept_master import ProgramDeptMaster
from database.models.master.status import Status
from database.models.master.roles import Role
from database.models.master.gender import Gender
from database.models.master.workflow import Workflow
from database.models.master.stage import Stage
from database.models.master.event_master import EventMaster
from database.models.mapping.staff_student_mapping import StaffStudentMapping
from database.models.mapping.user_activity_mapping import UserActivityMapping
from database.models.mapping.user_token_mapping import UserTokenMapping
from database.models.mapping.student_goal import StudentGoal

db = SessionLocal()

# ============================================================================
# MASTER TABLES
# ============================================================================

print("\n" + "=" * 80)
print("=== ROLES ===")
print("=" * 80)
roles = db.query(Role).all()
print(f"Total: {len(roles)} records\n")
for r in roles:
    print(f"ID: {r.id} | Role: {r.role_name}")

print("\n" + "=" * 80)
print("=== GENDER ===")
print("=" * 80)
genders = db.query(Gender).all()
print(f"Total: {len(genders)} records\n")
for g in genders:
    print(f"ID: {g.id} | Name: {g.name}")

print("\n" + "=" * 80)
print("=== PROGRAM/DEPARTMENT ===")
print("=" * 80)
departments = db.query(ProgramDeptMaster).all()
print(f"Total: {len(departments)} records\n")
for d in departments:
    print(f"ID: {d.id} | Program: {d.program} | Branch: {d.branch}")

print("\n" + "=" * 80)
print("=== ACTIVITY TYPE ===")
print("=" * 80)
types = db.query(ActivityTypeMaster).all()
print(f"Total: {len(types)} records\n")
for t in types:
    print(f"ID: {t.id} | Type: {t.type_name}")

print("\n" + "=" * 80)
print("=== STATUS ===")
print("=" * 80)
statuses = db.query(Status).all()
print(f"Total: {len(statuses)} records\n")
for s in statuses:
    print(f"ID: {s.id} | Status: {s.name}")

print("\n" + "=" * 80)
print("=== WORKFLOW ===")
print("=" * 80)
workflows = db.query(Workflow).all()
print(f"Total: {len(workflows)} records\n")
for w in workflows:
    print(f"ID: {w.id} | Name: {w.name}")

print("\n" + "=" * 80)
print("=== STAGE ===")
print("=" * 80)
stages = db.query(Stage).all()
print(f"Total: {len(stages)} records\n")
for s in stages:
    print(f"ID: {s.id} | Stage: {s.name}")

print("\n" + "=" * 80)
print("=== EVENT MASTER ===")
print("=" * 80)
events = db.query(EventMaster).all()
print(f"Total: {len(events)} records\n")
for e in events:
    print(f"ID: {e.id} | Name: {e.name}")

print("\n" + "=" * 80)
print("=== MALPRACTICE ===")
print("=" * 80)
malpractice = db.query(MalpracticeMaster).all()
print(f"Total: {len(malpractice)} records\n")
for m in malpractice:
    print(f"ID: {m.id} | Name: {m.name} | Token Deduction: {m.token_deduction}")

# ============================================================================
# MAPPING TABLES
# ============================================================================

print("\n" + "=" * 80)
print("=== USERS ===")
print("=" * 80)
users = db.query(User).all()
print(f"Total: {len(users)} records\n")
for u in users:
    role = db.query(Role).filter(Role.id == u.role_id).first()
    dept = (
        db.query(ProgramDeptMaster)
        .filter(ProgramDeptMaster.id == u.program_dept_id)
        .first()
    )
    gender = db.query(Gender).filter(Gender.id == u.gender_id).first()
    role_name = role.role_name if role else u.role_id
    dept_name = dept.branch if dept else "N/A"
    print(
        f"ID: {u.id} | {u.name} | {role_name} | {u.email_id} | "
        f"Register No: {u.register_no or 'N/A'} | Staff ID: {u.staff_id or 'N/A'} | "
        f"Year: {u.year or 'N/A'} | Semester: {u.semester or 'N/A'} | Dept: {dept_name} | "
        f"Tokens: {u.total_tokens} | Active: {u.is_active}"
    )

print("\n" + "=" * 80)
print("=== STAFF STUDENT MAPPING ===")
print("=" * 80)
mappings = db.query(StaffStudentMapping).all()
print(f"Total: {len(mappings)} records\n")
for m in mappings:
    staff = db.query(User).filter(User.id == m.staff_id).first()
    staff_name = staff.name if staff else m.staff_id
    print(
        f"ID: {m.id} | Staff: {staff_name} | Student ID: {m.student_id} | "
        f"Mapping Type: {m.mapping_type}"
    )

print("\n" + "=" * 80)
print("=== ACTIVITY (Master Activities) ===")
print("=" * 80)
activities = db.query(ActivityMaster).all()
print(f"Total: {len(activities)} records\n")
for a in activities:
    print(
        f"ID: {a.id} | Name: {a.activity_name} | Token: {a.token} | "
        f"Workflow ID: {a.workflow_id} | Type: {a.type} | Active: {a.is_active}"
    )

print("\n" + "=" * 80)
print("=== USER ACTIVITY MAPPING (User Progress) ===")
print("=" * 80)
user_activities = db.query(UserActivityMapping).all()
print(f"Total: {len(user_activities)} records\n")
if user_activities:
    for ua in user_activities:
        user = db.query(User).filter(User.id == ua.user_id).first()
        activity = (
            db.query(ActivityMaster).filter(ActivityMaster.id == ua.activity_id).first()
        )
        status = db.query(Status).filter(Status.id == ua.status).first()
        print(
            f"ID: {ua.id} | User: {user.name if user else ua.user_id} | "
            f"Activity: {activity.activity_name if activity else ua.activity_id} | "
            f"Title: {ua.title} | Status: {status.name if status else ua.status} | "
            f"Stage ID: {ua.stage_id} | Event Type: {ua.event_type}"
        )
else:
    print("No records")

print("\n" + "=" * 80)
print("=== USER TOKEN MAPPING (Transactions) ===")
print("=" * 80)
token_mappings = db.query(UserTokenMapping).all()
print(f"Total: {len(token_mappings)} records\n")
if token_mappings:
    for t in token_mappings:
        user = db.query(User).filter(User.id == t.user_id).first()
        print(
            f"ID: {t.id} | User: {user.name if user else t.user_id} | "
            f"Amount: {t.token_amount:+d} | Type: {t.transaction_type} | "
            f"Description: {t.description} | Ref ID: {t.reference_id or 'N/A'}"
        )
else:
    print("No records")

print("\n" + "=" * 80)
print("=== STUDENT GOAL ===")
print("=" * 80)
goals = db.query(StudentGoal).all()
print(f"Total: {len(goals)} records\n")
if goals:
    for g in goals:
        user = db.query(User).filter(User.id == g.user_id).first()
        activity = (
            db.query(ActivityMaster).filter(ActivityMaster.id == g.activity_id).first()
        )
        print(
            f"ID: {g.id} | User: {user.name if user else g.user_id} | "
            f"Activity: {activity.activity_name if activity else g.activity_id} | "
            f"Target Month: {g.target_month} | Active: {g.is_active}"
        )
else:
    print("No records")

db.close()
print("\n" + "=" * 80)
print("Database view complete!")
print("=" * 80)
