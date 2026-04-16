from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:1234@127.0.0.1:5432/SkillStack_v2")
conn = engine.connect()

# Step 1: Add new columns to activity table
print("=== Step 1: Adding columns to activity table ===")

# Add base_token column (copy from token first, then we'll update)
try:
    conn.execute(text("ALTER TABLE activity ADD COLUMN base_token INTEGER DEFAULT 0"))
    print("  Added: base_token column")
except Exception as e:
    print(f"  base_token: {e}")

try:
    conn.execute(
        text("ALTER TABLE activity ADD COLUMN has_sub_category INTEGER DEFAULT 0")
    )
    print("  Added: has_sub_category column")
except Exception as e:
    print(f"  has_sub_category: {e}")

# Step 2: Create activity_category table
print("\n=== Step 2: Creating activity_category table ===")
try:
    conn.execute(
        text("""
        CREATE TABLE IF NOT EXISTS activity_category (
            id SERIAL PRIMARY KEY,
            activity_id INTEGER REFERENCES activity(id),
            category_name VARCHAR(100),
            extra_token INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
    """)
    )
    print("  Created: activity_category table")
except Exception as e:
    print(f"  Error creating table: {e}")

conn.commit()
conn.close()

print("\n=== Database structure updated! ===")
