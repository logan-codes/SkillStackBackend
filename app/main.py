# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.api import api_router

# Import all models to register them with Base.metadata
from database.models.mapping.users import User
from database.models.mapping.user_social_links import UserSocialLink
from database.models.mapping.activity import Activity
from database.models.mapping.user_activity_mapping import UserActivityMapping
from database.models.mapping.user_token_mapping import UserTokenMapping
from database.models.mapping.student_goal import StudentGoal
from database.models.mapping.staff_student_mapping import StaffStudentMapping
from database.models.mapping.workflow_stage_mapping import WorkflowStageMapping

from database.models.master.gender import Gender
from database.models.master.roles import Role
from database.models.master.status import Status
from database.models.master.stage import Stage
from database.models.master.workflow import Workflow
from database.models.master.event_master import EventMaster
from database.models.master.application_config import ApplicationConfig
from database.models.master.program_dept_master import ProgramDeptMaster
from database.models.master.activity_type_master import ActivityTypeMaster
from database.models.master.malpractice_master import MalpracticeMaster

from database.init_db import engine, Base

# Create the FastAPI app
app = FastAPI(
    title="SkillStack API",
    description="Backend API for SkillStack platform",
    version="1.0.0"
)

# CORS — allows frontend to talk to backend
# Without this, browser blocks all requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # in production → replace * with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables if they don't exist
# Safe to run every time — skips if table exists
Base.metadata.create_all(bind=engine)

# Register all routes under /api/v1
app.include_router(api_router, prefix="/api/v1")

# Health check — useful to test if server is running
@app.get("/")
def root():
    return {"message": "SkillStack API is running ✅"}