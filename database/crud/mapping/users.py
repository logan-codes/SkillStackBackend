# User CRUD operations
from sqlalchemy.orm import Session
from database.models.mapping.users import User


def get_user_by_email(db: Session, email_id: str):
    return db.query(User).filter(User.email_id == email_id).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def update_external_links(db: Session, user_id: int, links: dict):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    for key, value in links.items():
        if value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user
