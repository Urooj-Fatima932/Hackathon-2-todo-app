# Research: Better Auth JWT Integration Patterns

**Feature**: Better Auth JWT Integration for Task Management
**Date**: 2026-02-08
**Status**: Complete

## Overview

This document captures research findings and technology decisions for integrating Better Auth authentication library on Next.js 14 frontend with JWT-based authorization for FastAPI backend task management APIs.

---

## 1. Better Auth Configuration for Next.js 14 App Router

### Decision

Use Better Auth library with Next.js 14 App Router, configured to generate JWT tokens with HS256 signing algorithm. Install `better-auth` package and configure it with database adapter, session management, and JWT settings.

### Rationale

- **Framework Compatibility**: Better Auth is designed for TypeScript/JavaScript frameworks including Next.js 14 App Router
- **Built-in JWT Support**: Native JWT token generation with customizable payload and signing algorithms
- **App Router Patterns**: Supports server components, server actions, and route handlers
- **Session Management**: Handles session storage, token refresh, and secure cookie management
- **Type Safety**: Full TypeScript support with type-safe authentication hooks

### Alternatives Considered

1. **NextAuth.js (Auth.js)**: More established but heavier, complex provider configuration
2. **Clerk**: SaaS solution with vendor lock-in, less control over JWT payload
3. **Custom JWT Implementation**: More work, no session management out of the box
4. **Supabase Auth**: Requires Supabase backend, not compatible with existing FastAPI

### Implementation Notes

**Installation**:
```bash
npm install better-auth
```

**Configuration** (`lib/auth.ts`):
```typescript
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  database: {
    // Database connection for session storage
    provider: "postgres",
    url: process.env.DATABASE_URL
  },
  jwt: {
    secret: process.env.BETTER_AUTH_SECRET!,
    algorithm: "HS256",
    expiresIn: "24h"
  },
  session: {
    cookieName: "auth_session",
    maxAge: 60 * 60 * 24 // 24 hours
  }
})
```

**Client Setup** (`components/auth/auth-provider.tsx`):
```typescript
"use client"
import { SessionProvider } from "better-auth/react"

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return <SessionProvider>{children}</SessionProvider>
}
```

**Server-Side Session Check**:
```typescript
import { auth } from "@/lib/auth"

export async function getServerSession() {
  return await auth.api.getSession({
    headers: headers() // Next.js headers()
  })
}
```

**Environment Variables**:
```
BETTER_AUTH_SECRET=<your-secret-key>
DATABASE_URL=<postgres-connection-string>
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 2. FastAPI JWT Verification with PyJWT

### Decision

Use PyJWT library (already in requirements.txt) to verify HS256-signed JWT tokens in FastAPI dependency injection pattern. Create reusable `get_current_user` dependency for route protection.

### Rationale

- **Standard Library**: PyJWT is the de facto standard for JWT handling in Python
- **Algorithm Support**: Full support for HS256 symmetric signing
- **Security Features**: Built-in token expiration, signature verification, claim validation
- **FastAPI Integration**: Works seamlessly with dependency injection pattern
- **Lightweight**: No heavy dependencies, fast verification

### Alternatives Considered

1. **python-jose**: More features but heavier, includes cryptography extras
2. **authlib**: Full OAuth/OIDC suite, overkill for JWT-only verification
3. **Custom JWT parsing**: Insecure, error-prone, reinventing the wheel

### Implementation Notes

**JWT Verification Utility** (`app/auth/jwt.py`):
```python
import jwt
from datetime import datetime
from fastapi import HTTPException, status
from app.config import settings

def verify_jwt_token(token: str) -> dict:
    """
    Verify JWT token and return decoded payload.

    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )

def extract_user_from_token(payload: dict) -> dict:
    """Extract user identity from JWT payload."""
    user_id = payload.get("sub") or payload.get("userId")
    email = payload.get("email")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier"
        )

    return {
        "user_id": user_id,
        "email": email
    }
```

**FastAPI Dependency** (`app/auth/dependencies.py`):
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt import verify_jwt_token, extract_user_from_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    FastAPI dependency to extract and verify current user from JWT token.

    Usage:
        @app.get("/api/tasks")
        async def get_tasks(user: dict = Depends(get_current_user)):
            user_id = user["user_id"]
            # ... fetch tasks for user_id
    """
    token = credentials.credentials
    payload = verify_jwt_token(token)
    user = extract_user_from_token(payload)
    return user
```

**Protected Route Example**:
```python
from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/api/tasks")
async def list_tasks(user: dict = Depends(get_current_user)):
    user_id = user["user_id"]
    # Query tasks filtered by user_id
    tasks = await Task.get_by_user_id(user_id)
    return tasks
```

**Configuration** (`app/config.py`):
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    JWT_SECRET: str
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 3. SQLModel User Model with Password Hashing

### Decision

Use SQLModel for User and Task models with `passlib` (bcrypt) for password hashing. Store hashed passwords in database, never plain text.

### Rationale

- **SQLModel Integration**: Already used in the project, type-safe ORM
- **Bcrypt Security**: Industry standard, designed for password hashing with built-in salting
- **Passlib Flexibility**: Abstraction layer over bcrypt, easy to upgrade algorithms later
- **Performance**: Bcrypt cost factor tunable for security/performance balance

### Alternatives Considered

1. **Argon2**: More modern, won a password hashing competition, but requires C dependencies
2. **PBKDF2**: Built into Python, but slower and less resistant to GPU attacks
3. **Scrypt**: Good security but higher memory requirements
4. **Plain bcrypt**: Passlib provides better abstraction and future-proofing

### Implementation Notes

**Installation**:
```bash
pip install passlib[bcrypt]
```

**User Model** (`app/models.py`):
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(nullable=False)
    description: Optional[str] = None
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Password Hashing Utilities** (`app/auth/password.py`):
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

**User Registration Example**:
```python
from app.auth.password import hash_password

async def create_user(email: str, password: str) -> User:
    hashed_password = hash_password(password)
    user = User(
        email=email,
        hashed_password=hashed_password
    )
    # Save to database
    session.add(user)
    await session.commit()
    return user
```

---

## 4. JWT Secret Management

### Decision

Store JWT secrets in environment variables (`.env` files), use different secrets for development and production, document rotation procedure.

### Rationale

- **Security Best Practice**: Never commit secrets to version control
- **Environment Isolation**: Separate secrets prevent token reuse across environments
- **Easy Rotation**: Change environment variable without code changes
- **12-Factor App**: Follows industry-standard configuration management

### Alternatives Considered

1. **Secrets Manager (AWS/GCP/Azure)**: Overkill for MVP, adds complexity and cost
2. **Encrypted Config Files**: Requires key management, still a bootstrapping problem
3. **Hardcoded Secrets**: NEVER - severe security vulnerability
4. **Database Storage**: Chicken-and-egg problem, not suitable for JWT signing

### Implementation Notes

**Secret Generation**:
```bash
# Generate secure random secret (32 bytes = 256 bits)
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Or
openssl rand -base64 32
```

**Backend Environment Variables** (`.env.example`):
```bash
# JWT Configuration
JWT_SECRET=<generate-secure-random-secret>

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/taskdb

# Environment
ENVIRONMENT=development
```

**Frontend Environment Variables** (`.env.local.example`):
```bash
# Better Auth Configuration
BETTER_AUTH_SECRET=<same-as-backend-JWT_SECRET>
DATABASE_URL=postgresql://user:password@localhost:5432/taskdb

# API Backend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**CRITICAL**: The `JWT_SECRET` (backend) and `BETTER_AUTH_SECRET` (frontend) **MUST be identical** for token verification to work.

**Secret Rotation Procedure**:
1. Generate new secret
2. Update both frontend and backend `.env` files
3. Restart both services simultaneously
4. All existing tokens become invalid (users must re-login)
5. Document the rotation date for audit purposes

**Production Security**:
- Use different secrets for dev/staging/production
- Store production secrets in secure secret management service
- Rotate secrets quarterly or after suspected compromise
- Never log or expose secrets in error messages
- Use HTTPS to prevent token interception in transit

---

## 5. Testing Authenticated Endpoints

### Decision

Use pytest fixtures to generate test JWT tokens for backend testing. Create reusable fixtures for authenticated test clients and mock user contexts.

### Rationale

- **Test Isolation**: Each test gets fresh authentication context
- **Reusability**: Fixtures eliminate duplicate token generation code
- **Realistic Testing**: Tests use actual JWT verification code paths
- **Fast Execution**: No need to spin up full auth flow for each test
- **Coverage**: Can test both authenticated and unauthenticated scenarios

### Alternatives Considered

1. **Mock JWT verification**: Faster but doesn't test real verification logic
2. **Full auth flow per test**: More realistic but much slower
3. **Shared test tokens**: Fast but risks test interdependence
4. **Database seeding**: Good for integration tests but slower

### Implementation Notes

**pytest Configuration** (`backend/tests/conftest.py`):
```python
import pytest
import jwt
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.main import app
from app.config import settings

@pytest.fixture
def client():
    """Test client without authentication."""
    return TestClient(app)

@pytest.fixture
def test_user():
    """Mock user data for testing."""
    return {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "test@example.com"
    }

@pytest.fixture
def auth_token(test_user):
    """Generate valid JWT token for testing."""
    payload = {
        "sub": test_user["user_id"],
        "email": test_user["email"],
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token

@pytest.fixture
def authenticated_client(client, auth_token):
    """Test client with authentication headers."""
    client.headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    return client
```

**Test Examples** (`backend/tests/test_tasks.py`):
```python
def test_list_tasks_unauthenticated(client):
    """Test that unauthenticated requests are rejected."""
    response = client.get("/api/tasks")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_list_tasks_authenticated(authenticated_client, test_user):
    """Test that authenticated users can list their tasks."""
    response = authenticated_client.get("/api/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)

def test_create_task_with_ownership(authenticated_client, test_user):
    """Test that created tasks are associated with the user."""
    task_data = {"title": "Test Task", "description": "Test Description"}
    response = authenticated_client.post("/api/tasks", json=task_data)
    assert response.status_code == 201
    task = response.json()
    assert task["user_id"] == test_user["user_id"]

def test_cannot_access_other_users_tasks(client, auth_token):
    """Test authorization enforcement for task ownership."""
    # Create task as user A
    client.headers = {"Authorization": f"Bearer {auth_token}"}
    task_response = client.post("/api/tasks", json={"title": "User A Task"})
    task_id = task_response.json()["id"]

    # Generate token for user B
    other_user_token = jwt.encode(
        {"sub": "different-user-id", "email": "other@example.com"},
        settings.JWT_SECRET,
        algorithm="HS256"
    )

    # Try to access as user B
    client.headers = {"Authorization": f"Bearer {other_user_token}"}
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 403
```

**Frontend Testing Patterns**:

For Next.js frontend with React Testing Library:

```typescript
// tests/helpers/auth.ts
import { render } from "@testing-library/react"
import { SessionProvider } from "better-auth/react"

export function renderWithAuth(component: React.ReactElement, session = mockSession) {
  return render(
    <SessionProvider session={session}>
      {component}
    </SessionProvider>
  )
}

export const mockSession = {
  user: { id: "test-user-id", email: "test@example.com" },
  token: "mock-jwt-token"
}
```

---

## 6. JWT Payload Structure

### Decision

Standardize JWT payload format between Better Auth (frontend) and FastAPI (backend) to ensure consistent user identification.

### Rationale

- **Interoperability**: Both services must understand the same token format
- **Standard Claims**: Use JWT standard claims (`sub`, `exp`, `iat`) plus custom claims
- **Minimal Payload**: Only include necessary user identity, keep tokens small
- **No Sensitive Data**: Never include passwords or sensitive PII in tokens

### Implementation Notes

**Standard JWT Payload Structure**:
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // User ID (standard claim)
  "email": "user@example.com",                     // User email (custom claim)
  "iat": 1672531200,                               // Issued at timestamp
  "exp": 1672617600                                // Expiration timestamp
}
```

**Better Auth Configuration**:
```typescript
export const auth = betterAuth({
  jwt: {
    encode: (payload) => ({
      sub: payload.userId,
      email: payload.email,
      exp: Math.floor(Date.now() / 1000) + 60 * 60 * 24  // 24 hours
    })
  }
})
```

**Backend Extraction**:
```python
def extract_user_from_token(payload: dict) -> dict:
    user_id = payload.get("sub")  # Standard JWT subject claim
    email = payload.get("email")   # Custom claim
    return {"user_id": user_id, "email": email}
```

---

## Summary of Key Decisions

| Component | Decision | Key Rationale |
|-----------|----------|---------------|
| Frontend Auth | Better Auth with HS256 JWT | Native Next.js 14 support, built-in session management |
| Backend Verification | PyJWT with FastAPI dependencies | Industry standard, clean dependency injection |
| Password Hashing | passlib[bcrypt] | Industry standard, future-proof abstraction |
| Secret Management | Environment variables | 12-factor app pattern, easy rotation |
| Testing | pytest fixtures with real JWTs | Test actual code paths, reusable patterns |
| JWT Payload | Standard claims + email | Minimal, standard, interoperable |

---

## References & Resources

- **Better Auth Documentation**: https://better-auth.com/docs
- **PyJWT Documentation**: https://pyjwt.readthedocs.io/
- **FastAPI Security**: https://fastapi.tiangolo.com/tutorial/security/
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **JWT Standard (RFC 7519)**: https://datatracker.ietf.org/doc/html/rfc7519
- **OWASP Password Storage**: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

---

## Next Steps

1. ✅ Research completed
2. **Phase 1**: Create data-model.md with entity definitions
3. **Phase 1**: Generate API contracts (auth-api.yaml, tasks-api.yaml)
4. **Phase 1**: Write quickstart.md with setup instructions
5. **Phase 2**: Generate tasks.md with `/sp.tasks` command
