from sqlalchemy import create_engine 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings 

# Create the database engine using the URL from settings
# connect_args={"check_same_thread": False} is needed only for SQLite
engine = create_engine (settings.DATABASE_URL)
# SessionLocal - this is what we use to talk to the database
# autocommit=False means we have to manually commit changes
# autoflush=False gives us more control over when data is sent to DB
sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base - all our database models will inherit from this
# It provides the table definitions we need
Base = declarative_base()

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

