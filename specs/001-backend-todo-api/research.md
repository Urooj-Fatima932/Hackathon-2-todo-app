# Research & Architecture Decisions

**Feature**: Backend Todo API
**Date**: 2026-02-06
**Purpose**: Document all architectural decisions and technology research for implementation planning

## Research Summary

This document consolidates all architectural decisions made during the planning phase. Each decision includes the chosen approach, rationale, alternatives considered, and references to authoritative sources.

## Key Architecture Decisions

### 1. Database Connection Management

**Decision**: Use SQLModel's `create_engine` with connection pooling (pool_size=5, max_overflow=10)

**Rationale**:
- Neon PostgreSQL is serverless and benefits from connection reuse to minimize cold start overhead
- Connection pooling reduces per-request connection establishment time (50-100ms savings)
- Pool size of 5 with max overflow of 10 supports 100 concurrent users per constitutional requirement
- `pool_pre_ping=True` ensures connections are valid before use, critical for serverless databases

**Alternatives Considered**:
1. **Direct connection per request**: Simple but wasteful
   - Overhead: ~100ms per request for connection establishment
   - Rejected: Violates <500ms performance target for task creation
2. **External connection pooler (PgBouncer)**: Industry standard for high-scale systems
   - Adds operational complexity (another service to deploy/monitor)
   - Rejected: Unnecessary for initial 100 concurrent user target

**Implementation Details**:
```python
engine = create_engine(
    DATABASE_URL,
    echo=DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)
```

**References**:
- SQLModel documentation on engine configuration
- Neon PostgreSQL connection pooling best practices
- SQLAlchemy engine configuration guide

---

### 2. JWT Verification Strategy

**Decision**: Verify JWT tokens synchronously using PyJWT library with shared secret from environment variable

**Rationale**:
- Better Auth issues JWT tokens signed with HS256 algorithm (symmetric key)
- Shared secret (`BETTER_AUTH_SECRET`) must match between auth system and this API
- Synchronous verification adds <5ms latency, well within <500ms budget
- No external service dependency eliminates network call overhead and failure modes
- PyJWT is industry-standard Python library with strong security track record

**Alternatives Considered**:
1. **Async JWT verification**: More complex for minimal benefit
   - Verification is CPU-bound, not I/O-bound
   - Async overhead (event loop switching) negates any gains
   - Rejected: Adds complexity without performance improvement
2. **Public key verification (RS256)**: Asymmetric cryptography
   - Requires public key distribution mechanism
   - Better Auth uses HS256, not RS256
   - Rejected: Not compatible with authentication system

**Implementation Details**:
```python
import jwt

JWT_SECRET = os.getenv("BETTER_AUTH_SECRET")
JWT_ALGORITHM = "HS256"

payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
user_id = payload["sub"]  # Extract user ID from token
```

**Security Considerations**:
- Secret must be at least 32 characters (256 bits for HS256)
- Never log the JWT token or secret
- Validate token expiration (`exp` claim)
- Handle expired and invalid tokens with 401 Unauthorized

**References**:
- PyJWT library documentation
- Better Auth JWT configuration
- RFC 7519 (JSON Web Token specification)

---

### 3. User Isolation Implementation

**Decision**: Enforce user isolation at database query level by filtering on `user_id` extracted from JWT token

**Rationale**:
- **Fail-secure design**: Every query explicitly filters by authenticated user_id
- Prevents accidental cross-user data leaks (developer error protection)
- Aligns with constitutional security-first principle (Principle III)
- Simple to audit: search codebase for queries without `.where(Task.user_id == user_id)`
- Performance: `user_id` index makes filtered queries fast (<10ms)

**Alternatives Considered**:
1. **Row-Level Security (RLS) in PostgreSQL**: Database-level enforcement
   - Pros: Impossible to bypass, even with SQL injection
   - Cons: Adds complexity, harder to debug, requires database migrations
   - Rejected: Overkill for initial version; application-level sufficient
2. **Application-level ACL system**: Centralized authorization service
   - Pros: More flexible for complex permissions
   - Cons: Unnecessary for simple user ownership model
   - Rejected: Over-engineering for binary owner/not-owner model

**Implementation Pattern**:
```python
# Correct: User isolation enforced
tasks = session.exec(
    select(Task).where(Task.user_id == current_user.sub)
).all()

# WRONG: Would return all users' tasks (security violation)
tasks = session.exec(select(Task)).all()
```

**Verification Strategy**:
- Integration tests must verify user A cannot access user B's tasks
- Test must verify 404 response (not 403) to prevent enumeration attacks

**References**:
- OWASP Top 10: Broken Access Control (A01:2021)
- FastAPI security best practices
- PostgreSQL Row-Level Security documentation

---

### 4. Error Response Format

**Decision**: Return all errors as JSON with `{"detail": "user-friendly message"}` structure

**Rationale**:
- Consistent error format across all endpoints simplifies frontend error handling
- Matches FastAPI's default `HTTPException` format (framework convention)
- Frontend can display `detail` field directly to users
- Structured JSON enables programmatic error handling by clients

**Alternatives Considered**:
1. **RFC 7807 Problem Details**: Standardized error format with `type`, `title`, `status`, `detail`, `instance`
   - Pros: Industry standard, rich error metadata
   - Cons: More verbose, frontend must parse multiple fields
   - Rejected: Overkill for simple API with straightforward errors
2. **Custom error schema**: Application-specific format
   - Pros: Maximum flexibility
   - Cons: Reinvents wheel, requires documentation
   - Rejected: FastAPI default is sufficient and well-documented

**Error Response Examples**:
```json
// 400 Bad Request
{"detail": "Task title must be between 1 and 200 characters"}

// 401 Unauthorized
{"detail": "Token has expired"}

// 404 Not Found
{"detail": "Task not found"}

// 500 Internal Server Error
{"detail": "Internal server error"}
```

**Implementation**:
```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Task not found"
)
```

**References**:
- FastAPI exception handling documentation
- RFC 7807 (Problem Details for HTTP APIs)
- REST API error handling best practices

---

### 5. API URL Pattern Design

**Decision**: Use URL pattern `/api/{user_id}/tasks[/{task_id}]` for all task operations

**Rationale**:
- Makes user scope explicit in URL structure (RESTful resource hierarchy)
- Supports future per-user rate limiting by extracting `user_id` from path
- Clear resource nesting: user → tasks collection → specific task
- Consistent with REST principle: URLs identify resources, not actions
- Enables caching strategies based on user_id path segment

**Alternatives Considered**:
1. **Implicit user from token only**: `/api/tasks[/{task_id}]`
   - Pros: Shorter URLs, simpler routing
   - Cons: User scope not visible in URL, harder to cache, less RESTful
   - Rejected: Violates REST resource identification principles
2. **User ID in request body**: POST with `user_id` in JSON body
   - Pros: None (anti-pattern)
   - Cons: Violates REST (URLs should identify resources), breaks caching
   - Rejected: Fundamentally non-RESTful design

**API Endpoint Mapping**:
```text
GET    /api/{user_id}/tasks              → List user's tasks
POST   /api/{user_id}/tasks              → Create new task
GET    /api/{user_id}/tasks/{task_id}    → Get specific task
PUT    /api/{user_id}/tasks/{task_id}    → Update task (full)
PATCH  /api/{user_id}/tasks/{task_id}    → Update task (partial)
DELETE /api/{user_id}/tasks/{task_id}    → Delete task
PATCH  /api/{user_id}/tasks/{task_id}/complete → Toggle completion
```

**Security Check**:
- Verify `user_id` in path matches `sub` claim in JWT
- Return 403 Forbidden if mismatch detected
- Prevents user A from accessing `/api/user_b/tasks`

**References**:
- RESTful Web Services (Leonard Richardson & Sam Ruby)
- REST API design patterns
- FastAPI path parameters documentation

---

### 6. Database Migration Strategy

**Decision**: Use SQLModel's `metadata.create_all()` for initial version; defer Alembic to future iteration

**Rationale**:
- Simpler setup for greenfield project with no existing database
- Sufficient for development and initial production deployment
- No schema changes expected during initial implementation
- Can add Alembic later when iterative schema changes become necessary
- Reduces initial complexity and setup time

**Alternatives Considered**:
1. **Alembic from start**: Industry-standard migration tool for SQLAlchemy/SQLModel
   - Pros: Versioned schema changes, rollback capability, production-ready
   - Cons: Additional setup, overkill for initial greenfield deployment
   - Rejected: Premature optimization for project with stable initial schema
2. **Manual SQL migrations**: Run SQL scripts directly
   - Pros: Maximum control
   - Cons: Error-prone, not version-controlled, manual tracking required
   - Rejected: Does not integrate with application code

**Implementation**:
```python
# app/main.py
from app.database import engine
from app.models import SQLModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if they don't exist
    SQLModel.metadata.create_all(engine)
    yield
    # Shutdown
    pass
```

**Migration Path**:
When schema changes become frequent:
1. Initialize Alembic: `alembic init alembic`
2. Generate initial migration from current schema: `alembic revision --autogenerate`
3. Apply migrations: `alembic upgrade head`

**References**:
- SQLModel documentation on table creation
- Alembic documentation
- Database migration best practices

---

### 7. Testing Strategy

**Decision**: Focus on integration tests using FastAPI TestClient with test database

**Rationale**:
- Integration tests validate entire request/response flow including authentication, validation, serialization
- Easier to maintain than extensive mocking (fewer brittle tests)
- Catches real-world issues: JWT parsing, SQL serialization, timestamp formatting
- TestClient runs tests synchronously without actual network overhead
- Test database ensures isolation between test runs

**Alternatives Considered**:
1. **Heavy unit testing with mocks**: Test each component in isolation
   - Pros: Fast, focused tests
   - Cons: Brittle (tests break when refactoring), misses integration bugs
   - Rejected: Time-consuming to maintain, lower value than integration tests
2. **End-to-end tests only**: Full system test with real database and authentication
   - Pros: Maximum confidence
   - Cons: Slow, flaky, hard to debug failures
   - Rejected: Too slow for development feedback loop

**Test Structure**:
```
tests/
├── conftest.py              # Fixtures: test_client, test_db, auth_headers
├── test_auth.py             # JWT verification, invalid tokens
├── test_tasks_create.py     # POST /api/{user_id}/tasks
├── test_tasks_read.py       # GET /api/{user_id}/tasks[/{task_id}]
├── test_tasks_update.py     # PUT/PATCH /api/{user_id}/tasks/{task_id}
├── test_tasks_delete.py     # DELETE /api/{user_id}/tasks/{task_id}
└── test_user_isolation.py   # Security: cross-user access attempts
```

**Test Database Strategy**:
- Use SQLite in-memory database for fast test execution
- Alternative: PostgreSQL test database (closer to production)
- Clean database between tests using fixtures

**References**:
- FastAPI testing documentation
- pytest fixtures guide
- Martin Fowler: Test Pyramid

---

### 8. Timestamp Management

**Decision**: Use `datetime.utcnow()` with `default_factory` for `created_at` and `updated_at` timestamps

**Rationale**:
- Application-level timestamps ensure consistency across all database clients
- UTC eliminates timezone ambiguity per constitutional requirement (Principle VI)
- SQLModel `default_factory` pattern cleanly handles timestamp generation
- Python `datetime` standard library (no external dependencies)
- Testable: Can mock `datetime.utcnow()` for deterministic tests

**Alternatives Considered**:
1. **Database-level DEFAULT CURRENT_TIMESTAMP**: Timestamps generated by PostgreSQL
   - Pros: Works even if application doesn't set timestamp
   - Cons: Logic split between app and database, harder to test
   - Rejected: Prefer keeping all logic in application code
2. **Timezone-aware timestamps**: Store timestamps with timezone info
   - Pros: Supports displaying times in user's local timezone
   - Cons: More complex, constitutional requirement is UTC-only
   - Rejected: Constitution mandates UTC for all timestamps

**Implementation**:
```python
from datetime import datetime
from sqlmodel import Field

class Task(SQLModel, table=True):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Update Strategy**:
When updating tasks, explicitly set `updated_at`:
```python
task.updated_at = datetime.utcnow()
session.add(task)
session.commit()
```

**References**:
- Python datetime documentation
- SQLModel Field default_factory
- Database timestamp patterns

---

## Technology Best Practices

### FastAPI Development

**Dependency Injection**:
- Use `Depends()` for database sessions: `session: Session = Depends(get_session)`
- Use `Depends()` for authentication: `current_user: JWTPayload = Depends(get_current_user)`
- Benefits: Testable (can override dependencies), clean separation of concerns

**Automatic Validation**:
- Leverage Pydantic models for request/response validation
- FastAPI automatically validates request bodies against schemas
- Returns 422 Unprocessable Entity for validation errors

**CORS Middleware**:
- Enable CORS with explicit origins only (no wildcards in production)
- Set `allow_credentials=True` for cookie-based auth (JWT in Authorization header doesn't require this)
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # From environment variable
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Lifespan Events**:
- Use `@asynccontextmanager` lifespan pattern for startup/shutdown
- Create database tables on startup
- Close connections on shutdown

**Modular Routers**:
- Define routes in separate router files: `routes/tasks.py`
- Include routers in main app: `app.include_router(tasks.router)`

### SQLModel Database Operations

**Table Definitions**:
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"  # Explicit table name
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    # ... other fields
```

**Type-Safe Queries**:
```python
# Correct: Type-safe select
statement = select(Task).where(Task.user_id == user_id)
tasks = session.exec(statement).all()

# Avoid: Raw SQL strings (loses type safety)
```

**Session Management**:
```python
def get_session():
    with Session(engine) as session:
        yield session
```

### Security Implementation

**JWT Token Handling**:
- Never log JWT tokens (potential security leak)
- Validate signature before processing claims
- Check token expiration (`exp` claim)
- Handle InvalidTokenError and ExpiredSignatureError

**Resource Enumeration Prevention**:
- Return 404 (not 403) when user tries to access another user's resource
- 403 reveals resource exists; 404 hides information

**SQL Injection Prevention**:
- Use ORM parameterized queries exclusively
- Never concatenate user input into SQL strings

**Error Message Sanitization**:
- Return user-friendly messages, not stack traces
- Avoid leaking internal system details in errors

### Performance Optimization

**Connection Pooling**:
- Configure pool_size based on expected concurrent users
- Set max_overflow for burst traffic
- Use pool_pre_ping for serverless databases

**Database Indexes**:
- Add index on foreign keys: `user_id`
- Add index on frequently filtered columns: `completed`
- Add composite index for common query patterns: `(user_id, completed)`

**Query Optimization**:
- Select only needed columns (default SQLModel behavior is fine)
- Use pagination for large result sets (defer until needed)
- Profile slow queries with `echo=True` during development

---

## Summary

All architectural decisions documented above support the constitutional requirements:
- **Security-First**: JWT authentication, user isolation, input validation
- **Technology Stack**: FastAPI, SQLModel, Neon PostgreSQL as mandated
- **API Standards**: RESTful design, proper HTTP status codes, JSON format
- **Performance**: Connection pooling, indexes, <500ms target achievable
- **Maintainability**: Clean separation of concerns, testable design, type safety

Next phase: Generate data model, API contracts, and quickstart guide.
