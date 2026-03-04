# SkillStack FastAPI Backend

Welcome to the backend of the SkillStack project! This is built using **FastAPI**, a modern, fast, and high-performance web framework for Python.

If you are new to the project or looking to contribute, this README will guide you through the folder structure to help you understand how everything is organized. We follow a clean, modular architecture, which makes it easy to split functionality, write tests, and maintain our code!

## 📂 Project Structure

Here is a quick overview of the main folders and files you'll find in this project. Each plays a specific role:

```text
└── 📁skillstack_fastapi
    └── 📁api #All api endpoints and router
        └── 📁v1
            └── 📁endpoints
                ├── users.py
            ├── api.py
    └── 📁app # Main application
        ├── main.py
    └── 📁core # Core
        ├── auth.py
        ├── config.py
    └── 📁database # Database controller and opertions
        └── 📁crud # db operations
            ├── user.py
        └── 📁models # table structure
            ├── user.py
        ├── init_db.py
    └── 📁schemas # Define response request models
        ├── user.py
    └── 📁services # business logic
        ├── user_service.py
    └── 📁utils # helpers
    ├── .env
    ├── .gitignore
    ├── README.md
    └── requirements.txt
```

### 1. `api/` (Routing & Endpoints)

**What it does:** This folder handles the web "routes" (the URLs users/clients can visit, e.g., `/users/login` or `/courses`). It connects an incoming web request to the underlying logic.

- **`v1/endpoints/`**: Holds different files for different modules (e.g., `users.py`, `courses.py`). This keeps our endpoints organized as the app grows.
- **`api.py`**: The main router file that gathers all the individual endpoints and ties them together before registering them to the FastAPI application.

### 2. `app/` (Application Core)

**What it does:** The starting point of the FastAPI application.

- **`main.py`**: The heart of the project. This is where the FastAPI app instance is created (`app = FastAPI()`), routers are included, globally applied middleware is added, and startup/shutdown events are handled.

### 3. `core/` (Configurations & Security)

**What it does:** Handles essential app-wide settings and security components.

- **`config.py`**: Loads environment variables from the `.env` file and defines application settings (like database URLs, secret keys for JWT, allowed CORS origins).
- **`auth.py`**: Contains the logic for authenticating users, generating/verifying JWT tokens, and managing password hashing.

### 4. `database/` (Data Management)

**What it does:** Everything related to the Database lives here!

- **`models/`**: Defines our database tables using SQLAlchemy structure. Each class here (e.g., `user.py` -> `User` model) corresponds to a table in our SQL database.
- **`crud/`** (Create, Read, Update, Delete): Contains functions that interact directly with the database. If you need to `get_user_by_id`, `create_new_course`, or `update_password`, it belongs in a file here (like `crud/user.py`).
- **`init_db.py`**: Functions used to set up the initial database state, create tables, or seed initial data.

### 5. `schemas/` (Data Validation - Pydantic)

**What it does:** Handles data validation using Pydantic.

- When a user sends data to the API (like signing up), we use **schemas** to validate that the incoming data is correct (e.g., the email is valid, the password has enough characters).
- When the API sends data back out, schemas define the structure of what gets returned, ensuring we don't accidentally leak sensitive database properties like hashed passwords.
- **Example:** `schemas/user.py` might contain `UserCreate` (what we expect on signup) and `UserResponse` (what we return after signup).

### 6. `services/` (Business Logic)

**What it does:** The middleman between the `api` (routes) and the `database` (CRUD actions).

- This directory contains the core logic of the application. For instance, a route might call a function in `services/user_service.py` to handle the flow of "registering a user". The service function will validate the schema, check if the email already exists using a `crud` function, hash the password, save the new user (via another `crud` action), and send a welcome email. By keeping this out of the endpoints, the code remains highly reusable and easier to test.

### 7. `utils/` (Helper Functions)

**What it does:** Small, reusable helper functions that don't belong to any specific feature but are useful across the app.

- **`email.py`**: A helper function to send emails.
- **`logger.py`**: Custom logging setup to make sure our console output is readable and trackable.

### 8. `Root` Level Files

- **`.env`**: Contains secure environment variables like your Database connection string or API keys. **Never commit this to Git!**
- **`requirements.txt`**: A list of all Python packages required to run the project. Use `pip install -r requirements.txt` to install them.

## How to Collaborate?

1. Clone the repository

```
git clone -b DEV https://github.com/logan-codes/SkillStackBackend.git
```

2. Create a new branch with name of the feature you are working on

```
git checkout <branch-name>
```

3. Push the branch to the repository

```
git push origin <branch-name>
```

4. Commit changes to your branch

```
git commit -am <commit-message>
```

5. Push to the repository

```
git push
```
