# SkillStack Backend - Complete Guide

FastAPI backend for a skill/token-based student tracking system.

---

## 1. Project Structure

```
SkillStackBackend/
├── api/v1/
│   └── endpoints/
│       ├── mapping/          # User-scoped endpoints
│       │   ├── users.py      # Login, profile, user endpoints
│       │   └── student_goal.py  # Student goals CRUD
│       └── master/           # Master table endpoints (future)
├── core/
│   ├── auth.py              # JWT, RBAC, role constants
│   ├── config.py            # Environment variables
│   └── security.py          # Password hashing
├── database/
│   ├── models/
│   │   ├── master/         # Reference tables (10 tables)
│   │   └── mapping/        # Data tables (7 tables)
│   └── crud/
│       ├── master/         # Master CRUD operations
│       └── mapping/        # Data CRUD operations
├── schemas/
│   ├── master/            # Master table schemas
│   └── mapping/           # Data schemas
├── app/
│   └── main.py            # FastAPI entry point
└── .env                   # Environment variables
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
7. JWT token created with user_id and role_id
8. Response sent back with token + user info
```

---

## 3. RBAC - Role-Based Access Control

### Roles

| Role ID | Name | Access Level |
|---------|------|-------------|
| 1 | ADMIN | Full access |
| 2 | STAFF | Staff + Admin functions |
| 3 | STUDENT | Basic authenticated access |

### Usage in Endpoints

```python
from core.auth import get_current_user, require_admin, require_staff

# Admin only
@router.post("/admin-only")
def admin_endpoint(current_user = Depends(require_admin)):
    """Only admins can access"""

# Staff and Admin
@router.post("/staff-action")
def staff_endpoint(current_user = Depends(require_staff)):
    """Staff and admins can access"""

# Any authenticated user
@router.get("/any-user")
def any_user_endpoint(current_user = Depends(get_current_user)):
    """All authenticated users can access"""
```

---

## 4. Database Tables

### Master Tables (Reference Data)

| Table | Description |
|-------|-------------|
| gender_master | Male, Female, Other |
| roles_master | Admin, Staff, Student |
| status_master | Yet To Start, In Progress, Completed, Failure |
| stage_master | Workflow stages with permissions |
| workflow_master | Workflow definitions |
| activity_type_master | Activity categories |
| event_master | Event types |
| program_dept_master | Programs & Departments |
| malpractice_master | Malpractice types with token deduction |
| application_config | App settings |

### Mapping Tables (Actual Data)

| Table | Description |
|-------|-------------|
| users | User accounts with academic info |
| activity_master | Activities with token rewards |
| workflow_stage_mapping | Links workflows to stages |
| user_token_mapping | Token transactions |
| user_activity_mapping | User progress in activities |
| student_goal | Student goals and targets |
| staff_student_mapping | Staff-Student relationships |

---

## 5. API Endpoints

### Authentication

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/api/v1/users/login` | Public | Login with email |

### User Profile

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/v1/users/me` | Auth | Get my profile |
| GET | `/api/v1/users/profile/full` | Auth | Get full profile |
| PUT | `/api/v1/users/profile` | Auth | Update profile |
| GET | `/api/v1/users/all` | Admin | Get all users |

### Student Goals

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/v1/goals/` | Auth | Get my goals |
| GET | `/api/v1/goals/{id}` | Auth | Get specific goal |
| POST | `/api/v1/goals/` | Auth | Create new goal |
| PUT | `/api/v1/goals/{id}` | Auth | Update goal |
| DELETE | `/api/v1/goals/{id}` | Auth | Delete goal |
| GET | `/api/v1/goals/all/students` | Staff/Admin | Get all student goals |

---

## 6. Schema Structure

### Schema Pattern

```python
# Base - common fields
class UserBase(BaseModel):
    email: str

# Create - for POST requests
class UserCreate(UserBase):
    password: str

# Update - for PUT requests (all fields optional)
class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None

# Response - what API returns
class UserResponse(UserBase):
    id: int
    name: str
    
    class Config:
        from_attributes = True
```

---

## 7. CRUD Pattern

### CRUD Repository Pattern

```python
# database/crud/mapping/student_goal.py

class StudentGoalRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_goals(self, user_id: int):
        return self.db.query(StudentGoal).filter(
            StudentGoal.user_id == user_id
        ).all()
    
    def create_goal(self, user_id: int, goal_name: str, target_tokens: int):
        goal = StudentGoal(...)
        self.db.add(goal)
        self.db.commit()
        return goal
```

---

## 8. Add New Endpoint (5 Steps)

### Step 1: Create Model
```python
# database/models/master/gender.py
from database.models.base import Base

class Gender(Base):
    __tablename__ = "gender_master"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
```

### Step 2: Create Schema
```python
# schemas/master/gender.py
class GenderResponse(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True
```

### Step 3: Create CRUD
```python
# database/crud/master/gender.py
def get_all_genders(db):
    return db.query(Gender).all()
```

### Step 4: Create Endpoint
```python
# api/v1/endpoints/master/genders.py
@router.get("/", response_model=List[GenderResponse])
def get_genders(db=Depends(get_db)):
    return get_all_genders(db)
```

### Step 5: Register Router
```python
# api/v1/api.py
api_router.include_router(genders.router, prefix="/genders", tags=["Genders"])
```

---

## 9. Environment Variables

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/Skillstack_DB_1
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## 10. How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload

# Open API docs
http://127.0.0.1:8000/docs
```

---

## 11. Implementation Status

| Layer | Status | Files |
|-------|--------|-------|
| Models | ✅ 100% | 17/17 |
| Schemas | ✅ 10% | 2/17 |
| CRUD | ✅ 10% | 2/17 |
| Endpoints | ✅ 10% | 2/17 |
| RBAC | ✅ Implemented | auth.py |

### Implemented Features

- ✅ User Login
- ✅ JWT Authentication
- ✅ Role-Based Access Control (RBAC)
- ✅ User Profile endpoints
- ✅ Student Goals CRUD

### Pending Features

- ❌ Activity System (Types, Activities, User Activities)
- ❌ Token Management
- ❌ Staff Approval Flow
- ❌ Master Table CRUD
- ❌ Dashboard/Analytics
- ❌ ML Integration

---

## 12. Quick Reference

| Need to... | Go to... |
|------------|----------|
| Add new table | `database/models/` |
| Add database query | `database/crud/` |
| Add API endpoint | `api/v1/endpoints/` |
| Add request/response format | `schemas/` |
| Change JWT settings | `core/auth.py` |
| Change RBAC roles | `core/auth.py` (ADMIN, STAFF, STUDENT constants) |
| Change DB connection | `.env` |

---

## 13. Technology Stack

- **FastAPI** - Web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **JWT (python-jose)** - Authentication
- **Pydantic** - Data validation
- **Passlib** - Password hashing
