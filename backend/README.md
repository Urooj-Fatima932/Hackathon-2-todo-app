# Backend Todo API

Secure, multi-user RESTful API for todo task management with JWT authentication and PostgreSQL persistence.

## Quick Start

### Prerequisites

- Python 3.13+ ([Download](https://www.python.org/downloads/))
- Neon PostgreSQL database ([Free tier](https://neon.tech))
- Better Auth configured with JWT secret

### Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your database URL and secrets

# 5. Run the API
uvicorn app.main:app --reload --port 8000
```

### Verify Installation

- **API Root**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

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

## Features

- ✅ JWT authentication with Better Auth integration
- ✅ User data isolation (users can only access their own tasks)
- ✅ Complete CRUD operations for tasks
- ✅ Task filtering by completion status
- ✅ Input validation with Pydantic
- ✅ Automatic API documentation
- ✅ Python 3.13 + Windows compatible

## Technology Stack

- **Framework**: FastAPI 0.115.6
- **Database**: Neon PostgreSQL (via psycopg 3.2.3)
- **ORM**: SQLModel 0.0.24
- **Validation**: Pydantic 2.10.6
- **Authentication**: PyJWT 2.10.1
- **Server**: Uvicorn 0.34.0

## Development

```bash
# Run with auto-reload
uvicorn app.main:app --reload

# Run tests (if configured)
pytest

# Check code style
black app/ tests/
flake8 app/ tests/
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Yes | JWT signing secret (matches frontend) |
| `API_HOST` | No | Server bind address (default: 0.0.0.0) |
| `API_PORT` | No | Server port (default: 8000) |
| `DEBUG` | No | Enable debug mode (default: False) |
| `CORS_ORIGINS` | Yes | Allowed frontend URLs (JSON array) |

## Deployment

See [quickstart.md](../specs/001-backend-todo-api/quickstart.md) for detailed deployment instructions.

## Documentation

- **Specification**: `../specs/001-backend-todo-api/spec.md`
- **Implementation Plan**: `../specs/001-backend-todo-api/plan.md`
- **Data Model**: `../specs/001-backend-todo-api/data-model.md`
- **API Contract**: `../specs/001-backend-todo-api/contracts/openapi.yaml`

## Support

For issues or questions, refer to the specification documents or check the API documentation at `/docs`.
