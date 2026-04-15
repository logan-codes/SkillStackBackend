from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:1234@127.0.0.1:5432/SkillStack_v2")
conn = engine.connect()

result = conn.execute(
    text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
    )
)
db_tables = sorted([r[0] for r in result.fetchall()])

print("=== DATABASE TABLES (22) ===")
for t in db_tables:
    print(f"  - {t}")

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
    "student_malpractice",
    "user_activity_mapping",
    "user_token_mapping",
    "users",
    "workflow",
    "workflow_stage_mapping",
]

print("\n=== ORM MODELS (20) ===")
for t in orm_tables:
    print(f"  - {t}")

print("\n=== MATCHING STATUS ===")
db_set = set(db_tables)
orm_set = set(orm_tables)

matching = db_set & orm_set
print(f"Matching tables: {len(matching)}")

only_db = db_set - orm_set
if only_db:
    print(f"\nTables in DB but NOT in ORM: {only_db}")

only_orm = orm_set - db_set
if only_orm:
    print(f"\nTables in ORM but NOT in DB (ERROR): {only_orm}")
else:
    print("\nAll ORM models match database tables!")

conn.close()
