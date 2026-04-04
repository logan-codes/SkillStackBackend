# =================================================================
# USER SCHEMAS (Pydantic Models)
# =================================================================
# Schemas define the SHAPE of data for API requests and responses.
# They provide automatic:
#   - Data validation (is email valid? is password long enough?)
#   - Type conversion (string to date, string to int)
#   - Documentation (Swagger UI shows these models)
#   - Serialization (Python objects → JSON)
# =================================================================

# Pydantic imports
# BaseModel: Parent class for all schemas
# EmailStr: Special type that validates email format
from pydantic import BaseModel, EmailStr
from typing import Optional  # For optional fields (can be None)

# =================================================================
# REQUEST SCHEMAS (Data coming IN to the API)
# =================================================================


class LoginRequest(BaseModel):
    """
    Schema for login request.

    Frontend sends this when user clicks "Login":
        POST /api/v1/users/login
        Body: { "email_id": "student@college.edu" }

    EmailStr automatically validates that the email is in correct format.
    If invalid, FastAPI returns 422 error before reaching the endpoint.
    """

    email_id: EmailStr  # Validated email format (user@example.com)


# =================================================================
# RESPONSE SCHEMAS (Data going OUT of the API)
# =================================================================


class TokenResponse(BaseModel):
    """
    JWT token response after successful login.

    The frontend receives this and stores the access_token.
    This token is sent with every subsequent request in the header:
        Authorization: Bearer <access_token>

    Example response:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """

    access_token: str  # JWT token string
    token_type: str = "bearer"  # Always "bearer" for OAuth2


class UserInfo(BaseModel):
    """
    User information returned to frontend.

    This is a SAFE subset of user data:
        ✓ id, name, email, role_id, is_active
        ✗ password (NEVER return this!)
        ✗ hashed_password (NEVER return this!)

    Why not return everything?
        - Security: Sensitive data should not be exposed
        - Performance: Smaller response = faster transfer
        - Clarity: Frontend only gets what it needs

    from_attributes = True:
        Allows converting SQLAlchemy models directly to this schema.
        Example: UserInfo.from_orm(user_model)
    """

    id: int  # User's unique ID
    name: Optional[str] = None  # User's full name
    email_id: str  # User's email
    role_id: Optional[int] = None  # Role (1=Admin, 2=Staff, 3=Student)
    is_active: int  # Account status (1=active, 0=inactive)

    class Config:
        from_attributes = True  # Allow conversion from SQLAlchemy models


class LoginResponse(BaseModel):
    """
    Full login response with token + user info.

    Returned after successful login.
    Frontend receives token AND basic user info in one call.

    Example response:
        {
            "access_token": "eyJ...",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "name": "John Doe",
                "email_id": "john@example.com",
                "role_id": 3,
                "is_active": 1
            }
        }
    """

    access_token: str  # JWT token
    token_type: str = "bearer"  # Always "bearer"
    user: UserInfo  # User info object


# =================================================================
# SCHEMA USAGE IN ENDPOINTS
# =================================================================
#
# REQUEST (Data validation):
#   @router.post("/login")
#   def login(request: LoginRequest, db: Session = Depends(get_db)):
#       # request.email_id is already validated by Pydantic
#       # If invalid email, FastAPI returns 422 before reaching here
#
# RESPONSE (Data formatting):
#   return LoginResponse(
#       access_token="eyJ...",
#       user=UserInfo(id=1, name="John", email_id="john@example.com")
#   )
#   # Automatically converts to JSON
#
# =================================================================
# =================================================================
# SCHEMA INHERITANCE DIAGRAM
# =================================================================
#
# BaseModel (from Pydantic)
#     │
#     ├── LoginRequest
#     │       └── email_id: EmailStr
#     │
#     ├── TokenResponse
#     │       └── access_token, token_type
#     │
#     ├── UserInfo
#     │       └── id, name, email_id, role_id, is_active
#     │
#     └── LoginResponse
#             └── access_token, token_type, user: UserInfo
#
# =================================================================
# =================================================================
# VALIDATION EXAMPLES
# =================================================================
#
# Valid email:
#   {"email_id": "john@example.com"} ✓
#
# Invalid email:
#   {"email_id": "not-an-email"}
#   → FastAPI returns 422:
#   → {"detail": [{"loc": ["body", "email_id"],
#                  "msg": "Invalid email address.",
#                  "type": "value_error.email"}]}
#
# Missing required field:
#   {}
#   → FastAPI returns 422:
#   → {"detail": [{"loc": ["body", "email_id"],
#                  "msg": "Field required",
#                  "type": "missing"}]}
#
# =================================================================
