from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:1234@127.0.0.1:5432/SkillStack_v2")
conn = engine.connect()

tables = [
    "status",
    "workflow",
    "stage",
    "event_master",
    "application_config",
    "menus",
    "role_menu_mapping",
]
for table in tables:
    result = conn.execute(
        text(
            f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'"
        )
    )
    print(f"\n=== {table} ===")
    for r in result:
        print(f"  {r[0]}: {r[1]}")

conn.close()
