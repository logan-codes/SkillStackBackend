from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:1234@127.0.0.1:5432/SkillStack_v2")
conn = engine.connect()
result = conn.execute(
    text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    )
)
tables = [row[0] for row in result]
print(f"Total tables: {len(tables)}")
for t in sorted(tables):
    print(f"  - {t}")
conn.close()
