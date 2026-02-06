# Initialize Prisma with Neon DB

## Installation

```bash
npm install prisma @prisma/client
npx prisma init
```

## Environment Variables

```bash
# .env

# Pooled connection (for queries) - use -pooler endpoint
DATABASE_URL="postgresql://user:password@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require"

# Direct connection (for migrations) - without -pooler
DIRECT_URL="postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"
```

## Prisma Schema

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")
  directUrl = env("DIRECT_URL")
}

// Example models
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  posts     Post[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

model Post {
  id        String   @id @default(cuid())
  title     String
  content   String?
  published Boolean  @default(false)
  author    User     @relation(fields: [authorId], references: [id])
  authorId  String
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
```

## Prisma Client

### For Next.js (Singleton Pattern)

```typescript
// lib/db.ts
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

### Usage in Server Components

```typescript
// app/users/page.tsx
import { prisma } from "@/lib/db"

export default async function UsersPage() {
  const users = await prisma.user.findMany()

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  )
}
```

### Usage in Server Actions

```typescript
// actions/users.ts
"use server"

import { prisma } from "@/lib/db"
import { revalidatePath } from "next/cache"

export async function createUser(formData: FormData) {
  const name = formData.get("name") as string
  const email = formData.get("email") as string

  await prisma.user.create({
    data: { name, email },
  })

  revalidatePath("/users")
}
```

## Migration Commands

```bash
# Create migration from schema changes
npx prisma migrate dev --name init

# Apply migrations in production
npx prisma migrate deploy

# Generate Prisma Client
npx prisma generate

# View database in browser
npx prisma studio

# Reset database (dev only)
npx prisma migrate reset
```

## Common Queries

```typescript
// Find many with relations
const users = await prisma.user.findMany({
  include: { posts: true },
})

// Find one
const user = await prisma.user.findUnique({
  where: { email: "user@example.com" },
})

// Create
const user = await prisma.user.create({
  data: { name: "John", email: "john@example.com" },
})

// Update
const user = await prisma.user.update({
  where: { id: "123" },
  data: { name: "Jane" },
})

// Delete
await prisma.user.delete({
  where: { id: "123" },
})

// Transaction
const [user, post] = await prisma.$transaction([
  prisma.user.create({ data: { name: "John", email: "john@example.com" } }),
  prisma.post.create({ data: { title: "Hello", authorId: "123" } }),
])
```

## Neon-Specific Tips

1. **Always use connection pooling** for serverless
2. **Use `directUrl`** for migrations to avoid timeouts
3. **Enable query logging** in development for debugging
4. **Connection limit**: Neon free tier has limited connections, pooling helps

## Verify Setup

```bash
# Test connection
npx prisma db pull

# Run first migration
npx prisma migrate dev --name init

# Open Prisma Studio
npx prisma studio
```
