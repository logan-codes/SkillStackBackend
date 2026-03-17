# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.api import api_router                    # Step 7 - all routes
from database.init_db import engine                  # Step 4 - DB connection
from database.models.mapping.users import Base                # Step 2 - table blueprints

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