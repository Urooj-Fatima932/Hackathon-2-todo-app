# Initialize Drizzle with Neon DB

## Installation

```bash
npm install drizzle-orm @neondatabase/serverless
npm install -D drizzle-kit
```

## Environment Variables

```bash
# .env

# Pooled connection (for queries)
DATABASE_URL="postgresql://user:password@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require"

# Direct connection (for migrations)
DIRECT_URL="postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"
```

## Drizzle Config

```typescript
// drizzle.config.ts
import { defineConfig } from "drizzle-kit"

export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: {
    url: process.env.DIRECT_URL!, // Use direct URL for migrations
  },
})
```

## Database Schema

```typescript
// src/db/schema.ts
import {
  pgTable,
  text,
  timestamp,
  boolean,
  serial,
} from "drizzle-orm/pg-core"

export const users = pgTable("users", {
  id: text("id").primaryKey().$defaultFn(() => crypto.randomUUID()),
  email: text("email").unique().notNull(),
  name: text("name"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
})

export const posts = pgTable("posts", {
  id: text("id").primaryKey().$defaultFn(() => crypto.randomUUID()),
  title: text("title").notNull(),
  content: text("content"),
  published: boolean("published").default(false).notNull(),
  authorId: text("author_id").references(() => users.id).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
})

// Type exports
export type User = typeof users.$inferSelect
export type NewUser = typeof users.$inferInsert
export type Post = typeof posts.$inferSelect
export type NewPost = typeof posts.$inferInsert
```

## Database Client

### For Next.js (Serverless)

```typescript
// src/db/index.ts
import { neon } from "@neondatabase/serverless"
import { drizzle } from "drizzle-orm/neon-http"
import * as schema from "./schema"

const sql = neon(process.env.DATABASE_URL!)

export const db = drizzle(sql, { schema })
```

### For Node.js (Connection Pool)

```typescript
// src/db/index.ts
import { Pool } from "@neondatabase/serverless"
import { drizzle } from "drizzle-orm/neon-serverless"
import * as schema from "./schema"

const pool = new Pool({ connectionString: process.env.DATABASE_URL })

export const db = drizzle(pool, { schema })
```

## Usage in Server Components

```typescript
// app/users/page.tsx
import { db } from "@/db"
import { users } from "@/db/schema"

export default async function UsersPage() {
  const allUsers = await db.select().from(users)

  return (
    <ul>
      {allUsers.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  )
}
```

## Usage in Server Actions

```typescript
// actions/users.ts
"use server"

import { db } from "@/db"
import { users } from "@/db/schema"
import { eq } from "drizzle-orm"
import { revalidatePath } from "next/cache"

export async function createUser(formData: FormData) {
  const name = formData.get("name") as string
  const email = formData.get("email") as string

  await db.insert(users).values({ name, email })

  revalidatePath("/users")
}

export async function deleteUser(id: string) {
  await db.delete(users).where(eq(users.id, id))
  revalidatePath("/users")
}
```

## Migration Commands

```bash
# Generate migration from schema
npx drizzle-kit generate

# Apply migrations
npx drizzle-kit migrate

# Push schema directly (dev only, no migration files)
npx drizzle-kit push

# Open Drizzle Studio
npx drizzle-kit studio
```

## Common Queries

```typescript
import { db } from "@/db"
import { users, posts } from "@/db/schema"
import { eq, and, or, like, desc, asc } from "drizzle-orm"

// Select all
const allUsers = await db.select().from(users)

// Select with where
const user = await db
  .select()
  .from(users)
  .where(eq(users.email, "user@example.com"))
  .limit(1)

// Select with join
const usersWithPosts = await db
  .select()
  .from(users)
  .leftJoin(posts, eq(users.id, posts.authorId))

// Insert
const newUser = await db
  .insert(users)
  .values({ name: "John", email: "john@example.com" })
  .returning()

// Update
await db
  .update(users)
  .set({ name: "Jane" })
  .where(eq(users.id, "123"))

// Delete
await db.delete(users).where(eq(users.id, "123"))

// Order and limit
const recentPosts = await db
  .select()
  .from(posts)
  .orderBy(desc(posts.createdAt))
  .limit(10)

// Like query
const searchUsers = await db
  .select()
  .from(users)
  .where(like(users.name, "%john%"))

// Transaction
const result = await db.transaction(async (tx) => {
  const [user] = await tx
    .insert(users)
    .values({ name: "John", email: "john@example.com" })
    .returning()

  await tx
    .insert(posts)
    .values({ title: "First Post", authorId: user.id })

  return user
})
```

## Relations (Optional)

```typescript
// src/db/schema.ts
import { relations } from "drizzle-orm"

export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}))

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
}))

// Query with relations
const usersWithPosts = await db.query.users.findMany({
  with: { posts: true },
})
```

## Verify Setup

```bash
# Generate initial migration
npx drizzle-kit generate

# Apply to database
npx drizzle-kit migrate

# Open Studio to verify
npx drizzle-kit studio
```
