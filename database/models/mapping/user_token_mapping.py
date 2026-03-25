# database/models/mapping/user_token_mapping.py
# TODO: Implement UserTokenMapping model
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
class UserTokenMapping():
    __tablename__ = "user_token_mapping"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Foreign key to user table
    completed_activity_id = Column(Integer, nullable=False)  # Foreign key to user_activity_mapping table
    token_value = Column(String(255), nullable=False)  # Token value associated with the completed activity
    is_active = Column(Integer, default=1, nullable=False)
    created_date = Column(DateTime, default=datetime.now(datetime.timezone.utc))
    updated_date = Column(DateTime, default=datetime.now(datetime.timezone.utc), onupdate=datetime.now(datetime.timezone.utc))
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
