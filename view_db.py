# Quick script to view database tables
from database.init_db import SessionLocal
from database.models.mapping.users import User
from database.models.mapping.activity import Activity
from database.models.mapping.student_goal import StudentGoal
from database.models.mapping.user_activity_mapping import UserActivityMapping

db = SessionLocal()

print("\n" + "=" * 50)
print("=== USERS ===")
print("=" * 50)
users = db.query(User).all()
print(f"Total: {len(users)} records\n")
for u in users:
    print(
        f"ID: {u.id} | Name: {u.name} | Email: {u.email_id} | Role: {u.role_id} | Tokens: {u.total_tokens}"
    )

print("\n" + "=" * 50)
print("=== ACTIVITIES ===")
print("=" * 50)
activities = db.query(Activity).all()
print(f"Total: {len(activities)} records\n")
for a in activities:
    print(
        f"ID: {a.id} | Name: {a.activity_name} | Token: {a.token} | Type: {a.activity_type_id}"
    )

print("\n" + "=" * 50)
print("=== STUDENT GOALS ===")
print("=" * 50)
goals = db.query(StudentGoal).all()
print(f"Total: {len(goals)} records\n")
for g in goals:
    print(
        f"ID: {g.id} | User: {g.user_id} | Activity: {g.activity_id} | Goal: {g.goal_name} | Target: {g.target_tokens} | Current: {g.current_tokens} | Deadline: {g.deadline}"
    )

print("\n" + "=" * 50)
print("=== USER ACTIVITIES ===")
print("=" * 50)
user_activities = db.query(UserActivityMapping).all()
print(f"Total: {len(user_activities)} records\n")
for ua in user_activities:
    print(
        f"ID: {ua.id} | User: {ua.user_id} | Activity: {ua.activity_id} | Custom: {ua.custom_name} | Status: {ua.status_id} | Tokens: {ua.tokens_earned}"
    )

db.close()
print("\n✅ Database view complete!")
