"""
Migration script to update activity_limit column
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from database.init_db import SessionLocal


def migrate():
    db = SessionLocal()
    try:
        # Add activity_limit to activity_master if not exists
        try:
            db.execute(
                text("ALTER TABLE activity_master ADD COLUMN activity_limit INTEGER")
            )
            print("Added column: activity_limit to activity_master")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("Column already exists: activity_limit in activity_master")
            else:
                print(f"Error adding activity_limit: {e}")

        # Remove activity_limit from student_goal_master if exists
        try:
            db.execute(
                text(
                    "ALTER TABLE student_goal_master DROP COLUMN IF EXISTS activity_limit"
                )
            )
            print("Removed column: activity_limit from student_goal_master")
        except Exception as e:
            print(f"Error removing activity_limit: {e}")

        db.commit()
        print("\nMigration completed successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    migrate()
