# SkillStack Backend - Architecture Guide

## Table of Contents
1. [Project Structure](#project-structure)
2. [Request Flow](#request-flow)
3. [Folder Explanation](#folder-explanation)
4. [Database Tables](#database-tables)
5. [Adding New Tables](#adding-new-tables)

---

## Project Structure

```
SkillStackBackend-Auth_m/
├── api/                          # API Endpoints
│   └── v1/
│       └── endpoints/            # Route handlers (one file per table)
│           ├── users.py          # /users endpoints
│           └── roles.py          # /roles endpoints (future)
│       └── api.py               # Router aggregator
│
├── core/                         # Core functionality
│   ├── auth.py                   # JWT token creation & verification
│   └── config.py                 # Configuration (.env)
│
├── database/                     # Database layer
│   ├── models/                   # SQLAlchemy ORM models (one file per table)
│   │   ├── users.py              # User table model
│   │   ├── roles.py              # Roles table model
│   │   └── ...
│   ├── crud/                     # Database operations (one file per table)
│   │   ├── users.py              # User CRUD functions
│   │   ├── roles.py
│   │   └── ...
│   └── init_db.py                # Database connection setup
│
├── schemas/                      # Pydantic models (request/response validation)
│   ├── user.py                   # User schemas
│   └── ...
│
├── services/                     # Business logic (future)
├── utils/                        # Utilities (email, logging)
└── app/
    └── main.py                   # FastAPI app entry point
```

---

## Request Flow

### Login Flow Example

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND                                           │
│  { "email_id": "student@college.com" }                                       │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼ POST /api/v1/users/login
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API ENDPOINT                                        │
│  api/v1/endpoints/users.py::login()                                         │
│  - Receives request                                                          │
│  - Validates input using LoginRequest schema                                │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼ Calls get_user_by_email()
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CRUD LAYER                                          │
│  database/crud/users.py::get_user_by_email()                                │
│  - Queries database                                                          │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼ SQL Query
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MODEL LAYER                                         │
│  database/models/users.py::User                                             │
│  - SQLAlchemy ORM model - maps to "users" table                             │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATABASE (PostgreSQL)                              │
│  - Checks if email exists                                                    │
│  - Returns user row or None                                                  │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
              User Found                          User Not Found
                    │                                   │
                    ▼                                   ▼
         create_access_token()              HTTP 404 Error
         (from core/auth.py)                 "User not found"
                    │
                    ▼
         ┌─────────────────────────────────────────┐
         │  Returns to Frontend:                    │
         │  {                                       │
         │    "access_token": "eyJ...",            │
         │    "token_type": "bearer",              │
         │    "user": { ... }                       │
         │  }                                       │
         └─────────────────────────────────────────┘
```

---

## Folder Explanation

### 1. `api/v1/endpoints/` - API Endpoints
**Purpose:** Handle HTTP requests from frontend

| File | Endpoint Prefix | Description |
|------|-----------------|-------------|
| `users.py` | `/api/v1/users` | Login, profile, user CRUD |
| `roles.py` | `/api/v1/roles` | Role management (future) |

**Example:**
```python
# api/v1/endpoints/users.py
@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, request.email_id)
    # ...
```

### 2. `schemas/` - Request/Response Models
**Purpose:** Validate incoming data & format outgoing data

| File | Purpose |
|------|---------|
| `user.py` | LoginRequest, LoginResponse, UserInfo |

**Example:**
```python
# schemas/user.py
class LoginRequest(BaseModel):
    email_id: EmailStr

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserInfo
```

### 3. `database/crud/` - Database Operations
**Purpose:** All database queries (Create, Read, Update, Delete)

| File | Functions |
|------|-----------|
| `users.py` | get_user_by_email(), get_user_by_id() |
| `roles.py` | get_role_by_id(), get_all_roles() (future) |

**Example:**
```python
# database/crud/users.py
def get_user_by_email(db: Session, email_id: str):
    return db.query(User).filter(User.email_id == email_id).first()
```

### 4. `database/models/` - ORM Models
**Purpose:** Python representation of database tables

| File | Table |
|------|-------|
| `users.py` | users |
| `roles.py` | roles (future) |

**Example:**
```python
# database/models/users.py
class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    email_id = Column(String(100), unique=True)
    name = Column(String(100))
```

### 5. `core/auth.py` - Authentication
**Purpose:** JWT token creation and verification

**Key Functions:**
- `create_access_token()` - Generates JWT token
- `get_current_user()` - Verifies token and returns current user

---

## Database Tables

### Master Tables (Reference Data)

| Table | Description | File |
|-------|-------------|------|
| `roles` | User roles (Student, Staff, Admin) | `roles.py` |
| `gender` | Gender options (Male, Female, Other) | `gender.py` |
| `stage` | Workflow stages (permission, verification, etc.) | `stage.py` |
| `status` | Activity status (Yet To Start, In Progress, Completed) | `status.py` |
| `workflow` | Workflow definitions | `workflow.py` |
| `activity_type_master` | Activity categories (Certifications, Workshops, etc.) | `activity_type_master.py` |
| `event_master` | Event types (Internal, External) | `event_master.py` |
| `malpractice_master` | Malpractice types and token deductions | `malpractice_master.py` |
| `program_dept_master` | Programs and branches | `program_dept_master.py` |
| `application_config` | App settings (min tokens, etc.) | `application_config.py` |

### Transaction Tables

| Table | Description | File |
|-------|-------------|------|
| `users` | User accounts | `users.py` |
| `activity` | Available activities | `activity.py` |
| `user_activity_mapping` | User's activity submissions | `user_activity_mapping.py` |
| `user_token_mapping` | Token transactions | `user_token_mapping.py` |
| `student_goal` | Student activity goals | `student_goal.py` |
| `staff_student_mapping` | Staff-Student assignments | `staff_student_mapping.py` |
| `workflow_stage_mapping` | Workflow stage configuration | `workflow_stage_mapping.py` |

---

## Adding New Tables

### Step 1: Create Model
```python
# database/models/roles.py
from sqlalchemy import Column, SmallInteger, String
from database.models import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(SmallInteger, primary_key=True)
    role_name = Column(String(30), unique=True)
    is_active = Column(SmallInteger, default=1)
```

### Step 2: Create CRUD Operations
```python
# database/crud/roles.py
from sqlalchemy.orm import Session
from database.models.roles import Role

def get_role_by_id(db: Session, role_id: int):
    return db.query(Role).filter(Role.id == role_id).first()

def get_all_roles(db: Session):
    return db.query(Role).all()
```

### Step 3: Create Schema
```python
# schemas/role.py
from pydantic import BaseModel

class RoleBase(BaseModel):
    role_name: str

class RoleResponse(RoleBase):
    id: int
    is_active: int
    
    class Config:
        from_attributes = True
```

### Step 4: Create Endpoint
```python
# api/v1/endpoints/roles.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.init_db import get_db
from database.crud.roles import get_all_roles
from schemas.role import RoleResponse

router = APIRouter()

@router.get("/", response_model=list[RoleResponse])
def list_roles(db: Session = Depends(get_db)):
    return get_all_roles(db)
```

### Step 5: Register Router
```python
# api/v1/api.py
from api.v1.endpoints import users, roles

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
```

---

## Current API Endpoints

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/api/v1/users/login` | Login with email | ✅ Active |
| GET | `/api/v1/users/me` | Get current user profile | ✅ Active |

---

## Environment Variables (.env)

```
DATABASE_URL=postgresql://user:password@localhost:5432/skillstack
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Quick Reference

| Question | Answer |
|----------|--------|
| Where to add new table model? | `database/models/<table_name>.py` |
| Where to add CRUD functions? | `database/crud/<table_name>.py` |
| Where to add API endpoint? | `api/v1/endpoints/<table_name>.py` |
| Where to add request/response schema? | `schemas/<table_name>.py` |
| Where is JWT logic? | `core/auth.py` |
| Where is DB connection? | `database/init_db.py` |
