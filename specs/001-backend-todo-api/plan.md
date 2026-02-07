# Implementation Plan: Backend Todo API

**Branch**: `001-backend-todo-api` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-backend-todo-api/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a secure, multi-user RESTful API for todo task management with JWT authentication and user isolation. The API provides complete CRUD operations for tasks, supports filtering by completion status, and enforces strict security boundaries ensuring users can only access their own data. All operations are authenticated, validated, and persisted to a relational database with automatic timestamp tracking.

**Technical Approach**: FastAPI backend with SQLModel ORM for type-safe database operations, JWT-based authentication integration, Pydantic schemas for request/response validation, and RESTful endpoint design following HTTP semantics. User isolation enforced at the database query level with all operations scoped to authenticated user ID from JWT token.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.115.0, SQLModel 0.0.22, Pydantic 2.9.0, PyJWT 2.9.0, psycopg2-binary 2.9.9, uvicorn 0.31.0
**Storage**: Neon PostgreSQL (serverless) - shared database instance with Better Auth
**Testing**: pytest with FastAPI TestClient for integration tests, pytest-asyncio for async tests
**Target Platform**: Linux server (Docker containerized), deployed on Render/Railway
**Project Type**: Web backend API (part of monorepo with separate frontend)
**Performance Goals**: <500ms task creation, <1s task list retrieval (up to 1000 tasks), 100 concurrent users
**Constraints**: <1s p95 latency for standard operations, zero data loss, 99.9% operation success rate
**Scale/Scope**: Multi-user system supporting 100+ concurrent users, 1000+ tasks per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Technology Stack Compliance
- [x] **Backend**: FastAPI + SQLModel + Python 3.11+ (matches constitutional requirement)
- [x] **Database**: Neon PostgreSQL serverless (matches constitutional requirement)
- [x] **Authentication**: JWT token verification with Better Auth integration (matches constitutional requirement)
- [x] **Deployment**: Render/Railway target (matches constitutional guidance)

### ✅ Security Requirements Compliance
- [x] **JWT Authentication**: All endpoints require valid JWT (except health/status endpoints)
- [x] **User Isolation**: Database queries scoped to authenticated user_id from JWT
- [x] **Input Validation**: Pydantic schemas validate all requests
- [x] **No Hardcoded Secrets**: All secrets via environment variables
- [x] **SQL Injection Prevention**: SQLModel ORM with parameterized queries
- [x] **CORS Configuration**: Explicit origins via environment variable

### ✅ API Design Standards Compliance
- [x] **RESTful Conventions**: GET/POST/PUT/PATCH/DELETE with proper semantics
- [x] **HTTP Status Codes**: 200, 201, 204, 400, 401, 403, 404, 500
- [x] **JSON Format**: All request/response bodies in JSON
- [x] **FastAPI Docs**: Automatic documentation at `/docs`
- [x] **User-Friendly Errors**: Structured error responses with "detail" field

### ✅ Monorepo Organization Compliance
- [x] **Backend Directory**: Code in `/backend` separate from frontend
- [x] **Specs Directory**: Planning artifacts in `/specs/001-backend-todo-api/`
- [x] **History Directory**: PHRs in `/history/prompts/001-backend-todo-api/`
- [x] **No Cross-Boundary Imports**: Backend is independent module

### ✅ Database Standards Compliance
- [x] **Shared Neon Instance**: Uses same database as Better Auth
- [x] **SQLModel**: Type-safe database models
- [x] **User ID Column**: All tasks include `user_id` for multi-tenant isolation
- [x] **Indexes**: Created on `user_id` and `completed` columns
- [x] **Connection Pooling**: Configured in database engine

### ✅ Development Workflow Compliance
- [x] **Specification Created**: `/specs/001-backend-todo-api/spec.md` exists
- [x] **Planning in Progress**: This plan.md being generated
- [x] **Tasks Next**: Will generate tasks.md via `/sp.tasks`
- [x] **Claude Code Implementation**: Will implement via `/sp.implement`

**Constitution Check Result**: ✅ PASSED - All constitutional requirements satisfied

## Project Structure

### Documentation (this feature)

```text
specs/001-backend-todo-api/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - architecture decisions
├── data-model.md        # Phase 1 output - database schema design
├── quickstart.md        # Phase 1 output - setup and run instructions
├── contracts/           # Phase 1 output - API contract definitions
│   └── openapi.yaml     # OpenAPI 3.0 specification
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management (env vars)
│   ├── database.py          # Database connection & session management
│   ├── models.py            # SQLModel database models (User, Task)
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── middleware.py    # JWT verification logic
│   │   └── dependencies.py  # FastAPI auth dependencies
│   ├── routes/
│   │   ├── __init__.py
│   │   └── tasks.py         # Task CRUD endpoints
│   └── utils/
│       ├── __init__.py
│       └── exceptions.py    # Custom exception handlers
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures (test client, auth, DB)
│   ├── test_auth.py         # Authentication tests
│   ├── test_tasks_create.py # Task creation tests
│   ├── test_tasks_read.py   # Task retrieval tests
│   ├── test_tasks_update.py # Task update tests
│   ├── test_tasks_delete.py # Task deletion tests
│   └── test_user_isolation.py # Security isolation tests
├── alembic/                 # Database migrations (if needed)
│   ├── versions/
│   └── env.py
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variable template
├── alembic.ini             # Alembic configuration (if needed)
├── Dockerfile              # Container definition
└── README.md               # Backend-specific documentation
```

**Structure Decision**: Web backend API structure selected because this is a FastAPI backend component of a larger monorepo. The backend directory is separate from the frontend per constitutional monorepo organization requirements. Code is organized by technical layer (models, schemas, routes, auth) with clear separation of concerns.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All design decisions align with constitutional requirements.

## Phase 0: Research & Decisions

### Architecture Decisions

#### Decision 1: Database Connection Management
**Decision**: Use SQLModel's `create_engine` with connection pooling (pool_size=5, max_overflow=10)
**Rationale**:
- Neon PostgreSQL is serverless and benefits from connection reuse
- Connection pooling reduces overhead for concurrent requests
- Matches constitutional requirement for production performance
**Alternatives Considered**:
- Direct connection per request: Rejected due to high overhead
- External connection pooler (PgBouncer): Rejected as unnecessary for initial scale
**References**: SQLModel documentation, Neon PostgreSQL best practices

#### Decision 2: JWT Verification Strategy
**Decision**: Verify JWT tokens using PyJWT library with shared secret from environment variable
**Rationale**:
- Better Auth uses HS256 algorithm with symmetric key
- Synchronous verification sufficient for performance goals (<500ms)
- No external service dependency for token validation
**Alternatives Considered**:
- Async JWT verification: Rejected as synchronous is fast enough
- Public key verification (RS256): Rejected as Better Auth uses HS256
**References**: Better Auth documentation, PyJWT library

#### Decision 3: User Isolation Implementation
**Decision**: Enforce user isolation at query level by filtering on `user_id` extracted from JWT
**Rationale**:
- Prevents accidental cross-user data leaks
- Fail-secure design: all queries require explicit user_id filter
- Matches constitutional security-first principle
**Alternatives Considered**:
- Row-level security in PostgreSQL: Rejected as adds complexity for initial version
- Application-level ACL system: Rejected as overkill for simple user ownership
**References**: OWASP security guidelines, FastAPI security patterns

#### Decision 4: Error Response Format
**Decision**: Return all errors as JSON with `{"detail": "user-friendly message"}` structure
**Rationale**:
- Consistent error format across all endpoints
- Matches FastAPI's default HTTPException format
- Frontend can easily parse and display errors
**Alternatives Considered**:
- RFC 7807 Problem Details: Rejected as too verbose for simple API
- Custom error schema: Rejected to avoid reinventing standard
**References**: FastAPI documentation, REST API best practices

#### Decision 5: API URL Pattern
**Decision**: Use pattern `/api/{user_id}/tasks[/{task_id}]` for all task operations
**Rationale**:
- Makes user scope explicit in URL structure
- Supports future per-user rate limiting by user_id
- Clear resource hierarchy: user → tasks → specific task
**Alternatives Considered**:
- Implicit user from token only: Rejected as less RESTful and harder to cache
- `/api/tasks` with user_id in body: Rejected as violates REST resource identification
**References**: REST API design patterns, RESTful Web Services book

#### Decision 6: Database Migration Strategy
**Decision**: Use SQLModel's `metadata.create_all()` for initial version; defer Alembic to future iteration
**Rationale**:
- Simpler for initial deployment and development
- Sufficient for greenfield project with no existing data
- Can add Alembic later when schema changes become frequent
**Alternatives Considered**:
- Alembic from start: Rejected as premature for initial version
- Manual SQL migrations: Rejected as error-prone and not version-controlled
**References**: SQLModel documentation, database migration best practices

#### Decision 7: Testing Strategy
**Decision**: Focus on integration tests using FastAPI TestClient with test database
**Rationale**:
- Integration tests validate entire request → database → response flow
- Easier to maintain than extensive mocking
- Catches more real-world issues (authentication, serialization, etc.)
**Alternatives Considered**:
- Heavy unit testing with mocks: Rejected as brittle and time-consuming
- End-to-end tests only: Rejected as too slow for development feedback
**References**: FastAPI testing documentation, pytest best practices

#### Decision 8: Timestamp Management
**Decision**: Use `datetime.utcnow()` with `default_factory` for created_at/updated_at
**Rationale**:
- Application-level timestamps ensure consistency across all clients
- UTC eliminates timezone ambiguity per constitutional requirement
- SQLModel supports default_factory pattern cleanly
**Alternatives Considered**:
- Database-level DEFAULT CURRENT_TIMESTAMP: Rejected to keep logic in code
- Timezone-aware timestamps: Rejected as UTC-only per constitution
**References**: Python datetime documentation, database timestamp patterns

### Technology Best Practices

#### FastAPI Best Practices
- Use dependency injection for database sessions (`Depends(get_session)`)
- Use dependency injection for authentication (`Depends(get_current_user)`)
- Leverage automatic validation via Pydantic models
- Enable CORS middleware with explicit origins only
- Use lifespan events for startup/shutdown logic
- Separate route definitions into modular router files

#### SQLModel Best Practices
- Define table models with `table=True` parameter
- Use `Optional[int]` for auto-increment primary keys
- Use `Field(foreign_key="...")` for relationships
- Define indexes via `Field(index=True)` where needed
- Use `Session.exec(select(...))` for type-safe queries
- Always use context managers for session lifecycle

#### Security Best Practices
- Never log JWT tokens or secrets
- Validate JWT signature before processing claims
- Return 404 (not 403) for other users' resources to prevent enumeration
- Use parameterized queries exclusively (via ORM)
- Set CORS allow_credentials=True only with specific origins
- Sanitize error messages to avoid information disclosure

#### Performance Best Practices
- Use connection pooling with appropriate pool size
- Add database indexes on foreign keys and frequently filtered columns
- Use `pool_pre_ping=True` to verify connections before use
- Defer pagination until performance testing shows need
- Use `select()` queries to load only needed columns
- Profile slow queries if p95 latency exceeds targets

## Phase 1: Design & Contracts

See generated files:
- [data-model.md](./data-model.md) - Database schema and entity relationships
- [contracts/openapi.yaml](./contracts/openapi.yaml) - Complete API specification
- [quickstart.md](./quickstart.md) - Setup and development instructions

---

*Planning complete. Next: run `/sp.tasks` to generate dependency-ordered implementation tasks.*
