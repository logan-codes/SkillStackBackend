from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:1234@127.0.0.1:5432/SkillStack_v2")
conn = engine.connect()

result = conn.execute(text("SELECT * FROM workflow LIMIT 1"))
print("=== workflow columns ===")
for desc in result._metadata.keys:
    print(f"  {desc}")

conn.close()
