from database.init_db import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("=== USERS TABLE ===")
    result = conn.execute(
        text(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position"
        )
    )
    for row in result:
        print(f"{row[0]}: {row[1]}")

    print("\n=== ACTIVITY TABLE ===")
    result = conn.execute(
        text(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'activity' ORDER BY ordinal_position"
        )
    )
    for row in result:
        print(f"{row[0]}: {row[1]}")

    print("\n=== USER_ACTIVITY_MAPPING TABLE ===")
    result = conn.execute(
        text(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'user_activity_mapping' ORDER BY ordinal_position"
        )
    )
    for row in result:
        print(f"{row[0]}: {row[1]}")

    print("\n=== STATUS TABLE ===")
    result = conn.execute(
        text(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'status' ORDER BY ordinal_position"
        )
    )
    for row in result:
        print(f"{row[0]}: {row[1]}")
