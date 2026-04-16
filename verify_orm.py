from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:1234@127.0.0.1:5432/SkillStack_v2")
conn = engine.connect()

result = conn.execute(
    text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
    )
)
db_tables = sorted([r[0] for r in result.fetchall()])

# ORM models that should exist (based on user's actual local DB - 19 tables)
orm_tables = [
    "activity",
    "activity_type_master",
    "application_config",
    "event_master",
    "gender",
    "malpractice_master",
    "menus",
    "program_dept_master",
    "role_menu_mapping",
    "roles",
    "staff_student_mapping",
    "stage",
    "status",
    "student_goal",
    "user_activity_mapping",
    "user_token_mapping",
    "users",
    "workflow",
    "workflow_stage_mapping",
]

print("=== DATABASE TABLES ===")
for t in db_tables:
    print(f"  - {t}")
print(f"\nTotal DB tables: {len(db_tables)}")

print("\n=== ORM MODELS ===")
for t in orm_tables:
    print(f"  - {t}")
print(f"\nTotal ORM tables: {len(orm_tables)}")

print("\n=== COMPARISON ===")
db_set = set(db_tables)
orm_set = set(orm_tables)

matching = db_set & orm_set
print(f"Matching: {len(matching)} tables")

only_db = db_set - orm_set
if only_db:
    print(f"\nIn DB but NOT in ORM (extra in DB): {only_db}")

only_orm = orm_set - db_set
if only_orm:
    print(f"\nIn ORM but NOT in DB (MISSING from DB): {only_orm}")

if only_orm:
    print("\n⚠️ PROBLEM: ORM references tables not in DB!")
else:
    print("\n✅ All ORM models match database tables!")

conn.close()
