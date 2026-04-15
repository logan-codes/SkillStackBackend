from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:1234@127.0.0.1:5432/SkillStack_v2")
conn = engine.connect()
result = conn.execute(
    text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'activity_studentgoalmapping')"
    )
)
exists = result.fetchone()[0]
print(f"activity_studentgoalmapping exists: {exists}")
conn.close()
