# Drizzle ORM with Neon

## Installation

```bash
npm install drizzle-orm @neondatabase/serverless
npm install -D drizzle-kit
```

## Configuration

### drizzle.config.ts

```typescript
import { defineConfig } from "drizzle-kit"

export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
})
```

## Schema Definition

### src/db/schema.ts

```typescript
import {
  pgTable,
  serial,
  text,
  varchar,
  boolean,
  timestamp,
  integer,
} from "drizzle-orm/pg-core"
import { relations } from "drizzle-orm"

// Users table
export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  email: varchar("email", { length: 255 }).unique().notNull(),
  name: varchar("name", { length: 255 }),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
})

// Posts table
export const posts = pgTable("posts", {
  id: serial("id").primaryKey(),
  title: varchar("title", { length: 255 }).notNull(),
  content: text("content"),
  published: boolean("published").default(false).notNull(),
  authorId: integer("author_id")
    .references(() => users.id)
    .notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
})

// Relations
export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}))

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
}))

// Type exports
export type User = typeof users.$inferSelect
export type NewUser = typeof users.$inferInsert
export type Post = typeof posts.$inferSelect
export type NewPost = typeof posts.$inferInsert
```

## Database Client

### HTTP Mode (Serverless - Recommended)

```typescript
// src/db/index.ts
import { neon } from "@neondatabase/serverless"
import { drizzle } from "drizzle-orm/neon-http"
import * as schema from "./schema"

const sql = neon(process.env.DATABASE_URL!)

export const db = drizzle(sql, { schema })
```

### WebSocket Mode (Sessions/Transactions)

```typescript
// src/db/index.ts
import { Pool, neonConfig } from "@neondatabase/serverless"
import { drizzle } from "drizzle-orm/neon-serverless"
import * as schema from "./schema"

// Enable WebSocket
neonConfig.webSocketConstructor = globalThis.WebSocket

const pool = new Pool({ connectionString: process.env.DATABASE_URL })

export const db = drizzle(pool, { schema })
```

## Migrations

```bash
# Generate migration from schema changes
npx drizzle-kit generate

# Apply migrations to database
npx drizzle-kit migrate

# Push schema directly (dev only, no migration files)
npx drizzle-kit push

# Open Drizzle Studio
npx drizzle-kit studio
```

## Query Examples

### Basic CRUD

```typescript
import { db } from "@/db"
import { users, posts } from "@/db/schema"
import { eq, desc, and } from "drizzle-orm"

// Create
const [newUser] = await db
  .insert(users)
  .values({
    email: "user@example.com",
    name: "John Doe",
  })
  .returning()

// Read all
const allUsers = await db.select().from(users)

// Read with filter
const user = await db
  .select()
  .from(users)
  .where(eq(users.email, "user@example.com"))
  .limit(1)

// Update
const [updated] = await db
  .update(users)
  .set({ name: "Jane Doe" })
  .where(eq(users.id, 1))
  .returning()

// Delete
await db.delete(users).where(eq(users.id, 1))
```

### With Relations

```typescript
// Query with relations
const usersWithPosts = await db.query.users.findMany({
  with: {
    posts: true,
  },
})

// Single user with posts
const userWithPosts = await db.query.users.findFirst({
  where: eq(users.id, 1),
  with: {
    posts: {
      where: eq(posts.published, true),
      orderBy: desc(posts.createdAt),
    },
  },
})
```

### Joins

```typescript
// Inner join
const postsWithAuthors = await db
  .select({
    postId: posts.id,
    postTitle: posts.title,
    authorName: users.name,
  })
  .from(posts)
  .innerJoin(users, eq(posts.authorId, users.id))
  .where(eq(posts.published, true))
```

### Pagination

```typescript
const page = 1
const pageSize = 10

const results = await db
  .select()
  .from(posts)
  .where(eq(posts.published, true))
  .orderBy(desc(posts.createdAt))
  .limit(pageSize)
  .offset((page - 1) * pageSize)

// Get total count
const [{ count }] = await db
  .select({ count: sql<number>`count(*)` })
  .from(posts)
  .where(eq(posts.published, true))
```

### Transactions

```typescript
import { db } from "@/db"

const result = await db.transaction(async (tx) => {
  const [user] = await tx
    .insert(users)
    .values({ email: "new@example.com" })
    .returning()

  const [post] = await tx
    .insert(posts)
    .values({
      title: "First Post",
      authorId: user.id,
    })
    .returning()

  return { user, post }
})
```

## Next.js Server Actions

```typescript
// app/actions.ts
"use server"

import { db } from "@/db"
import { posts } from "@/db/schema"
import { revalidatePath } from "next/cache"

export async function createPost(formData: FormData) {
  const title = formData.get("title") as string
  const content = formData.get("content") as string

  await db.insert(posts).values({
    title,
    content,
    authorId: 1,
  })

  revalidatePath("/posts")
}

export async function getPosts() {
  return db.query.posts.findMany({
    where: eq(posts.published, true),
    with: { author: true },
    orderBy: desc(posts.createdAt),
  })
}
```

## Project Structure

```
src/
├── db/
│   ├── index.ts          # Database client
│   ├── schema.ts         # Table definitions
│   └── migrations/       # Generated migrations
├── app/
│   └── actions.ts        # Server actions
drizzle/
└── *.sql                 # Migration files
drizzle.config.ts         # Drizzle configuration
```
