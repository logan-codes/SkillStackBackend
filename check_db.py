from database.init_db import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("PostgreSQL connection successful!")

        result = conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
            )
        )
        tables = [row[0] for row in result]
        print(f"Tables in database: {len(tables)}")
        for t in tables:
            print(f"  - {t}")
except Exception as e:
    print(f"Connection failed: {e}")
