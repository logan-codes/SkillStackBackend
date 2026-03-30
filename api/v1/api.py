# api/v1/api.py
# Main router - aggregates all endpoint routers

from fastapi import APIRouter
from api.v1.endpoints.mapping import users
from api.v1.endpoints.mapping import student_goal

# This is the v1 router — parent of all v1 endpoints
api_router = APIRouter()

# ──────────────────────────────────────────────────────────────
# USER ENDPOINTS
# ──────────────────────────────────────────────────────────────
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

# ──────────────────────────────────────────────────────────────
# STUDENT GOAL ENDPOINTS
# ──────────────────────────────────────────────────────────────
api_router.include_router(
    student_goal.router,
    prefix="/goals",
    tags=["Goals"]
)

# ──────────────────────────────────────────────────────────────
# To add more endpoints:
# 1. Import the router at the top
# 2. Add api_router.include_router() here
# Example:
# from api.v1.endpoints.master import activities
# api_router.include_router(activities.router, prefix="/activities", tags=["Activities"])
# ──────────────────────────────────────────────────────────────
