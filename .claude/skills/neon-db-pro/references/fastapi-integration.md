# FastAPI Integration with Neon

## Setup

### Installation

```bash
pip install fastapi uvicorn sqlalchemy asyncpg alembic pydantic-settings email-validator
```

### Connection String Format

```
postgresql+asyncpg://user:password@ep-xxx-pooler.region.aws.neon.tech/dbname
```

> **IMPORTANT: asyncpg SSL Handling**
>
> The `asyncpg` driver does NOT support `sslmode=require` or `channel_binding=require` as URL query parameters. These will cause:
> ```
> TypeError: connect() got an unexpected keyword argument 'sslmode'
> ```
>
> **Solution:** Pass SSL via `connect_args` instead of URL parameters.

## SSL Configuration for asyncpg

When connecting to Neon PostgreSQL with asyncpg, you MUST handle SSL separately:

```python
import ssl
from sqlalchemy.ext.asyncio import create_async_engine

def get_database_url(url: str) -> str:
    """Strip unsupported asyncpg parameters from URL."""
    if "?" in url:
        base, params = url.split("?", 1)
        param_list = params.split("&")
        # Remove sslmode and channel_binding - asyncpg doesn't support them in URL
        filtered = [p for p in param_list if not p.startswith(("sslmode=", "channel_binding="))]
        return f"{base}?{'&'.join(filtered)}" if filtered else base
    return url

def get_ssl_context():
    """Create SSL context for Neon PostgreSQL."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    return ssl_context

# Create engine with SSL via connect_args
engine = create_async_engine(
    get_database_url(settings.database_url),
    connect_args={"ssl": get_ssl_context()},
    pool_pre_ping=True,
)
```

### Alembic migrations/env.py

Apply the same SSL handling for Alembic migrations:

```python
from app.database import get_database_url, get_ssl_context

# Set cleaned URL
config.set_main_option("sqlalchemy.url", get_database_url())

async def run_async_migrations() -> None:
    ssl_context = get_ssl_context()
    connect_args = {"ssl": ssl_context} if ssl_context else {}

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,  # Pass SSL here
    )
    # ... rest of migration code
```

## Project Structure

```
app/
├── __init__.py
├── main.py
├── config.py
├── database.py
├── models/
│   ├── __init__.py
│   └── user.py
├── schemas/
│   └── user.py
├── routers/
│   └── users.py
└── repositories/
    └── user_repository.py
alembic/
├── versions/
└── env.py
alembic.ini
```

## Configuration

### config.py

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Pooled connection for app queries
    DATABASE_URL: str

    # Direct connection for migrations
    DIRECT_URL: str

    @property
    def async_database_url(self) -> str:
        """Convert to asyncpg format."""
        return self.DATABASE_URL.replace(
            "postgresql://", "postgresql+asyncpg://"
        ).replace("sslmode=require", "ssl=require")

    @property
    def sync_database_url(self) -> str:
        """Sync URL for Alembic migrations."""
        return self.DIRECT_URL.replace("sslmode=require", "sslmode=require")

settings = Settings()
```

### .env

```bash
DATABASE_URL="postgresql://user:pass@ep-xxx-pooler.region.aws.neon.tech/db?sslmode=require"
DIRECT_URL="postgresql://user:pass@ep-xxx.region.aws.neon.tech/db?sslmode=require"
```

## Database Setup

### database.py

```python
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(
    settings.async_database_url,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

## Models

### models/user.py

```python
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

## Schemas

### schemas/user.py

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = None

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
```

## Repository

### repositories/user_repository.py

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, user_in: UserCreate) -> User:
        user = User(**user_in.model_dump())
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user: User, user_in: UserUpdate) -> User:
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.flush()
```

## Router

### routers/users.py

```python
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

async def get_user_repo(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserRepository:
    return UserRepository(db)

@router.get("/", response_model=list[UserResponse])
async def list_users(
    repo: Annotated[UserRepository, Depends(get_user_repo)],
    skip: int = 0,
    limit: int = 100,
):
    return await repo.get_all(skip=skip, limit=limit)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    repo: Annotated[UserRepository, Depends(get_user_repo)],
):
    existing = await repo.get_by_email(user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await repo.create(user_in)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    repo: Annotated[UserRepository, Depends(get_user_repo)],
):
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    repo: Annotated[UserRepository, Depends(get_user_repo)],
):
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await repo.update(user, user_in)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    repo: Annotated[UserRepository, Depends(get_user_repo)],
):
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await repo.delete(user)
```

## Main Application

### main.py

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import users

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown

app = FastAPI(title="API", lifespan=lifespan)
app.include_router(users.router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

## Alembic Migrations

### alembic/env.py

```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.database import Base
from app.config import settings

config = context.config
config.set_main_option("sqlalchemy.url", settings.DIRECT_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
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

### Commands

```bash
# Create migration
alembic revision --autogenerate -m "create users table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Running

```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```
