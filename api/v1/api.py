#Register that route
# api/v1/api.py

from fastapi import APIRouter
from api.v1.endpoints import users          # import the users router

# This is the v1 router — parent of all v1 endpoints
api_router = APIRouter()

# Register users router
# prefix = all users routes start with /users
# tags   = groups them in the auto docs (Swagger UI)
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

# When you add more endpoints later, just add them here:
# api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])
# api_router.include_router(admin.router,   prefix="/admin",   tags=["Admin"])