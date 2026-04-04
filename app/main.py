# Main application entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.api import api_router
from database.init_db import engine
from database.models.base import Base

# Import all models to register them with Base.metadata
from database.models.mapping import users, activity, student_goal, user_activity_mapping
from database.models.master import (
    activity_type_master,
    application_config,
    event_master,
    malpractice_master,
    program_dept_master,
    stage,
    workflow,
    status,
    roles,
    gender,
)

app = FastAPI(
    title="SkillStack API",
    description="Backend API for SkillStack platform",
    version="1.0.0",
)

# CORS - allows frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
Base.metadata.create_all(bind=engine)

# Register API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "SkillStack API is running"}
