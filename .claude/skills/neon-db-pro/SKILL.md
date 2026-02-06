---
name: neon-db-pro
description: |
  Integrates Neon serverless PostgreSQL with applications using Prisma, Drizzle,
  or SQLAlchemy. This skill should be used when users want to set up Neon DB,
  configure connection pooling, run migrations, or implement database branching
  for development workflows.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

# Neon DB Pro

Integrate Neon serverless PostgreSQL with Next.js, FastAPI, or any application.

## What This Skill Does

- Sets up Neon PostgreSQL projects and connection strings
- Configures ORMs (Prisma, Drizzle, SQLAlchemy) with Neon
- Implements connection pooling for serverless environments
- Creates database branching workflows for dev/staging
- Generates migration patterns for schema changes
- Integrates with both Next.js and FastAPI backends

## What This Skill Does NOT Do

- Manage Neon billing or project settings
- Handle database backups (Neon handles this automatically)
- Deploy applications to hosting platforms
- Create application-level auth (see fullstack-auth skill)

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing ORM setup, .env files, database schema |
| **Conversation** | User's ORM preference, Next.js or FastAPI, branching needs |
| **Skill References** | Neon patterns from `references/` |
| **User Guidelines** | Project conventions, existing migrations |

---

## Clarifications (Ask User)

Ask before generating:

1. **Which ORM?** - Prisma, Drizzle, SQLAlchemy, or raw SQL?
2. **Framework?** - Next.js (serverless), FastAPI, or both?
3. **Branching?** - Need dev/staging database branches?
4. **Existing DB?** - New project or migrating existing data?

---

## Generation Process

```
Check existing setup → Configure connection → Set up ORM → Create migrations
```

### Step 1: Check Existing Setup

```
# Find existing ORM config
Glob: **/prisma/schema.prisma, **/drizzle.config.*, **/alembic.ini

# Check environment files
Glob: **/.env*, **/.env.example

# Find existing database code
Grep: "DATABASE_URL|neon|postgres" in *.ts, *.py
```

### Step 2: Configure Based on ORM

| ORM | Configuration Files |
|-----|---------------------|
| Prisma | `prisma/schema.prisma`, `src/lib/db.ts` |
| Drizzle | `drizzle.config.ts`, `src/db/schema.ts`, `src/db/index.ts` |
| SQLAlchemy | `app/database.py`, `alembic/env.py` |

### Step 3: Environment Variables

Always configure both connection types:

```env
# Pooled connection (for app queries)
DATABASE_URL="postgresql://user:pass@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require"

# Direct connection (for migrations)
DIRECT_URL="postgresql://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"
```

---

## Connection String Format

```
postgresql://[user]:[password]@[endpoint].[region].aws.neon.tech/[dbname]?sslmode=require
```

| Type | Endpoint Format | Use Case |
|------|-----------------|----------|
| Pooled | `ep-xxx-pooler` | App queries, serverless functions |
| Direct | `ep-xxx` | Migrations, schema changes, CLI |

---

## Standards

| Standard | Implementation |
|----------|----------------|
| **Pooled connections** | Always use `-pooler` endpoint for app queries |
| **Direct for migrations** | Use direct endpoint for Prisma/Drizzle migrations |
| **SSL required** | Always include `?sslmode=require` |
| **Env vars** | Never hardcode credentials, use `.env` |
| **Connection limits** | Configure pool size for serverless |

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/setup.md` | Initial Neon project setup |
| `references/prisma.md` | Prisma ORM configuration |
| `references/drizzle.md` | Drizzle ORM configuration |
| `references/serverless-driver.md` | @neondatabase/serverless usage |
| `references/connection-pooling.md` | Pooled vs direct connections |
| `references/branching.md` | Dev/staging database branches |
| `references/migrations.md` | Schema migration patterns |
| `references/fastapi-integration.md` | SQLAlchemy async with Neon |

---

## Quick Patterns

### Prisma Setup
```prisma
datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")
  directUrl = env("DIRECT_URL")
}
```

### Drizzle Setup
```typescript
import { neon } from "@neondatabase/serverless"
import { drizzle } from "drizzle-orm/neon-http"

const sql = neon(process.env.DATABASE_URL!)
export const db = drizzle(sql)
```

### SQLAlchemy Async
```python
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "postgresql+asyncpg://user:pass@ep-xxx-pooler.region.aws.neon.tech/db"
engine = create_async_engine(DATABASE_URL, echo=False)
```

---

## Checklist

Before completing, verify:

- [ ] Both DATABASE_URL and DIRECT_URL configured
- [ ] Pooled endpoint used for app connections
- [ ] Direct endpoint used for migrations
- [ ] SSL mode enabled (`?sslmode=require`)
- [ ] Connection pool limits set for serverless
- [ ] .env.example updated with variable names
- [ ] Credentials not committed to git
