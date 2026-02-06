#!/usr/bin/env python3
"""
Initialize a new FastAPI project with production-ready structure.

Usage:
    python init_project.py <project_name> [--async] [--auth] [--postgres]
"""

import argparse
import os
from pathlib import Path

PROJECT_STRUCTURE = {
    "app": {
        "__init__.py": "",
        "main.py": None,  # Template
        "config.py": None,  # Template
        "database.py": None,  # Template
        "dependencies.py": None,  # Template
        "routers": {
            "__init__.py": "",
            "api.py": None,  # Template
        },
        "models": {
            "__init__.py": "",
        },
        "schemas": {
            "__init__.py": "",
        },
        "services": {
            "__init__.py": "",
        },
        "repositories": {
            "__init__.py": "",
        },
    },
    "tests": {
        "__init__.py": "",
        "conftest.py": None,  # Template
    },
    "alembic": {},
}

TEMPLATES = {
    "main.py": '''"""FastAPI application factory."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import api

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api.router, prefix="/api/v1")

    return app

app = create_app()
''',

    "config.py": '''"""Application configuration."""
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "FastAPI App"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
''',

    "database.py": '''"""Database configuration."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
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
''',

    "dependencies.py": '''"""Common dependencies."""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

DbDep = Annotated[AsyncSession, Depends(get_db)]
''',

    "api.py": '''"""API router aggregator."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}
''',

    "conftest.py": '''"""Test configuration."""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from app.database import get_db, Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
''',
}

REQUIREMENTS = """# Core
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
pydantic>=2.6.0
pydantic-settings>=2.1.0

# Database
sqlalchemy>=2.0.0
aiosqlite>=0.19.0
# asyncpg>=0.29.0  # Uncomment for PostgreSQL
# alembic>=1.13.0  # Uncomment for migrations

# Security
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
httpx>=0.27.0
"""

ENV_TEMPLATE = """# Application
APP_NAME="FastAPI App"
APP_VERSION="1.0.0"
DEBUG=true
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite+aiosqlite:///./app.db

# Security
SECRET_KEY=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000
"""


def create_structure(base_path: Path, structure: dict):
    for name, content in structure.items():
        path = base_path / name
        if isinstance(content, dict):
            path.mkdir(parents=True, exist_ok=True)
            create_structure(path, content)
        elif content is None:
            # Use template
            template_content = TEMPLATES.get(name, "")
            path.write_text(template_content)
        else:
            path.write_text(content)


def main():
    parser = argparse.ArgumentParser(description="Initialize FastAPI project")
    parser.add_argument("project_name", help="Name of the project")
    parser.add_argument("--async", dest="use_async", action="store_true", default=True)
    parser.add_argument("--auth", action="store_true", help="Include auth module")
    parser.add_argument("--postgres", action="store_true", help="Use PostgreSQL")
    args = parser.parse_args()

    project_path = Path(args.project_name)
    if project_path.exists():
        print(f"Error: {project_path} already exists")
        return 1

    print(f"Creating FastAPI project: {args.project_name}")

    # Create structure
    project_path.mkdir()
    create_structure(project_path, PROJECT_STRUCTURE)

    # Create requirements.txt
    (project_path / "requirements.txt").write_text(REQUIREMENTS)

    # Create .env.example
    (project_path / ".env.example").write_text(ENV_TEMPLATE)

    # Create .gitignore
    gitignore = """__pycache__/
*.py[cod]
.env
*.db
.pytest_cache/
.coverage
htmlcov/
dist/
*.egg-info/
.venv/
venv/
"""
    (project_path / ".gitignore").write_text(gitignore)

    print(f"""
Project created successfully!

Next steps:
  cd {args.project_name}
  python -m venv .venv
  source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
  pip install -r requirements.txt
  cp .env.example .env
  uvicorn app.main:app --reload

Documentation: http://localhost:8000/docs
""")
    return 0


if __name__ == "__main__":
    exit(main())
