# database/models/mapping/user_activity_mapping.py
# TODO: Implement UserActivityMapping model
from sqlalchemy import Column, Integer, DateTime ,String
from datetime import datetime

class UserActivityMapping():
    __tablename__ = "user_activity_mapping"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Foreign key to user table
    activity_id = Column(Integer, nullable=False)  # Foreign key to activity table
    title = Column(String(255), nullable=False)  # Title of the activity
    activity_details = Column(String(255), nullable=True)  # Details of the activity
    event_type = Column(String(100), nullable=False)  # Type of the event (e.g., "login", "logout", "data_update")
    stage_id = Column(Integer, nullable=True)  # Foreign key to stage_master table (if applicable)
    status = Column(Integer, default=1, nullable=False)  # Status of the activity (e.g., active/inactive)
    permission_score = Column(Integer, nullable=True)  # Permission score associated with the activity
    proof_score = Column(Integer, nullable=True)  # Proof score associated with the activity
    activity_start_data = Column(DateTime, nullable=True)  # Start time of the activity
    activity_end_data = Column(DateTime, nullable=True)  # End time of the activity
    is_active = Column(Integer, default=1, nullable=False)
    created_date = Column(DateTime, default=datetime.now(datetime.timezone.utc))
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

