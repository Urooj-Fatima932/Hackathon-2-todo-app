# Database Migrations

## Key Rule

**Always use DIRECT connection for migrations** (not pooled).

The pooled connection uses transaction mode, which doesn't support DDL operations properly.

## Prisma Migrations

### Setup

```prisma
// prisma/schema.prisma
datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")      // Pooled - for queries
  directUrl = env("DIRECT_URL")        // Direct - for migrations
}
```

### Commands

```bash
# Create migration (development)
npx prisma migrate dev --name add_users_table

# Apply migrations (production)
npx prisma migrate deploy

# Reset database (development only!)
npx prisma migrate reset

# Check migration status
npx prisma migrate status

# Generate client without migration
npx prisma generate
```

### Migration Files

```
prisma/
├── schema.prisma
└── migrations/
    ├── 20240101000000_init/
    │   └── migration.sql
    ├── 20240102000000_add_users/
    │   └── migration.sql
    └── migration_lock.toml
```

### CI/CD Deployment

```yaml
# GitHub Actions
- name: Deploy Migrations
  run: npx prisma migrate deploy
  env:
    DIRECT_URL: ${{ secrets.DIRECT_URL }}
```

## Drizzle Migrations

### Setup

```typescript
// drizzle.config.ts
import { defineConfig } from "drizzle-kit"

export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: {
    url: process.env.DIRECT_URL!,  // Direct connection for migrations
  },
})
```

### Commands

```bash
# Generate migration from schema changes
npx drizzle-kit generate

# Apply migrations
npx drizzle-kit migrate

# Push schema directly (no migration file - dev only)
npx drizzle-kit push

# Check current state
npx drizzle-kit check

# Open Drizzle Studio
npx drizzle-kit studio
```

### Migration Files

```
drizzle/
├── 0000_initial.sql
├── 0001_add_posts.sql
├── meta/
│   ├── 0000_snapshot.json
│   ├── 0001_snapshot.json
│   └── _journal.json
```

### Programmatic Migrations

```typescript
import { migrate } from "drizzle-orm/neon-http/migrator"
import { drizzle } from "drizzle-orm/neon-http"
import { neon } from "@neondatabase/serverless"

const sql = neon(process.env.DIRECT_URL!)
const db = drizzle(sql)

await migrate(db, { migrationsFolder: "./drizzle" })
```

## SQLAlchemy / Alembic Migrations

### Setup

```bash
# Install
pip install alembic asyncpg

# Initialize
alembic init alembic
```

### Configuration

```python
# alembic/env.py
from sqlalchemy.ext.asyncio import create_async_engine
import os

# Use DIRECT_URL for migrations
config.set_main_option("sqlalchemy.url", os.environ["DIRECT_URL"])
```

```ini
# alembic.ini
[alembic]
script_location = alembic
```

### Commands

```bash
# Create migration
alembic revision --autogenerate -m "add users table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Check current version
alembic current

# Show history
alembic history
```

## Migration Best Practices

### 1. Always Test Locally First

```bash
# Create dev branch
neonctl branches create --name migration-test

# Test migration
DATABASE_URL=<dev-branch-url> npx prisma migrate dev

# If successful, apply to production
```

### 2. Backup Before Production Migrations

Neon has automatic point-in-time recovery, but consider:

```bash
# Note the time before migration
echo "Migration starting at $(date -u)"

# Run migration
npx prisma migrate deploy

# If issues, restore to timestamp via Neon dashboard
```

### 3. Make Migrations Reversible

```sql
-- Prisma: Include down migration in comments
-- Up
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Down (manual)
-- ALTER TABLE users DROP COLUMN phone;
```

### 4. Avoid Breaking Changes

```sql
-- Bad: Dropping column immediately
ALTER TABLE users DROP COLUMN old_field;

-- Good: Deprecate first, drop later
-- Step 1: Add new column
ALTER TABLE users ADD COLUMN new_field TEXT;
-- Step 2: Migrate data (in app code)
-- Step 3: Remove old column (later migration)
```

### 5. Handle Long-Running Migrations

For large tables:

```sql
-- Add index concurrently (doesn't lock table)
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

## Rollback Strategies

### Prisma

```bash
# Prisma doesn't have built-in rollback
# Option 1: Restore from Neon point-in-time
# Option 2: Create reverse migration manually
npx prisma migrate dev --name rollback_feature_x
```

### Drizzle

```bash
# Drizzle doesn't auto-rollback
# Create reverse migration manually
# Or use Neon point-in-time restore
```

### Alembic

```bash
# Rollback specific number of migrations
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123

# Rollback all
alembic downgrade base
```

## Troubleshooting

### Migration Stuck

```bash
# Check for locks
SELECT * FROM pg_locks WHERE NOT granted;

# Kill blocking query (carefully!)
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE query LIKE '%migration%';
```

### Migration Failed Midway

1. Check Neon dashboard for point-in-time restore
2. Restore to before migration
3. Fix migration script
4. Re-run migration

### "Connection refused" During Migration

Ensure using DIRECT_URL (not DATABASE_URL with pooler).
