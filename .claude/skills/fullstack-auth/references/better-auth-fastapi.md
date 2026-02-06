# Better Auth - FastAPI Integration

## Overview

FastAPI integrates with Better Auth by validating JWT tokens or session cookies issued by the Next.js frontend. This enables a unified auth system where users authenticate via Better Auth on the frontend, and the backend validates those credentials.

## Project Structure

```
app/
├── core/
│   ├── config.py              # Settings/configuration
│   ├── db.py                  # Database setup
│   └── deps.py                # Common dependencies
├── auth/
│   ├── __init__.py
│   ├── jwt.py                 # JWT utilities
│   ├── dependencies.py        # Auth dependencies
│   └── router.py              # Auth endpoints (optional)
├── models/
│   └── user.py                # User model
└── main.py
```

## Configuration

### core/config.py

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    DATABASE_URL: str
    DIRECT_URL: str | None = None

    # JWT Configuration (shared with Better Auth)
    BETTER_AUTH_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"


settings = Settings()
```

### .env

```bash
# Database (Neon)
DATABASE_URL="postgresql+asyncpg://user:pass@ep-xxx.neon.tech/dbname?sslmode=require"
DIRECT_URL="postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require"

# JWT - Use same secret as Better Auth
BETTER_AUTH_SECRET="your-better-auth-secret-from-nextjs"
JWT_ALGORITHM="HS256"

# CORS
FRONTEND_URL="http://localhost:3000"
```

## JWT Utilities

### auth/jwt.py

```python
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt, JWTError

from app.core.config import settings


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(
        to_encode,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(
        to_encode,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> dict[str, Any] | None:
    """Verify a JWT token and check its type."""
    payload = decode_token(token)
    if payload is None:
        return None
    if payload.get("type") != token_type:
        return None
    return payload


def verify_better_auth_session(session_token: str) -> dict[str, Any] | None:
    """
    Verify a Better Auth session token.
    Better Auth sessions are stored in the database, so this validates
    the token format and expiry, then we look up the session.
    """
    payload = decode_token(session_token)
    if payload is None:
        return None

    # Check expiry
    exp = payload.get("exp")
    if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
        return None

    return payload
```

## Auth Dependencies

### auth/dependencies.py

```python
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth.jwt import decode_token, verify_token
from app.core.deps import get_session
from app.models.session import Session as AuthSession
from app.models.user import User

# Bearer token security
security = HTTPBearer(auto_error=False)


async def get_user_from_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> User | None:
    """
    Extract user from Bearer token (JWT).
    Returns None if no token or invalid token.
    """
    if not credentials:
        return None

    payload = verify_token(credentials.credentials, "access")
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_from_session_cookie(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_session)],
    better_auth_session: str | None = Cookie(default=None, alias="better-auth.session_token"),
) -> User | None:
    """
    Extract user from Better Auth session cookie.
    Returns None if no session or invalid session.
    """
    if not better_auth_session:
        return None

    # Look up session in database
    result = await db.execute(
        select(AuthSession).where(AuthSession.token == better_auth_session)
    )
    session = result.scalar_one_or_none()

    if not session:
        return None

    # Check if session is expired
    if session.expires_at < datetime.now(timezone.utc):
        return None

    # Get user
    user = await db.get(User, session.user_id)
    return user


async def get_current_user(
    token_user: Annotated[User | None, Depends(get_user_from_token)],
    session_user: Annotated[User | None, Depends(get_user_from_session_cookie)],
) -> User:
    """
    Get current authenticated user from either JWT token or session cookie.
    Raises 401 if not authenticated.
    """
    user = token_user or session_user

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current user and verify they are active."""
    if hasattr(current_user, "is_active") and not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def get_optional_user(
    token_user: Annotated[User | None, Depends(get_user_from_token)],
    session_user: Annotated[User | None, Depends(get_user_from_session_cookie)],
) -> User | None:
    """
    Get current user if authenticated, None otherwise.
    Does not raise exception for unauthenticated requests.
    """
    return token_user or session_user


# Type aliases for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
ActiveUser = Annotated[User, Depends(get_current_active_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
```

## Role-Based Access Control

### auth/rbac.py

```python
from typing import Annotated
from functools import wraps

from fastapi import Depends, HTTPException, status

from app.auth.dependencies import CurrentUser
from app.models.user import User


def require_role(*required_roles: str):
    """
    Dependency factory that requires user to have one of the specified roles.

    Usage:
        @router.get("/admin")
        async def admin_route(user: AdminUser):
            ...

        AdminUser = Annotated[User, Depends(require_role("admin"))]
    """
    async def role_checker(current_user: CurrentUser) -> User:
        user_role = getattr(current_user, "role", None)

        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {' or '.join(required_roles)}",
            )

        return current_user

    return role_checker


def require_any_role(*roles: str):
    """Alias for require_role with multiple options."""
    return require_role(*roles)


def require_all_roles(*roles: str):
    """Require user to have ALL specified roles."""
    async def role_checker(current_user: CurrentUser) -> User:
        user_roles = getattr(current_user, "roles", [])

        if not all(role in user_roles for role in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required roles: {', '.join(roles)}",
            )

        return current_user

    return role_checker


# Pre-defined role dependencies
AdminUser = Annotated[User, Depends(require_role("admin"))]
ModeratorUser = Annotated[User, Depends(require_role("moderator", "admin"))]
```

## Protected Routes

### Basic Protection

```python
from fastapi import APIRouter

from app.auth.dependencies import CurrentUser, OptionalUser

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/me")
async def get_current_user_info(user: CurrentUser):
    """Get current authenticated user's information."""
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
    }


@router.get("/posts")
async def list_posts(user: OptionalUser):
    """List posts - personalized if authenticated."""
    if user:
        return {"posts": [], "personalized": True, "user_id": user.id}
    return {"posts": [], "personalized": False}
```

### Role-Based Protection

```python
from app.auth.rbac import AdminUser, ModeratorUser


@router.get("/admin/users")
async def list_all_users(admin: AdminUser):
    """Admin-only: List all users."""
    return {"users": []}


@router.delete("/posts/{post_id}")
async def delete_post(post_id: int, moderator: ModeratorUser):
    """Moderator or Admin: Delete a post."""
    return {"deleted": post_id}
```

### Router-Level Protection

```python
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user

# All routes in this router require authentication
protected_router = APIRouter(
    prefix="/protected",
    tags=["protected"],
    dependencies=[Depends(get_current_user)],
)


@protected_router.get("/data")
async def get_protected_data():
    """Already authenticated via router dependency."""
    return {"data": "secret"}


@protected_router.post("/action")
async def protected_action():
    """Already authenticated via router dependency."""
    return {"success": True}
```

## Auth Router (Optional Local Auth)

### auth/router.py

```python
from typing import Annotated
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from passlib.context import CryptContext

from app.core.deps import get_session
from app.core.config import settings
from app.models.user import User
from app.auth.jwt import create_access_token, create_refresh_token, verify_token
from app.auth.schemas import Token, TokenRefresh, UserCreate, UserResponse


router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """Register a new user with email/password."""
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        email=user_in.email,
        name=user_in.name,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """Login with email/password and get JWT tokens."""
    # Find user
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """Refresh access token using refresh token."""
    payload = verify_token(token_data.refresh_token, "refresh")
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )
```

### auth/schemas.py

```python
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str | None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str
```

## CORS Configuration

### main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(title="API")

# CORS for Better Auth frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
    ],
    allow_credentials=True,  # Important for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Session Validation from Better Auth

If you want to validate Better Auth sessions directly (looking up the session in the shared database):

```python
from sqlmodel import select
from app.models.session import Session as AuthSession


async def validate_better_auth_session(
    session_token: str,
    db: AsyncSession,
) -> User | None:
    """
    Validate a Better Auth session token by looking it up in the database.
    This is useful when you share the same database between Next.js and FastAPI.
    """
    # Find session
    result = await db.execute(
        select(AuthSession).where(AuthSession.token == session_token)
    )
    session = result.scalar_one_or_none()

    if not session:
        return None

    # Check expiry
    from datetime import datetime, timezone
    if session.expires_at < datetime.now(timezone.utc):
        return None

    # Get user
    user = await db.get(User, session.user_id)
    return user
```

## Testing Auth

```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_protected_route_without_auth():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/me")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_auth(auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/me", headers=auth_headers)
        assert response.status_code == 200
        assert "email" in response.json()
```
