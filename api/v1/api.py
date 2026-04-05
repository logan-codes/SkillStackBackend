# Main API router - aggregates all endpoint routers
from fastapi import APIRouter
from api.v1.endpoints.mapping import (
    users,
    student_goal,
    student_profile,
    user_activity,
)

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(student_goal.router, prefix="/goals", tags=["Goals"])
api_router.include_router(
    user_activity.router, prefix="/my-activities", tags=["My Activities"]
)
api_router.include_router(student_profile.router, prefix="/students", tags=["Students"])
