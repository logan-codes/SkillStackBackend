#Actually talk to the database
# database/crud/user.py

from sqlalchemy.orm import Session
from database.models.user import User        # the table blueprint from Step 2


def get_user_by_email(db: Session, email_id: str):
    """
    Looks up a user by their email_id in the database.

    db        = the database session (connection handed by get_db())
    email_id  = the email frontend sent us

    Returns:
        User object if found
        None if not found
    """
    return (
        db.query(User)                        # → "SELECT * FROM users"
        .filter(User.email_id == email_id)    # → "WHERE email_id = ?"
        .first()                              # → "LIMIT 1" — we only need one row
    )


def get_user_by_id(db: Session, user_id: int):
    """
    Looks up a user by their ID.
    Used when verifying JWT token — token carries user ID inside it.

    Returns:
        User object if found
        None if not found
    """
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )