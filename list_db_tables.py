from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:1234@127.0.0.1:5432/SkillStack_v2")
conn = engine.connect()

result = conn.execute(
    text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
    )
)
db_tables = sorted([r[0] for r in result.fetchall()])

print("=== DATABASE TABLES ===")
for t in db_tables:
    print(f"  - {t}")
print(f"\nTotal: {len(db_tables)} tables")

conn.close()
