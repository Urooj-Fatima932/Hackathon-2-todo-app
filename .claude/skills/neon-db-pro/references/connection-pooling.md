# Connection Pooling with Neon

## Overview

Neon uses PgBouncer for connection pooling, enabling up to 10,000 concurrent connections. This is essential for serverless environments where many short-lived connections are created.

## Pooled vs Direct Connections

### Pooled Connection
- Hostname: `ep-xxx-pooler.region.aws.neon.tech`
- Use for: Application queries, serverless functions
- Mode: Transaction pooling (connection released after each transaction)

### Direct Connection
- Hostname: `ep-xxx.region.aws.neon.tech`
- Use for: Migrations, schema changes, `pg_dump`, `LISTEN/NOTIFY`
- Mode: Direct Postgres connection

## When to Use Each

| Task | Connection Type |
|------|-----------------|
| App queries | Pooled |
| Serverless functions | Pooled |
| Prisma queries | Pooled |
| Drizzle queries | Pooled |
| Prisma migrations | Direct |
| Drizzle migrations | Direct |
| Alembic migrations | Direct |
| `pg_dump` / `pg_restore` | Direct |
| `LISTEN` / `NOTIFY` | Direct |
| Temporary tables | Direct |
| `SET` statements | Direct |

## Configuration

### Environment Variables

```bash
# .env
DATABASE_URL="postgresql://user:pass@ep-xxx-pooler.region.aws.neon.tech/db?sslmode=require"
DIRECT_URL="postgresql://user:pass@ep-xxx.region.aws.neon.tech/db?sslmode=require"
```

### Prisma

```prisma
datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")      // Pooled
  directUrl = env("DIRECT_URL")        // Direct for migrations
}
```

### Drizzle

```typescript
// drizzle.config.ts - uses direct for migrations
export default defineConfig({
  dbCredentials: {
    url: process.env.DIRECT_URL!,  // Direct connection
  },
})

// src/db/index.ts - uses pooled for queries
const sql = neon(process.env.DATABASE_URL!)  // Pooled connection
```

## Pool Configuration Parameters

Add to connection string:

```
?sslmode=require&connection_limit=10&pool_timeout=15
```

| Parameter | Description | Default | Serverless |
|-----------|-------------|---------|------------|
| `connection_limit` | Max connections | 10 | 5-10 |
| `pool_timeout` | Wait time (seconds) | 10 | 15 |
| `connect_timeout` | Connection timeout | 10 | 15 |

## Neon PgBouncer Settings

Neon's PgBouncer is pre-configured:

| Setting | Value |
|---------|-------|
| `pool_mode` | transaction |
| `max_client_conn` | 10,000 |
| `query_wait_timeout` | 120s |

## Serverless Function Best Practices

### Vercel / Next.js

```typescript
// Use HTTP mode for serverless
import { neon } from "@neondatabase/serverless"

const sql = neon(process.env.DATABASE_URL!)

export async function GET() {
  // Each request creates new HTTP connection
  // Connection automatically closed after query
  const users = await sql`SELECT * FROM users`
  return Response.json(users)
}
```

### AWS Lambda

```typescript
import { Pool, neonConfig } from "@neondatabase/serverless"

// Configure outside handler for connection reuse
neonConfig.webSocketConstructor = globalThis.WebSocket
const pool = new Pool({ connectionString: process.env.DATABASE_URL })

export async function handler(event) {
  // Reuse pool across invocations
  const { rows } = await pool.query("SELECT * FROM users")
  return { statusCode: 200, body: JSON.stringify(rows) }
}
```

## Limitations with Pooled Connections

Transaction mode pooling doesn't support:

| Feature | Workaround |
|---------|------------|
| `SET` statements | Use per-query settings |
| `LISTEN`/`NOTIFY` | Use direct connection |
| Temporary tables | Use CTEs or permanent tables |
| Session advisory locks | Use transaction-level locks |
| `PREPARE` (SQL-level) | Use client-side prepared statements |

## Monitoring Connections

### Check Current Connections

```sql
SELECT count(*) FROM pg_stat_activity;
```

### Check Pool Status (via Neon Dashboard)

The Neon dashboard shows:
- Active connections
- Pooled connections
- Connection history

## Troubleshooting

### "Too many connections"

1. Ensure using pooled endpoint (`-pooler`)
2. Reduce `connection_limit` in connection string
3. Check for connection leaks (always close/release)

### Slow connections

1. Use HTTP mode for serverless
2. Enable WebSocket for interactive transactions
3. Check regional endpoint (use closest region)

### Migration failures

1. Ensure using direct URL (not pooled)
2. Check `DIRECT_URL` environment variable
3. Verify network access to direct endpoint
