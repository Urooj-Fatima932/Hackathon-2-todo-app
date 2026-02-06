# Neon Serverless Driver

## Installation

```bash
npm install @neondatabase/serverless
```

## HTTP Queries (Recommended for Serverless)

Best for one-shot queries in serverless functions.

### Basic Usage

```typescript
import { neon } from "@neondatabase/serverless"

const sql = neon(process.env.DATABASE_URL!)

// Simple query
const users = await sql`SELECT * FROM users`

// With parameters (SQL injection safe)
const userId = 1
const user = await sql`SELECT * FROM users WHERE id = ${userId}`

// Multiple parameters
const email = "user@example.com"
const name = "John"
const result = await sql`
  INSERT INTO users (email, name)
  VALUES (${email}, ${name})
  RETURNING *
`
```

### Array Mode

```typescript
const sql = neon(process.env.DATABASE_URL!, { arrayMode: true })

// Returns arrays instead of objects
const rows = await sql`SELECT id, name FROM users`
// [[1, "John"], [2, "Jane"]]
```

### Full Results

```typescript
const sql = neon(process.env.DATABASE_URL!, { fullResults: true })

const result = await sql`SELECT * FROM users`
// {
//   rows: [...],
//   fields: [...],
//   rowCount: 10,
//   command: "SELECT"
// }
```

### Transactions (HTTP)

```typescript
import { neon } from "@neondatabase/serverless"

const sql = neon(process.env.DATABASE_URL!)

// Transaction with HTTP (non-interactive)
const results = await sql.transaction([
  sql`INSERT INTO users (email) VALUES ('user1@example.com')`,
  sql`INSERT INTO users (email) VALUES ('user2@example.com')`,
])
```

## WebSocket Connections

Use for interactive transactions and session support.

### Pool Connection

```typescript
import { Pool, neonConfig } from "@neondatabase/serverless"

// Enable WebSocket (required in serverless environments)
neonConfig.webSocketConstructor = globalThis.WebSocket

const pool = new Pool({ connectionString: process.env.DATABASE_URL })

// Query
const { rows } = await pool.query("SELECT * FROM users WHERE id = $1", [1])

// Don't forget to release
const client = await pool.connect()
try {
  await client.query("SELECT * FROM users")
} finally {
  client.release()
}
```

### Client Connection

```typescript
import { Client, neonConfig } from "@neondatabase/serverless"

neonConfig.webSocketConstructor = globalThis.WebSocket

const client = new Client({ connectionString: process.env.DATABASE_URL })
await client.connect()

const { rows } = await client.query("SELECT * FROM users")

await client.end()
```

### Interactive Transactions (WebSocket)

```typescript
import { Pool, neonConfig } from "@neondatabase/serverless"

neonConfig.webSocketConstructor = globalThis.WebSocket

const pool = new Pool({ connectionString: process.env.DATABASE_URL })

const client = await pool.connect()
try {
  await client.query("BEGIN")

  const { rows: [user] } = await client.query(
    "INSERT INTO users (email) VALUES ($1) RETURNING *",
    ["user@example.com"]
  )

  await client.query(
    "INSERT INTO posts (title, author_id) VALUES ($1, $2)",
    ["First Post", user.id]
  )

  await client.query("COMMIT")
} catch (error) {
  await client.query("ROLLBACK")
  throw error
} finally {
  client.release()
}
```

## Choosing Connection Method

| Method | Use Case |
|--------|----------|
| **HTTP (`neon()`)** | Single queries, serverless functions, Vercel Edge |
| **WebSocket (Pool)** | Interactive transactions, session features |
| **WebSocket (Client)** | Long-running connections, LISTEN/NOTIFY |

## Next.js App Router

### Route Handler

```typescript
// app/api/users/route.ts
import { neon } from "@neondatabase/serverless"

const sql = neon(process.env.DATABASE_URL!)

export async function GET() {
  const users = await sql`SELECT * FROM users`
  return Response.json(users)
}

export async function POST(request: Request) {
  const { email, name } = await request.json()

  const [user] = await sql`
    INSERT INTO users (email, name)
    VALUES (${email}, ${name})
    RETURNING *
  `

  return Response.json(user, { status: 201 })
}
```

### Server Component

```typescript
// app/users/page.tsx
import { neon } from "@neondatabase/serverless"

const sql = neon(process.env.DATABASE_URL!)

export default async function UsersPage() {
  const users = await sql`SELECT * FROM users ORDER BY created_at DESC`

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  )
}
```

### Server Action

```typescript
// app/actions.ts
"use server"

import { neon } from "@neondatabase/serverless"
import { revalidatePath } from "next/cache"

const sql = neon(process.env.DATABASE_URL!)

export async function createUser(formData: FormData) {
  const email = formData.get("email") as string
  const name = formData.get("name") as string

  await sql`
    INSERT INTO users (email, name)
    VALUES (${email}, ${name})
  `

  revalidatePath("/users")
}
```

## Edge Runtime

The serverless driver works in Edge Runtime:

```typescript
// app/api/edge/route.ts
import { neon } from "@neondatabase/serverless"

export const runtime = "edge"

export async function GET() {
  const sql = neon(process.env.DATABASE_URL!)
  const result = await sql`SELECT NOW()`
  return Response.json(result)
}
```

## Error Handling

```typescript
import { neon, NeonDbError } from "@neondatabase/serverless"

const sql = neon(process.env.DATABASE_URL!)

try {
  await sql`INSERT INTO users (email) VALUES (${email})`
} catch (error) {
  if (error instanceof NeonDbError) {
    if (error.code === "23505") {
      // Unique violation
      throw new Error("Email already exists")
    }
  }
  throw error
}
```

## Common Error Codes

| Code | Meaning |
|------|---------|
| `23505` | Unique violation |
| `23503` | Foreign key violation |
| `23502` | Not null violation |
| `42P01` | Table doesn't exist |
| `42703` | Column doesn't exist |
