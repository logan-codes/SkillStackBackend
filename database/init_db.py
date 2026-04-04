# Database connection setup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from database.models.base import Base

# Create engine and session factory
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# FastAPI dependency for database access
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
