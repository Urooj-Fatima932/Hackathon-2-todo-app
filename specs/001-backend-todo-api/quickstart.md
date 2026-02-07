# Quickstart Guide: Backend Todo API

**Feature**: Backend Todo API
**Date**: 2026-02-06
**Purpose**: Get the backend API running locally in under 10 minutes

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** installed ([Download](https://www.python.org/downloads/))
- **Git** installed
- **Neon PostgreSQL database** created ([Get free tier](https://neon.tech))
- **Better Auth** configured with JWT secret

Verify Python version:
```bash
python --version
# Should output: Python 3.11.x or higher
```

---

## Step 1: Clone and Navigate

```bash
# From repository root
cd backend
```

---

## Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Verify activation (should show (venv) prefix in terminal)
```

---

## Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Required dependencies** (`requirements.txt`):
```txt
fastapi==0.115.0
uvicorn[standard]==0.31.0
sqlmodel==0.0.22
psycopg2-binary==2.9.9
pydantic==2.9.0
pydantic-settings==2.5.0
PyJWT==2.9.0
python-multipart==0.0.12
```

---

## Step 4: Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Create .env from template
cp .env.example .env

# Edit .env file with your values
```

**Required environment variables** (`.env`):
```env
# Database Connection
DATABASE_URL=postgresql://[user]:[password]@[host]/[database]?sslmode=require

# JWT Authentication (must match Better Auth secret)
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# CORS (frontend URL)
CORS_ORIGINS=["http://localhost:3000"]
```

### How to get DATABASE_URL (Neon PostgreSQL):

1. Go to [Neon Console](https://console.neon.tech)
2. Select your project
3. Navigate to "Connection Details"
4. Copy the connection string (format: `postgresql://[user]:[password]@[host]/[database]?sslmode=require`)

### How to get BETTER_AUTH_SECRET:

- This must match the secret used by Better Auth in the frontend
- Generate strong secret: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Copy same value to both frontend and backend `.env` files

---

## Step 5: Initialize Database

The database tables will be created automatically on first startup using SQLModel's `metadata.create_all()`.

**Manual database creation** (optional, if needed):
```bash
# Run Python script to create tables
python -c "
from app.database import engine
from app.models import SQLModel

SQLModel.metadata.create_all(engine)
print('Database tables created successfully')
"
```

---

## Step 6: Run the API

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Expected output**:
```
INFO:     Will watch for changes in these directories: ['/path/to/backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## Step 7: Verify API is Running

### Option A: Browser
Open browser and navigate to:
- **Root**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs (interactive Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (alternative API documentation)

### Option B: Command Line (curl)
```bash
# Test root endpoint
curl http://localhost:8000

# Expected response:
# {"message":"Todo API is running"}

# Test health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy"}
```

---

## Step 8: Test API with Authentication

### Get JWT Token from Better Auth

First, authenticate with Better Auth (frontend) to get a JWT token:

```bash
# Example: Sign in via Better Auth
# This will return a JWT token in the response
```

### Test Authenticated Endpoint

```bash
# Replace <JWT_TOKEN> with actual token from Better Auth
# Replace <USER_ID> with user ID from token's sub claim

# List user's tasks (should return empty array initially)
curl -X GET "http://localhost:8000/api/<USER_ID>/tasks" \
  -H "Authorization: Bearer <JWT_TOKEN>"

# Expected response:
# {"tasks":[],"total":0}

# Create a new task
curl -X POST "http://localhost:8000/api/<USER_ID>/tasks" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test task",
    "description": "Testing the API"
  }'

# Expected response:
# {
#   "id": 1,
#   "user_id": "<USER_ID>",
#   "title": "Test task",
#   "description": "Testing the API",
#   "completed": false,
#   "created_at": "2026-02-06T18:30:00Z",
#   "updated_at": "2026-02-06T18:30:00Z"
# }
```

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── models.py            # SQLModel database models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── auth/
│   │   ├── middleware.py    # JWT verification
│   │   └── dependencies.py  # Auth dependencies
│   ├── routes/
│   │   └── tasks.py         # Task CRUD endpoints
│   └── utils/
│       └── exceptions.py    # Custom exception handlers
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create this)
├── .env.example            # Environment variable template
└── README.md               # Backend documentation
```

---

## Common Issues & Solutions

### Issue: `ModuleNotFoundError: No module named 'app'`
**Solution**: Make sure you're running uvicorn from the `backend/` directory and your virtual environment is activated.

### Issue: `sqlalchemy.exc.OperationalError: could not connect to server`
**Solution**:
- Verify `DATABASE_URL` in `.env` is correct
- Check Neon database is running and accessible
- Ensure `?sslmode=require` is appended to connection string

### Issue: `401 Unauthorized` when testing endpoints
**Solution**:
- Verify JWT token is valid and not expired
- Ensure `BETTER_AUTH_SECRET` in backend `.env` matches frontend
- Check `Authorization: Bearer <token>` header is included in request

### Issue: `403 Forbidden` when accessing tasks
**Solution**:
- Verify `user_id` in URL path matches `sub` claim in JWT token
- Extract `sub` claim from JWT: `jwt.decode(token, verify=False)['sub']`

### Issue: Database tables not created
**Solution**:
- Run manual table creation script (see Step 5)
- Check database connection is successful
- Verify user has CREATE TABLE permissions in Neon database

### Issue: `ImportError: cannot import name 'Annotated' from 'typing'`
**Solution**: Upgrade to Python 3.11+. `Annotated` was added in Python 3.9 but Pydantic 2.x requires 3.11+.

---

## Development Workflow

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run specific test file
pytest tests/test_tasks_create.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html
```

### API Documentation

- **Interactive Docs**: http://localhost:8000/docs
  - Try out endpoints directly in browser
  - See request/response schemas
  - Test authentication

- **ReDoc**: http://localhost:8000/redoc
  - Clean, readable API documentation
  - Better for sharing with frontend team

### Database Inspection

```bash
# Connect to Neon database using psql
psql "<DATABASE_URL>"

# List tables
\dt

# Describe tasks table
\d tasks

# Query tasks
SELECT * FROM tasks;

# Exit psql
\q
```

---

## Next Steps

1. **Run Tests**: `pytest` to verify all functionality works
2. **Integrate with Frontend**: Update frontend `NEXT_PUBLIC_API_URL` to `http://localhost:8000`
3. **Implement Features**: Follow tasks.md for implementation order
4. **Deploy**: See deployment guide for Render/Railway configuration

---

## Quick Reference

### Essential Commands

```bash
# Start API (development)
uvicorn app.main:app --reload

# Run tests
pytest

# Check code style
black app/ tests/
flake8 app/ tests/

# View API docs
open http://localhost:8000/docs
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Yes | JWT signing secret (matches frontend) |
| `API_HOST` | No | Server bind address (default: 0.0.0.0) |
| `API_PORT` | No | Server port (default: 8000) |
| `DEBUG` | No | Enable debug mode (default: False) |
| `CORS_ORIGINS` | Yes | Allowed frontend URLs (JSON array) |

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| GET | `/api/{user_id}/tasks` | List user's tasks |
| POST | `/api/{user_id}/tasks` | Create new task |
| GET | `/api/{user_id}/tasks/{task_id}` | Get task details |
| PUT | `/api/{user_id}/tasks/{task_id}` | Update task |
| DELETE | `/api/{user_id}/tasks/{task_id}` | Delete task |
| PATCH | `/api/{user_id}/tasks/{task_id}/complete` | Toggle completion |

---

## Support

**Issues**: Check [troubleshooting section](#common-issues--solutions) above

**API Documentation**: http://localhost:8000/docs

**Specification**: See `specs/001-backend-todo-api/spec.md`

**Implementation Plan**: See `specs/001-backend-todo-api/plan.md`

---

**You're ready to build! 🚀**

The API is running and ready for frontend integration. Next, run `/sp.tasks` to generate implementation tasks.
