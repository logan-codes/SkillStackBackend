>>The Request Journey:

Frontend POST /api/v1/login
        ↓
  [users.py endpoint]      ← receives the request
        ↓
  [user_service.py]        ← business logic: validate SSO, find/create user
        ↓
  [database/crud/user.py]  ← hit the database
        ↓
  [core/auth.py]           ← mint a JWT token
        ↓
  Return { access_token: "eyJ..." } back to frontend

>> What the Frontend Needs From us:

 1. POST /api/v1/login
   Input:  { sso_token: "token from google/microsoft" }
   Output: { access_token: "your JWT", token_type: "bearer" }

2. Every protected route should accept:
   Header: Authorization: Bearer <our_JWT>


>> Handling keys :

Google's Token (ID Token)          YOUR JWT Token
─────────────────────────          ──────────────
Issued by: Google                  Issued by: YOUR server
Proves: "Google knows this user"   Proves: "OUR app logged this user in"
You use it: ONCE (to verify)       Frontend uses it: EVERY request
Expires: Google decides            Expires: YOU decide
You store it: NEVER                You store it: NEVER (stateless!)

>>File Structure & What Each File :

SkillStackBackend/
│
├── .env                          ← YOUR secrets (never in git, you create this locally)
│
├── core/
│   ├── config.py                 ← reads .env, makes settings available to whole app
│   └── auth.py                   ← JWT engine: create token + verify token (bouncer)
│
├── database/
│   ├── init_db.py                ← opens connection to PostgreSQL (SessionLocal, get_db)
│   ├── models/
│   │   └── user.py               ← maps the users table columns to Python class
│   └── crud/
│       └── user.py               ← DB queries: get_user_by_email, get_user_by_id
│
├── schemas/
│   └── user.py                   ← data shapes: LoginRequest (in), LoginResponse (out)
│
├── api/
│   └── v1/
│       ├── api.py                ← route registry: registers all endpoint routers
│       └── endpoints/
│           └── users.py          ← actual /login and /me routes
│
└── app/
    └── main.py                   ← entry point: creates app, CORS, DB tables, registers routes


>> The Login Flow (What Happens at Runtime) :

Frontend POST /api/v1/users/login
  { "email_id": "student@college.edu" }
          ↓
  schemas/user.py         validates email format
          ↓
  database/crud/user.py   get_user_by_email() → hits PostgreSQL
          ↓
  user not found?         → 404 error
  is_active == 0?         → 403 error
          ↓
  core/auth.py            create_access_token({ user_id, role_id })
          ↓
  Returns to frontend:
  {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "user": { id, name, email_id, role_id, is_active }
  }

>> Add these in the required.tx:
fastapi
sqlalchemy
psycopg2-binary
pydantic-settings
python-jose[cryptography]
python-dotenv
email-validator
uvicorn

>>HOW TO RUN LOCALLY :
==================

1. Clone the repo
   git clone <repo-url>
   cd SkillStackBackend

2. Install packages
   pip install -r requirements.txt

3. Create .env file
   Windows PowerShell  →  New-Item .env
   Mac/Linux           →  touch .env

4. Generate a SECRET_KEY
   python -c "import secrets; print(secrets.token_hex(32))"
   Copy the output.

5. Fill your .env file with this:
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/skillstack_db
   SECRET_KEY=paste_generated_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60

   Note: If you never set a postgres password, use postgres as the password.

6. Create the database
   In pgAdmin → Right click Databases → Create → name it skillstack_db
   OR in terminal → psql -U postgres -c "CREATE DATABASE skillstack_db;"

7. Run the server
   uvicorn app.main:app --reload

8. Test it
   http://localhost:8000       → should return "SkillStack API is running"
   http://localhost:8000/docs  → Swagger UI to test all endpoints visually