from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:1234@127.0.0.1:5432/SkillStack_v2")
conn = engine.connect()

result = conn.execute(
    text(
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'student_goal' ORDER BY ordinal_position"
    )
)
cols = [r[0] for r in result.fetchall()]
print("student_goal columns:")
for c in cols:
    print(" ", c)

conn.close()
