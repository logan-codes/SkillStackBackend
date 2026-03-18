# SkillStack Backend - Complete Guide

FastAPI backend for a skill/token-based student tracking system.

---

## 1. Project Structure

```
SkillStackBackend/
├── api/v1/endpoints/     # API routes (login, users, activities)
├── core/                 # config, auth (JWT), security
├── database/
│   ├── models/           # Database tables
│   │   ├── master/      # Reference tables (gender, roles, status...)
│   │   └── mapping/     # Data tables (users, activities...)
│   └── crud/            # Database operations
├── schemas/              # Request/Response validation
├── app/main.py           # FastAPI entry point
└── .env                 # Environment variables
```

---

## 2. Request Flow

```
Frontend → API Endpoint → Schema Validation → CRUD → Model → Database
                                ↑                              │
                                └──────── Response ←──────────┘
```

### Login Flow Example

```
1. Frontend sends { "email_id": "student@college.com" }
2. POST /api/v1/users/login receives request
3. Schema validates email format
4. CRUD function queries database
5. Model maps to "users" table
6. Database returns user (or 404)
7. JWT token created
8. Response sent back with token
```

---

## 3. Folder Explanation

### `api/v1/endpoints/` - API Endpoints
Handle HTTP requests from frontend

| File       | Endpoint Prefix | Description    |
|------      |-----------------|-------------   |
| `users.py` | `/api/v1/users` | Login, profile |

```python
@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, request.email_id)
```

### `schemas/` - Request/Response Models
Validate incoming data & format outgoing data

```python
class LoginRequest(BaseModel):
    email_id: EmailStr

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserInfo
```

### `database/crud/` - Database Operations
All database queries (Create, Read, Update, Delete)

```python
def get_user_by_email(db: Session, email_id: str):
    return db.query(User).filter(User.email_id == email_id).first()
```

### `database/models/` - ORM Models
Python representation of database tables

```python
class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    email_id = Column(String(100), unique=True)
    name = Column(String(100))
```

### `core/auth.py` - Authentication
JWT token creation and verification

- `create_access_token()` - Generates JWT token
- `get_current_user()` - Verifies token and returns current user

---

## 4. Database Tables

### Master Tables (Reference Data)

| Table                 | Description                                   |
|-------                |-------------                                  |
| gender_master         | Male, Female, Other                           |
| roles_master          | Admin, Staff, Student                         |
| status_master         | Yet To Start, In Progress, Completed, Failure |
| stage_master          | Workflow stages with permissions              |
| workflow_master       | Workflow definitions                          |
| activity_type_master  | Activity categories                           |
| event_master          | Event types                                   |
| program_dept_master   | Programs & Departments                        |
| malpractice_master    | Malpractice types with token deduction        |
| application_config    | App settings                                  |

### Mapping Tables (Actual Data)

| Table                  | Description                      |
|-------                 |-------------                     |
| users                  | User accounts with academic info |
| activity_master        | Activities with token rewards    |
| workflow_stage_mapping | Links workflows to stages        |
| user_token_mapping     | Token transactions               |
| user_activity_mapping  | User progress in activities      |
| student_goal           | Student goals and targets        |
| staff_student_mapping  | Staff-Student relationships      |

---

## 5. API Endpoints

| Method | Endpoint             | Description                   |
|--------|----------            |-------------                  |
| POST   | `/api/v1/users/login`| Login with email (SSO style)  |
| GET    | `/api/v1/users/me`   | Get current user (protected)  |

---

## 6. Add New Table (5 Steps)

### Step 1: Create Model
```python
# database/models/master/roles.py
from sqlalchemy import Column, Integer, String
from database.models.base import Base

class Role(Base):
    __tablename__ = "roles_master"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
```

### Step 2: Create CRUD
```python
# database/crud/roles.py
from sqlalchemy.orm import Session
from database.models.master.roles import Role

def get_role(db: Session, id: int):
    return db.query(Role).filter(Role.id == id).first()
```

### Step 3: Create Schema
```python
# schemas/role.py
from pydantic import BaseModel

class RoleResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True
```

### Step 4: Create Endpoint
```python
# api/v1/endpoints/roles.py
from fastapi import APIRouter, Depends
from database.init_db import get_db
from database.crud.roles import get_role
from schemas.role import RoleResponse

router = APIRouter()

@router.get("/{id}", response_model=RoleResponse)
def get_role_endpoint(id: int, db=Depends(get_db)):
    return get_role(db, id)
```

### Step 5: Register Router
```python
# api/v1/api.py
from api.v1.endpoints.mapping import users, roles

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
```

---

## 7. Environment Variables (.env)

```
DATABASE_URL=postgresql://user:password@localhost:5432/skillstack
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 8. How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload

# Open API docs
http://127.0.0.1:8000/docs
```

---

## 9. Quick Reference

| Need to...                  | Go to...            |
|------------                 |----------           |
| Add new table               | `database/models/`  |
| Add database query          | `database/crud/`    |
| Add API endpoint            | `api/v1/endpoints/` |
| Add request/response format | `schemas/`          |
| Change JWT settings         | `core/auth.py`      |
| Change DB connection        | `.env`              |

---

## 10. Technology Stack

- **FastAPI** - Web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **JWT** - Authentication
- **Pydantic** - Data validation
