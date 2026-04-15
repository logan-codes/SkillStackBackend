# Main application entry point
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from api.v1.api import api_router
from database.init_db import engine
from database.models.base import Base

# Import all models to register them with Base.metadata
from database.models.mapping.users import User
from database.models.mapping.student_goal import StudentGoal
from database.models.mapping.user_activity_mapping import UserActivityMapping
from database.models.mapping.user_token_mapping import UserTokenMapping
from database.models.mapping.staff_student_mapping import StaffStudentMapping
from database.models.mapping.workflow_stage_mapping import WorkflowStageMapping

# Note: The following models reference tables that don't exist in PostgreSQL
# from database.models.mapping.activity_studentgoal_mapping import ActivityStudentGoalMapping
# from database.models.master.student_goal_master import StudentGoalMaster

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="SkillStack API",
    description="Backend API for SkillStack platform",
    version="1.0.0",
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
    )


# CORS - allows frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup (only creates if not exist)
Base.metadata.create_all(bind=engine)

# Register API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "SkillStack API is running"}
