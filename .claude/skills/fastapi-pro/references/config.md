# FastAPI Configuration Patterns

## Pydantic Settings

```python
# app/config.py
from functools import lru_cache
from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "My API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # Database
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

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
```

## Environment-Specific Config

```python
# app/config.py
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    APP_NAME: str = "My API"
    SECRET_KEY: str
    DATABASE_URL: str

class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"

class StagingConfig(BaseConfig):
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    DOCS_URL: str = "/docs"
    REDOC_URL: str | None = None

class ProductionConfig(BaseConfig):
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    DOCS_URL: str | None = None
    REDOC_URL: str | None = None

def get_config() -> BaseConfig:
    env = os.getenv("ENVIRONMENT", "development")
    configs = {
        "development": DevelopmentConfig,
        "staging": StagingConfig,
        "production": ProductionConfig,
    }
    return configs[env]()
```

## Dependency Injection for Settings

```python
from typing import Annotated
from fastapi import Depends

def get_settings() -> Settings:
    return Settings()

SettingsDep = Annotated[Settings, Depends(get_settings)]

@router.get("/info")
async def get_info(settings: SettingsDep):
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
```

## Sample .env File

```bash
# .env
APP_NAME="My FastAPI App"
APP_VERSION="1.0.0"
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/mydb
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Logging Configuration

```python
# app/logging_config.py
import logging
import sys
from app.config import settings

def setup_logging():
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    if settings.ENVIRONMENT == "production":
        # JSON logging for production
        import json_log_formatter
        formatter = json_log_formatter.JSONFormatter()
    else:
        formatter = logging.Formatter(log_format)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    root_logger.addHandler(handler)

    # Reduce noise from libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Call in lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield
```

## App Factory with Config

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import api

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_database()
    yield
    # Shutdown
    await close_database()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url=settings.DOCS_URL if hasattr(settings, "DOCS_URL") else "/docs",
        redoc_url=settings.REDOC_URL if hasattr(settings, "REDOC_URL") else "/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(api.router, prefix="/api/v1")

    return app

app = create_app()
```

## Docker Compose with Environment

```yaml
# docker-compose.yml
services:
  api:
    build: .
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
```

## Secrets Management

```python
# For production, use secret managers
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Can be loaded from AWS Secrets Manager, HashiCorp Vault, etc.
    DATABASE_PASSWORD: str = Field(default=..., json_schema_extra={"env": "DATABASE_PASSWORD"})

    @classmethod
    def settings_customise_sources(cls, settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings):
        # Add custom secret source
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            aws_secrets_source,  # Custom source
            file_secret_settings,
        )
```
