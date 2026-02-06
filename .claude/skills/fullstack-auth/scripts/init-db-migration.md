# Database Migration Setup

## Overview

This script sets up database migrations for the fullstack auth system. Supports both Better Auth auto-migration and manual Alembic migrations for FastAPI.

## Option 1: Better Auth Auto-Migration (Recommended for Development)

Better Auth can automatically create and migrate tables.

### Next.js Setup

```bash
# Install Better Auth CLI
npm install better-auth

# Run migration
npx better-auth migrate
```

### Configuration

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"
import { Pool } from "@neondatabase/serverless"

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),
  // Tables are auto-created on first run
})
```

## Option 2: Alembic Migrations (Production)

For production FastAPI apps, use Alembic for controlled migrations.

### Installation

```bash
pip install alembic
```

### Initialize Alembic

```bash
alembic init alembic
```

### Configure Alembic

```python
# alembic/env.py
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# Import all models to register them
from app.models.user import User
from app.models.session import Session
from app.models.account import Account
from app.models.verification import Verification

from app.core.config import settings

config = context.config

# Set database URL from settings
config.set_main_option("sqlalchemy.url", settings.sync_database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Update alembic.ini

```ini
# alembic.ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

# Use env variable for database URL
sqlalchemy.url = driver://user:pass@localhost/dbname
```

### Create Initial Migration

```bash
# Generate migration from models
alembic revision --autogenerate -m "Initial auth tables"

# Review the generated migration in alembic/versions/

# Apply migration
alembic upgrade head
```

## Option 3: Raw SQL Migration

For simple setups or direct database access.

### auth_tables.sql

```sql
-- Users table (Better Auth compatible)
CREATE TABLE IF NOT EXISTS "user" (
    "id" TEXT PRIMARY KEY,
    "name" TEXT,
    "email" TEXT UNIQUE NOT NULL,
    "emailVerified" BOOLEAN DEFAULT FALSE,
    "image" TEXT,
    "hashedPassword" TEXT,
    "role" TEXT DEFAULT 'user',
    "isActive" BOOLEAN DEFAULT TRUE,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions table
CREATE TABLE IF NOT EXISTS "session" (
    "id" TEXT PRIMARY KEY,
    "userId" TEXT NOT NULL REFERENCES "user"("id") ON DELETE CASCADE,
    "token" TEXT UNIQUE NOT NULL,
    "expiresAt" TIMESTAMP NOT NULL,
    "ipAddress" TEXT,
    "userAgent" TEXT,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accounts table (OAuth providers)
CREATE TABLE IF NOT EXISTS "account" (
    "id" TEXT PRIMARY KEY,
    "userId" TEXT NOT NULL REFERENCES "user"("id") ON DELETE CASCADE,
    "accountId" TEXT NOT NULL,
    "providerId" TEXT NOT NULL,
    "accessToken" TEXT,
    "refreshToken" TEXT,
    "accessTokenExpiresAt" TIMESTAMP,
    "refreshTokenExpiresAt" TIMESTAMP,
    "scope" TEXT,
    "idToken" TEXT,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE("providerId", "accountId")
);

-- Verification tokens table
CREATE TABLE IF NOT EXISTS "verification" (
    "id" TEXT PRIMARY KEY,
    "identifier" TEXT NOT NULL,
    "value" TEXT NOT NULL,
    "expiresAt" TIMESTAMP NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS "idx_user_email" ON "user"("email");
CREATE INDEX IF NOT EXISTS "idx_session_token" ON "session"("token");
CREATE INDEX IF NOT EXISTS "idx_session_userId" ON "session"("userId");
CREATE INDEX IF NOT EXISTS "idx_account_userId" ON "account"("userId");
CREATE INDEX IF NOT EXISTS "idx_account_provider" ON "account"("providerId");
CREATE INDEX IF NOT EXISTS "idx_verification_identifier" ON "verification"("identifier");
```

### Run SQL Migration

```bash
# Using psql
psql $DATABASE_URL -f auth_tables.sql

# Using Neon console
# Copy and paste the SQL into the Neon SQL Editor
```

## Migration Scripts

### Python Migration Helper

```python
# scripts/migrate.py
import asyncio
import sys

from sqlalchemy import text
from sqlmodel import SQLModel

from app.core.db import engine
from app.models.user import User
from app.models.session import Session
from app.models.account import Account
from app.models.verification import Verification


async def create_tables():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("Tables created successfully")


async def drop_tables():
    """Drop all tables (DANGEROUS!)."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    print("Tables dropped")


async def check_tables():
    """Check if tables exist."""
    async with engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
        )
        tables = [row[0] for row in result]
        print(f"Existing tables: {tables}")

        required = ["user", "session", "account", "verification"]
        missing = [t for t in required if t not in tables]

        if missing:
            print(f"Missing tables: {missing}")
            return False

        print("All required tables exist")
        return True


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "check"

    if command == "create":
        asyncio.run(create_tables())
    elif command == "drop":
        confirm = input("This will DROP all tables. Type 'yes' to confirm: ")
        if confirm == "yes":
            asyncio.run(drop_tables())
    elif command == "check":
        asyncio.run(check_tables())
    else:
        print(f"Unknown command: {command}")
        print("Usage: python scripts/migrate.py [create|drop|check]")
```

### Usage

```bash
# Check table status
python scripts/migrate.py check

# Create tables
python scripts/migrate.py create

# Drop tables (requires confirmation)
python scripts/migrate.py drop
```

## Neon-Specific Notes

### Connection Pooling

```bash
# Pooled connection (for app queries)
DATABASE_URL="postgresql://user:pass@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require"

# Direct connection (for migrations - bypasses pooler)
DIRECT_URL="postgresql://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"
```

### Branching for Development

```bash
# Create a development branch in Neon console
# Use the branch's connection string for development
# Merge changes to main branch when ready
```

## Rollback Strategy

### Alembic Rollback

```bash
# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# Rollback all
alembic downgrade base
```

### Manual Rollback

Keep rollback SQL scripts versioned:

```sql
-- rollback_001_auth_tables.sql
DROP TABLE IF EXISTS "verification";
DROP TABLE IF EXISTS "account";
DROP TABLE IF EXISTS "session";
DROP TABLE IF EXISTS "user";
```

## Checklist

- [ ] Choose migration strategy (auto/alembic/raw SQL)
- [ ] Set DATABASE_URL and DIRECT_URL
- [ ] Run initial migration
- [ ] Verify tables exist
- [ ] Test auth flow end-to-end
- [ ] Set up rollback procedure
