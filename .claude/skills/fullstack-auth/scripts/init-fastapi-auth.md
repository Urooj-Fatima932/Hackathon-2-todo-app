# Initialize Better Auth Integration in FastAPI

## Overview

This script sets up FastAPI backend authentication that integrates with Better Auth on the Next.js frontend. It creates JWT validation, session management, and protected route dependencies.

## Prerequisites

- Python 3.11+
- FastAPI project initialized
- Neon PostgreSQL database
- Better Auth configured on frontend

## Installation

```bash
pip install sqlmodel asyncpg python-jose[cryptography] passlib[bcrypt] pydantic-settings httpx
```

## Project Structure

```
app/
├── core/
│   ├── __init__.py
│   ├── config.py          # Settings
│   ├── db.py              # Database setup
│   └── deps.py            # Common dependencies
├── auth/
│   ├── __init__.py
│   ├── jwt.py             # JWT utilities
│   ├── dependencies.py    # Auth dependencies
│   ├── router.py          # Auth endpoints
│   └── utils.py           # Password hashing
├── models/
│   ├── __init__.py
│   ├── user.py            # User model
│   ├── session.py         # Session model
│   └── account.py         # OAuth account model
└── main.py
```

## Step 1: Configuration

```python
# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str
    DIRECT_URL: str | None = None

    # Auth - Use same secret as Better Auth
    BETTER_AUTH_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # App
    DEBUG: bool = False
    APP_NAME: str = "FastAPI App"

    @property
    def async_database_url(self) -> str:
        """Convert to asyncpg URL."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


settings = Settings()
```

## Step 2: Database Setup

```python
# app/core/db.py
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.core.config import settings

engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,
)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def create_db_and_tables() -> None:
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for database sessions."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

## Step 3: JWT Utilities

```python
# app/auth/jwt.py
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

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
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(
        to_encode,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT token."""
    try:
        return jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> dict[str, Any] | None:
    """Verify a JWT token and check its type."""
    payload = decode_token(token)
    if payload is None or payload.get("type") != token_type:
        return None
    return payload
```

## Step 4: Password Utilities

```python
# app/auth/utils.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

## Step 5: Auth Dependencies

```python
# app/auth/dependencies.py
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth.jwt import verify_token
from app.core.db import get_session
from app.models.session import Session as AuthSession
from app.models.user import User

security = HTTPBearer(auto_error=False)


async def get_user_from_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> User | None:
    """Extract user from Bearer token."""
    if not credentials:
        return None

    payload = verify_token(credentials.credentials, "access")
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    return await db.get(User, user_id)


async def get_user_from_session_cookie(
    db: Annotated[AsyncSession, Depends(get_session)],
    better_auth_session: str | None = Cookie(
        default=None, alias="better-auth.session_token"
    ),
) -> User | None:
    """Extract user from Better Auth session cookie."""
    if not better_auth_session:
        return None

    result = await db.execute(
        select(AuthSession).where(AuthSession.token == better_auth_session)
    )
    session = result.scalar_one_or_none()

    if not session or session.expires_at < datetime.now(timezone.utc):
        return None

    return await db.get(User, session.user_id)


async def get_current_user(
    token_user: Annotated[User | None, Depends(get_user_from_token)],
    session_user: Annotated[User | None, Depends(get_user_from_session_cookie)],
) -> User:
    """Get current authenticated user."""
    user = token_user or session_user

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_optional_user(
    token_user: Annotated[User | None, Depends(get_user_from_token)],
    session_user: Annotated[User | None, Depends(get_user_from_session_cookie)],
) -> User | None:
    """Get current user if authenticated, None otherwise."""
    return token_user or session_user


# Type aliases
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
```

## Step 6: Main Application

```python
# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import create_db_and_tables, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle."""
    await create_db_and_tables()
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## Step 7: Protected Route Example

```python
# app/api/routes/protected.py
from fastapi import APIRouter

from app.auth.dependencies import CurrentUser, OptionalUser

router = APIRouter(prefix="/api", tags=["protected"])


@router.get("/me")
async def get_current_user_info(user: CurrentUser):
    """Get current user info (requires auth)."""
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
    }


@router.get("/public")
async def public_route(user: OptionalUser):
    """Public route with optional user info."""
    if user:
        return {"message": f"Hello, {user.name}!"}
    return {"message": "Hello, guest!"}
```

## Environment Variables

```bash
# .env
DATABASE_URL="postgresql+asyncpg://user:pass@ep-xxx.neon.tech/dbname?sslmode=require"
DIRECT_URL="postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require"
BETTER_AUTH_SECRET="your-better-auth-secret-from-nextjs"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL="http://localhost:3000"
DEBUG=true
```

## Verification

After setup, verify with:

```bash
# Start the server
uvicorn app.main:app --reload

# Test health endpoint
curl http://localhost:8000/health

# Test protected endpoint (should return 401)
curl http://localhost:8000/api/me

# Test with token
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/me
```
