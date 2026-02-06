# Initialize SQLModel with Neon DB

## Installation

```bash
pip install sqlmodel asyncpg pydantic-settings alembic
```

## Environment Variables

```bash
# .env

# Pooled connection (for app queries) - async
DATABASE_URL="postgresql+asyncpg://user:password@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require"

# Direct connection (for migrations) - sync
DIRECT_URL="postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"
```

## Configuration

```python
# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    DIRECT_URL: str | None = None

    @property
    def async_database_url(self) -> str:
        """Ensure async driver for queries."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def sync_database_url(self) -> str:
        """Sync URL for migrations."""
        url = self.DIRECT_URL or self.DATABASE_URL
        if "asyncpg" in url:
            url = url.replace("+asyncpg", "")
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url


settings = Settings()
```

## Database Setup

```python
# app/core/db.py
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.core.config import settings

# Async engine for queries
engine = create_async_engine(
    settings.async_database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=300,
)

# Session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI routes."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_db_and_tables():
    """Create tables (dev only, use migrations in prod)."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

## Models

```python
# app/models/user.py
from datetime import datetime, timezone
from typing import TYPE_CHECKING
import uuid

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.post import Post


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    name: str | None = None


class User(UserBase, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    posts: list["Post"] = Relationship(back_populates="author")


class UserCreate(SQLModel):
    email: str
    name: str | None = None


class UserResponse(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
```

```python
# app/models/post.py
from datetime import datetime, timezone
from typing import TYPE_CHECKING
import uuid

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User


class PostBase(SQLModel):
    title: str
    content: str | None = None
    published: bool = Field(default=False)


class Post(PostBase, table=True):
    __tablename__ = "posts"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    author_id: str = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    author: "User" = Relationship(back_populates="posts")


class PostCreate(SQLModel):
    title: str
    content: str | None = None
    published: bool = False


class PostResponse(PostBase):
    id: str
    author_id: str
    created_at: datetime

    class Config:
        from_attributes = True
```

## Dependencies

```python
# app/core/deps.py
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
```

## FastAPI Integration

```python
# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.db import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
```

## Router Example

```python
# app/routers/users.py
from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.core.deps import SessionDep
from app.models.user import User, UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserResponse])
async def list_users(session: SessionDep):
    result = await session.execute(select(User))
    return result.scalars().all()


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(session: SessionDep, user_in: UserCreate):
    # Check if exists
    result = await session.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User.model_validate(user_in)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(session: SessionDep, user_id: str):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## Alembic Setup

```bash
# Initialize Alembic
alembic init alembic
```

```python
# alembic/env.py
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from sqlmodel import SQLModel

# Import all models
from app.models import user, post  # noqa

from app.core.config import settings

config = context.config

# Use sync URL for migrations
config.set_main_option("sqlalchemy.url", settings.sync_database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Migration Commands

```bash
# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head

# Downgrade one step
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

## Verify Setup

```bash
# Test the connection
python -c "from app.core.config import settings; print(settings.async_database_url)"

# Create first migration
alembic revision --autogenerate -m "Initial tables"

# Apply migration
alembic upgrade head

# Run the app
uvicorn app.main:app --reload
```
