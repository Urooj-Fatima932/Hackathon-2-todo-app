# Neon Setup Guide

## Create Neon Project

1. Sign up at [neon.tech](https://neon.tech)
2. Create a new project
3. Copy connection strings from dashboard

## Connection String Formats

### Pooled Connection (for application)
```
postgresql://[user]:[password]@[endpoint]-pooler.[region].aws.neon.tech/[dbname]?sslmode=require
```

### Direct Connection (for migrations)
```
postgresql://[user]:[password]@[endpoint].[region].aws.neon.tech/[dbname]?sslmode=require
```

**Key difference**: Pooled has `-pooler` in the hostname.

## Environment Variables

### .env
```bash
# Pooled connection - use for app queries
DATABASE_URL="postgresql://user:password@ep-cool-name-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"

# Direct connection - use for migrations
DIRECT_URL="postgresql://user:password@ep-cool-name.us-east-2.aws.neon.tech/neondb?sslmode=require"

# Optional: Neon API key for branching
NEON_API_KEY="your-api-key"
```

### .env.example (commit this)
```bash
DATABASE_URL="postgresql://user:password@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require"
DIRECT_URL="postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"
NEON_API_KEY=""
```

## Connection Parameters

Add to connection string for optimization:

```
?sslmode=require&connect_timeout=15&connection_limit=10&pool_timeout=15
```

| Parameter | Purpose | Recommended |
|-----------|---------|-------------|
| `sslmode` | SSL encryption | `require` (mandatory) |
| `connect_timeout` | Connection timeout (seconds) | 15 |
| `connection_limit` | Max pool connections | 10 for serverless |
| `pool_timeout` | Wait for connection (seconds) | 15 |

## Project Structure

```
project/
├── .env                    # Local credentials (git ignored)
├── .env.example           # Template (committed)
├── prisma/
│   └── schema.prisma      # If using Prisma
├── drizzle/
│   └── schema.ts          # If using Drizzle
└── src/
    └── lib/
        └── db.ts          # Database client
```

## Neon CLI (Optional)

```bash
# Install
npm install -g neonctl

# Login
neonctl auth

# List projects
neonctl projects list

# Get connection string
neonctl connection-string --project-id your-project-id
```

## Regional Endpoints

| Region | Endpoint Suffix |
|--------|-----------------|
| US East | `.us-east-2.aws.neon.tech` |
| US West | `.us-west-2.aws.neon.tech` |
| Europe | `.eu-central-1.aws.neon.tech` |
| Asia Pacific | `.ap-southeast-1.aws.neon.tech` |

## Security Best Practices

1. **Never commit credentials** - Use `.env` and add to `.gitignore`
2. **Use environment variables** - Reference in code via `process.env`
3. **Rotate passwords** - Change periodically via Neon dashboard
4. **IP allowlist** - Configure in Neon settings for production
5. **SSL required** - Always use `?sslmode=require`

## Verifying Connection

### Node.js
```typescript
import { neon } from "@neondatabase/serverless"

const sql = neon(process.env.DATABASE_URL!)
const result = await sql`SELECT version()`
console.log(result)
```

### Python
```python
import asyncpg

async def test_connection():
    conn = await asyncpg.connect(DATABASE_URL)
    version = await conn.fetchval("SELECT version()")
    print(version)
    await conn.close()
```
