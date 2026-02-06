# Prisma with Neon

## Installation

```bash
npm install prisma @prisma/client @neondatabase/serverless @prisma/adapter-neon
npx prisma init
```

## Schema Configuration

```prisma
// prisma/schema.prisma
generator client {
  provider        = "prisma-client-js"
  previewFeatures = ["driverAdapters"]
}

datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")
  directUrl = env("DIRECT_URL")
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  posts     Post[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

model Post {
  id        Int      @id @default(autoincrement())
  title     String
  content   String?
  published Boolean  @default(false)
  authorId  Int
  author    User     @relation(fields: [authorId], references: [id])
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
```

## Database Client Setup

### For Serverless (Next.js App Router, Vercel)

```typescript
// src/lib/db.ts
import { Pool, neonConfig } from "@neondatabase/serverless"
import { PrismaNeon } from "@prisma/adapter-neon"
import { PrismaClient } from "@prisma/client"

// Enable WebSocket for serverless
neonConfig.webSocketConstructor = globalThis.WebSocket

const pool = new Pool({ connectionString: process.env.DATABASE_URL })
const adapter = new PrismaNeon(pool)

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    adapter,
    log: process.env.NODE_ENV === "development" ? ["query"] : [],
  })

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma
```

### For Standard Node.js

```typescript
// src/lib/db.ts
import { PrismaClient } from "@prisma/client"

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === "development" ? ["query"] : [],
  })

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma
```

## Environment Variables

```bash
# .env
DATABASE_URL="postgresql://user:pass@ep-xxx-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
DIRECT_URL="postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require"
```

## Migrations

```bash
# Create migration
npx prisma migrate dev --name init

# Apply to production (uses DIRECT_URL)
npx prisma migrate deploy

# Generate client
npx prisma generate

# Reset database (dev only)
npx prisma migrate reset
```

## Query Examples

### Basic CRUD

```typescript
import { prisma } from "@/lib/db"

// Create
const user = await prisma.user.create({
  data: {
    email: "user@example.com",
    name: "John Doe",
  },
})

// Read
const users = await prisma.user.findMany({
  include: { posts: true },
})

const user = await prisma.user.findUnique({
  where: { email: "user@example.com" },
})

// Update
const updated = await prisma.user.update({
  where: { id: 1 },
  data: { name: "Jane Doe" },
})

// Delete
await prisma.user.delete({
  where: { id: 1 },
})
```

### With Relations

```typescript
// Create with relation
const userWithPost = await prisma.user.create({
  data: {
    email: "author@example.com",
    name: "Author",
    posts: {
      create: {
        title: "First Post",
        content: "Hello world",
      },
    },
  },
  include: { posts: true },
})

// Query with relation
const postsWithAuthor = await prisma.post.findMany({
  where: { published: true },
  include: { author: true },
  orderBy: { createdAt: "desc" },
})
```

### Pagination

```typescript
const page = 1
const pageSize = 10

const [posts, total] = await Promise.all([
  prisma.post.findMany({
    skip: (page - 1) * pageSize,
    take: pageSize,
    orderBy: { createdAt: "desc" },
  }),
  prisma.post.count(),
])
```

### Transactions

```typescript
const result = await prisma.$transaction(async (tx) => {
  const user = await tx.user.create({
    data: { email: "new@example.com" },
  })

  const post = await tx.post.create({
    data: {
      title: "New Post",
      authorId: user.id,
    },
  })

  return { user, post }
})
```

## Next.js Server Actions

```typescript
// app/actions.ts
"use server"

import { prisma } from "@/lib/db"
import { revalidatePath } from "next/cache"

export async function createPost(formData: FormData) {
  const title = formData.get("title") as string
  const content = formData.get("content") as string

  await prisma.post.create({
    data: { title, content, authorId: 1 },
  })

  revalidatePath("/posts")
}
```

## Connection Pool Settings

For high-traffic serverless apps, add to DATABASE_URL:

```
?sslmode=require&connection_limit=10&pool_timeout=15
```

| Setting | Serverless | Traditional |
|---------|------------|-------------|
| `connection_limit` | 5-10 | 20-50 |
| `pool_timeout` | 15 | 30 |
