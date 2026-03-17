# database/init_db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings              # reads DATABASE_URL from .env

# Engine = the actual connection to PostgreSQL
# pool_pre_ping=True means: "test connection before using it, reconnect if dropped"
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

# SessionLocal = a factory that creates DB sessions
# Each session = one conversation with the database
SessionLocal = sessionmaker(
    autocommit=False,                         # we control when to save (commit)
    autoflush=False,                          # we control when to sync
    bind=engine
)


# get_db() = the function FastAPI calls to hand a DB session to your endpoints
# yield = gives the session, then closes it when the request is done
# Think of it as: opening a DB connection for ONE request, then closing it
def get_db():
    db = SessionLocal()
    try:
        yield db                              # ← FastAPI uses this session
    finally:
        db.close()                            # ← always closes, even if error occurs