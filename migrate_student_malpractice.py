"""
Migration script to create student_malpractice table
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from database.init_db import SessionLocal


def migrate():
    db = SessionLocal()
    try:
        # Create student_malpractice table
        db.execute(
            text("""
            CREATE TABLE IF NOT EXISTS student_malpractice (
                id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL,
                malpractice_id INTEGER NOT NULL,
                token_deducted INTEGER NOT NULL,
                teacher_id INTEGER NOT NULL,
                description VARCHAR(500),
                is_reversed INTEGER DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        )
        print("Created table: student_malpractice")

        db.commit()
        print("Migration completed successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    migrate()
