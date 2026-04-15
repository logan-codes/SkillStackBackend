from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:1234@127.0.0.1:5432/SkillStack_v2")
conn = engine.connect()

for table in [
    "user_activity_mapping",
    "user_token_mapping",
    "student_goal",
    "staff_student_mapping",
]:
    result = conn.execute(text(f"SELECT * FROM {table} LIMIT 1"))
    print(f"=== {table} columns ===")
    for desc in result._metadata.keys:
        print(f"  {desc}")
    print()

conn.close()
