# SkillStack Backend - Complete Documentation

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Database Models](#3-database-models)
4. [Schemas](#4-schemas)
5. [CRUD Operations](#5-crud-operations)
6. [Authentication](#6-authentication)
7. [API Endpoints](#7-api-endpoints)
8. [Request-Response Flow](#8-request-response-flow)

---

## 1. Project Overview

SkillStack is a **FastAPI Python backend** for a skill/token-based student tracking system.

**Tech Stack:**
- FastAPI (web framework)
- SQLAlchemy (ORM)
- PostgreSQL (database)
- JWT (authentication)
- Pydantic (data validation)

**Run the server:**
```bash
uvicorn app.main:app --reload
```

**Access API docs:** http://localhost:8000/docs

---

## 2. Architecture

```
SkillStackBackend/
├── app/
│   └── main.py              # Entry point
├── core/
│   ├── config.py           # Settings from .env
│   ├── security.py         # Password hashing (bcrypt)
│   └── auth.py             # JWT authentication & RBAC
├── database/
│   ├── init_db.py          # Engine, SessionLocal, get_db()
│   ├── models/
│   │   ├── base.py         # Base + CommonFields
│   │   ├── master/         # Master tables
│   │   └── mapping/        # Business tables
│   └── crud/               # Database operations
├── schemas/                # Pydantic models
│   ├── master/
│   └── mapping/
└── api/
    └── v1/
        ├── api.py          # Router aggregator
        └── endpoints/      # API routes
```

---

## 3. Database Models

### 3.1 Base Model (`database/models/base.py`)

```python
Base = declarative_base()

class CommonFields:
    id = Column(BigInteger, primary_key=True)
    is_active = Column(SmallInteger, default=1)
    created_date = Column(DateTime, default=...)
    updated_date = Column(DateTime, onupdate=...)
    created_by = Column(BigInteger)
    updated_by = Column(BigInteger)
```

**All models inherit from both `Base` and `CommonFields`:**

```python
class User(Base, CommonFields):
    __tablename__ = "users"
    # Only model-specific fields here
    email_id = Column(String(100), unique=True)
    name = Column(String(100))
```

### 3.2 Master Tables (Reference Data)

| Model | Table | Purpose |
|-------|-------|---------|
| `Gender` | gender_master | Male, Female, Other |
| `Role` | roles_master | Admin, Staff, Student |
| `Status` | status_master | Yet To Start, In Progress, Completed |
| `Stage` | stage_master | Workflow stages |
| `Workflow` | workflow_master | Workflow definitions |
| `ActivityTypeMaster` | activity_type_master | Workshop, Seminar, Hackathon |
| `ProgramDeptMaster` | program_dept_master | Programs & Departments |
| `MalpracticeMaster` | malpractice_master | Malpractice types |
| `EventMaster` | event_master | Event types |
| `ApplicationConfig` | application_config | App settings |

### 3.3 Mapping Tables (Business Data)

| Model | Table | Purpose |
|-------|-------|---------|
| `User` | users | User accounts |
| `StudentGoal` | student_goal | Student goals |
| `Activity` | activity_master | Activities with token rewards |
| `UserActivityMapping` | user_activity_mapping | User progress in activities |
| `UserTokenMapping` | user_token_mapping | Token transactions |
| `WorkflowStageMapping` | workflow_stage_mapping | Workflow-stage links |
| `StaffStudentMapping` | staff_student_mapping | Staff-Student relationships |

---

## 4. Schemas

Schemas define data shape for API requests/responses.

### 4.1 Pattern

```python
# Base - common fields
class UserBase(BaseModel):
    email: str
    name: str

# Create - for POST requests
class UserCreate(UserBase):
    password: str  # extra field for creation

# Update - for PUT requests (all optional)
class UserUpdate(BaseModel):
    name: Optional[str] = None

# Response - for GET responses
class UserResponse(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True  # Allows reading from SQLAlchemy model
```

### 4.2 from_attributes = True

Tells Pydantic it can read data from Python objects (SQLAlchemy models):

```python
user = User(id=1, name="John", email="john@test.com")
user_info = UserInfo.model_validate(user)  # ✅ Works!
```

---

## 5. CRUD Operations

CRUD = Create, Read, Update, Delete

### 5.1 Pattern

```python
# Simple functions
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, email: str, name: str):
    user = User(email=email, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

### 5.2 Repository Pattern (for complex models)

```python
class StudentGoalRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_goals(self, user_id: int):
        return self.db.query(StudentGoal).filter(
            StudentGoal.user_id == user_id,
            StudentGoal.is_active == 1
        ).all()
    
    def create_goal(self, user_id: int, goal_name: str, target_tokens: int):
        goal = StudentGoal(user_id=user_id, goal_name=goal_name, target_tokens=target_tokens)
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal
```

---

## 6. Authentication

### 6.1 Password Hashing (`core/security.py`)

```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

### 6.2 JWT Token (`core/auth.py`)

```python
# Create token
def create_access_token(data: dict) -> str:
    payload = {"exp": datetime.now() + timedelta(minutes=60), **data}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Verify token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    return user
```

### 6.3 Role-Based Access Control (RBAC)

```python
def require_admin(current_user = Depends(get_current_user)):
    if current_user.role_id != 1:  # 1 = Admin
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user

def require_staff(current_user = Depends(get_current_user)):
    if current_user.role_id not in [1, 2]:  # 1=Admin, 2=Staff
        raise HTTPException(status_code=403, detail="Staff only")
    return current_user
```

---

## 7. API Endpoints

### 7.1 User Endpoints

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | /users/login | Public | Login, returns JWT |
| GET | /users/me | User | Get current user profile |
| GET | /users/profile/full | User | Get full profile |
| GET | /users/all | Admin | Get all users |

### 7.2 Student Goal Endpoints

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | /goals/ | User | Get my goals |
| POST | /goals/ | User | Create goal |
| PUT | /goals/{id} | Owner | Update goal |
| DELETE | /goals/{id} | Owner | Delete goal |
| GET | /goals/all/students | Staff/Admin | Get all goals |

### 7.3 Master Endpoints

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | /genders/ | Public | List genders |
| POST | /genders/ | Staff | Create gender |
| GET | /roles/ | Public | List roles |
| GET | /statuses/ | Public | List statuses |
| GET | /activities/ | Public | List activities |

---

## 8. Request-Response Flow

### 8.1 Complete Flow Diagram

```
1. FRONTEND REQUEST
   POST /api/v1/users/login
   Body: {"email_id": "user@test.com"}
   
2. FASTAPI APP (main.py)
   → CORS Middleware (check origin)
   → Route matching
   
3. ENDPOINT (users.py)
   @router.post("/login")
   
4. DEPENDENCIES
   Depends(get_db)         → Database session
   Depends(oauth2_scheme)  → Extract JWT token
   
5. CRUD (users.py)
   get_user_by_email(db, email)
   
6. MODEL (User)
   SQLAlchemy converts to query
   
7. DATABASE (PostgreSQL)
   SELECT * FROM users WHERE email = ?
   
8. RESPONSE
   LoginResponse(access_token="...", user={...})
   
9. BACK TO FRONTEND
```

### 8.2 Authentication Flow

```
USER LOGIN:
1. POST /login with email
2. Find user in DB
3. Verify password
4. Create JWT token (user_id, role_id)
5. Return token

PROTECTED REQUEST:
1. Send request with header: Authorization: Bearer <token>
2. get_current_user() extracts token
3. Decode token, get user_id
4. Find user in DB
5. Check is_active
6. Return user object

ROLE CHECK:
1. require_admin() checks user.role_id == 1
2. If yes: allow access
3. If no: return 403 Forbidden
```

---

## Quick Reference

### Import Order
```python
# 1. FastAPI
from fastapi import APIRouter, Depends, HTTPException

# 2. Database
from sqlalchemy.orm import Session
from database.init_db import get_db

# 3. Models
from database.models.mapping.users import User

# 4. Schemas
from schemas.mapping.user import LoginRequest, LoginResponse

# 5. CRUD
from database.crud.mapping.users import get_user_by_email

# 6. Auth
from core.auth import get_current_user, require_admin
```

### Database Session Pattern
```python
@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
```

### Creating a New Model
```python
# 1. Create model in database/models/mapping/
# 2. Create schema in schemas/mapping/
# 3. Create CRUD in database/crud/mapping/
# 4. Create endpoint in api/v1/endpoints/mapping/
# 5. Register in api/v1/api.py
```

---

## End
