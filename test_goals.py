from database.init_db import SessionLocal
from database.crud.mapping.student_goal import StudentGoalRepo
from database.models.mapping.users import User
from database.models.master.activity_master import ActivityMaster

db = SessionLocal()

student = db.query(User).filter(User.id == 2).first()
if student:
    repo = StudentGoalRepo(db)
    goals = repo.get_user_goals(student.id)
    for g in goals:
        repo.delete_goal(g.id)

    activities = db.query(ActivityMaster).limit(16).all()
    activity_ids = [a.id for a in activities]
    new_goals = repo.create_goals_bulk(student.id, activity_ids)

    print("Student:", student.name)
    print("Goals Created:", len(new_goals))

    summary = repo.get_goal_summary(student.id)
    print("")
    print("=== GOAL SUMMARY ===")
    print("Total Goals:", summary["total_goals"])
    print("Minimum Required:", summary["minimum_required"])
    print("Minimum Met:", summary["minimum_met"])
    print("Total Target Tokens:", summary["total_target_tokens"])
    print("Total Current Tokens:", summary["total_current_tokens"])
    print("Remaining Tokens:", summary["remaining_tokens"])
    print("")
    print("Sample Goals (first 3):")
    for g in summary["goals"][:3]:
        print(
            "  -",
            g["activity_name"],
            ": target=",
            g["target_tokens"],
            ", current=",
            g["current_tokens"],
            ", completed=",
            g["is_completed"],
        )

db.close()
