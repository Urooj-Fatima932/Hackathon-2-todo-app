---
name: nextjs-pro
description: |
  Generates Next.js App Router projects with server components, server actions, and data fetching patterns.
  This skill should be used when users want to create Next.js projects, set up routing, implement
  server actions, configure data fetching, or integrate with FastAPI backends. Works with nextjs-ui-pro
  for components, fullstack-auth for authentication, and neon-db-pro for database integration.

  ENHANCED: Automatically prevents route group conflicts with root page.tsx and ensures 'use client'
  directives on interactive components to avoid common App Router pitfalls.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash, Skill
---

# Next.js Pro

Generate production-grade Next.js App Router projects with server components, server actions, and type-safe patterns.

## What This Skill Does

- Creates Next.js 14/15 App Router project structure
- Implements server components and client components patterns
- Sets up server actions for mutations and form handling
- Configures data fetching with caching and revalidation
- Integrates react-hook-form + zod for type-safe forms
- Creates API client for FastAPI backend integration
- Sets up middleware, error handling, and loading states
- **Prevents route group conflicts** (no root page.tsx with route groups)
- **Ensures 'use client' on interactive components** (prevents event handler errors)

## What This Skill Does NOT Do

- Create UI components (use `nextjs-ui-pro`)
- Set up authentication (use `fullstack-auth`)
- Configure database connections (use `neon-db-pro`)
- Deploy applications

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing Next.js setup, app/ structure, existing patterns |
| **Conversation** | User's requirements, routes needed, data sources |
| **Skill References** | Patterns from `references/` |
| **Related Skills** | `nextjs-ui-pro`, `fullstack-auth`, `fastapi-pro` |

---

## Critical App Router Issue Prevention

### Issue 1: Route Group Conflicts with Root page.tsx

**Problem**: Having both `/app/page.tsx` AND `/app/(group)/page.tsx` causes the root page.tsx to take precedence, breaking route groups.

**Prevention Rules**:
1. **NEVER create `/app/page.tsx` when using route groups for top-level pages**
2. Route groups `(name)` don't affect URLs - `(public)/page.tsx` serves at `/`
3. Only use root page.tsx if NOT using route groups at the same level

**Auto-Check Before Generation**:
```typescript
// When generating with route groups like (public), (marketing), (admin):
const hasRouteGroupAtRoot = routeGroups.some(g => g.level === 'root')
const willCreateRootPage = files.includes('app/page.tsx')

if (hasRouteGroupAtRoot && willCreateRootPage) {
  // ❌ CONFLICT! Remove root page.tsx
  files = files.filter(f => f !== 'app/page.tsx')
}
```

**Correct Structure**:
```
✅ WITH ROUTE GROUPS:
app/
├── layout.tsx
├── (public)/
│   ├── layout.tsx
│   ├── page.tsx         # Serves at /
│   └── about/page.tsx   # Serves at /about
└── admin/
    └── page.tsx         # Serves at /admin

❌ WRONG (creates conflict):
app/
├── layout.tsx
├── page.tsx             # ❌ Takes precedence, breaks (public)
└── (public)/
    └── page.tsx         # ❌ Never reached
```

### Issue 2: Missing 'use client' on Interactive Components

**Problem**: Components with event handlers (onClick, onChange), hooks (useState, useEffect), or browser APIs need 'use client'. Without it, Next.js throws "Event handlers cannot be passed to Client Component props" errors.

**Prevention Rules**:
1. **ALL components with these features MUST have 'use client' at line 1**:
   - Event handlers: `onClick`, `onChange`, `onSubmit`, `onFocus`, etc.
   - React hooks: `useState`, `useEffect`, `useContext`, `useRef`, etc.
   - Browser APIs: `window`, `document`, `localStorage`, `navigator`, etc.
   - Third-party interactive libraries: Framer Motion, React Hook Form, etc.

2. **Common components that ALWAYS need 'use client'**:
   - **shadcn/ui**: Button, Input, Textarea, Select, Dialog, Sheet, Popover, Dropdown Menu, Tabs, Accordion, Toast, Form components
   - **Layouts with state**: Navbar with mobile menu, Sidebar with collapse state
   - **Any component receiving callbacks**: onClick, onChange handlers from parent

**Auto-Check Function**:
```typescript
function needsClientDirective(code: string): boolean {
  const patterns = [
    /\b(onClick|onChange|onSubmit|onFocus|onBlur|onKeyDown|onKeyPress)\w*\s*=/,
    /\buse(State|Effect|Context|Ref|Reducer|Callback|Memo)\b/,
    /\b(window|document|localStorage|sessionStorage|navigator)\./,
    /from ['"]framer-motion['"]/,
    /from ['"]react-hook-form['"]/,
    /from ['"]@radix-ui/,  // Most Radix UI components need client
  ]
  return patterns.some(p => p.test(code))
}

// Apply before writing component:
if (needsClientDirective(componentCode) && !componentCode.startsWith("'use client'")) {
  componentCode = `'use client'\n\n${componentCode}`
}
```

**Implementation Pattern**:
```typescript
// ✅ CORRECT: Interactive component
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'

export function Counter() {
  const [count, setCount] = useState(0)
  return <Button onClick={() => setCount(count + 1)}>Count: {count}</Button>
}

// ✅ CORRECT: Server component (default, no directive)
import { db } from '@/lib/db'

export async function BlogList() {
  const posts = await db.post.findMany()
  return <div>{posts.map(p => <div key={p.id}>{p.title}</div>)}</div>
}
```

**shadcn/ui Components Reference**:

| Component | Needs 'use client'? | Reason |
|-----------|---------------------|--------|
| Button | ✅ YES | Has onClick, uses Slot |
| Input, Textarea | ✅ YES | Has onChange, onFocus |
| Select, Dropdown Menu, Popover | ✅ YES | Radix UI with state |
| Dialog, Sheet, Accordion, Tabs | ✅ YES | Manages open/collapse state |
| Form (react-hook-form) | ✅ YES | Uses hooks |
| Card, Badge, Separator, Avatar, Skeleton | ❌ NO | Purely presentational |

**Rule**: If it uses Radix UI primitives or has any interactivity → add 'use client'

---

## Clarifications (Ask User)

Ask before generating:

1. **What pages/routes?** - Main routes and nested routes needed
2. **Data sources?** - FastAPI backend, external APIs, or database direct?
3. **Authentication?** - Protected routes needed? (use fullstack-auth)
4. **Forms?** - What forms/mutations are needed?

---

## Skill Integration

| Skill | Integration Point |
|-------|-------------------|
| **nextjs-ui-pro** | UI components in `components/ui/` |
| **fullstack-auth** | Auth in `lib/auth.ts`, `lib/auth-client.ts` |
| **fastapi-pro** | API client in `lib/api/`, types in `types/` |
| **neon-db-pro** | Direct DB in server components (if needed) |

---

## Project Structure

```
├── app/
│   ├── layout.tsx                 # Root layout
│   ├── page.tsx                   # Home page
│   ├── loading.tsx                # Global loading
│   ├── error.tsx                  # Global error boundary
│   ├── not-found.tsx              # 404 page
│   ├── (auth)/                    # Auth route group
│   │   ├── login/page.tsx
│   │   └── signup/page.tsx
│   ├── (main)/                    # Main app route group
│   │   ├── layout.tsx             # Shared layout
│   │   ├── dashboard/
│   │   │   ├── page.tsx
│   │   │   └── loading.tsx
│   │   └── settings/
│   │       └── page.tsx
│   └── api/                       # API routes (if needed)
│       └── [...]/route.ts
├── components/
│   ├── ui/                        # shadcn/ui components
│   └── [feature]/                 # Feature components
├── lib/
│   ├── api/                       # API client
│   │   ├── client.ts              # Fetch wrapper
│   │   └── [resource].ts          # Resource-specific
│   ├── auth.ts                    # Better Auth server
│   ├── auth-client.ts             # Better Auth client
│   ├── utils.ts                   # Utilities
│   └── validations/               # Zod schemas
│       └── [resource].ts
├── actions/                       # Server actions
│   └── [resource].ts
├── types/
│   └── [resource].ts              # Shared types
├── middleware.ts                  # Auth/routing middleware
└── next.config.ts
```

---

## Generation Process

```
Check existing → Create structure → Add routes → Implement patterns → Integrate
```

### Step 1: Check Existing Setup

```
# Find existing Next.js
Glob: app/**/page.tsx, app/**/layout.tsx

# Check for existing patterns
Grep: "use server|use client" in app/**/*.tsx

# Find lib setup
Glob: lib/**/*.ts
```

### Step 2: Create Based on Need

| Need | Files to Create |
|------|-----------------|
| New project | Full structure above |
| Add route | `app/[route]/page.tsx`, `layout.tsx` |
| Add form | `actions/[name].ts`, `lib/validations/[name].ts` |
| Add API client | `lib/api/client.ts`, `lib/api/[resource].ts` |

### Step 2.5: Validate Structure (CRITICAL)

Before writing any files, run these checks:

**Check 1: Route Group Conflict Detection**
```typescript
// Check if creating route groups at root level
const routeGroups = filesToCreate.filter(f =>
  f.startsWith('app/(') && f.includes('/page.tsx')
)

// If route groups exist, ensure no root page.tsx
if (routeGroups.length > 0) {
  const hasRootPage = filesToCreate.includes('app/page.tsx')
  if (hasRootPage) {
    console.warn('⚠️ Removing app/page.tsx - conflicts with route groups')
    filesToCreate = filesToCreate.filter(f => f !== 'app/page.tsx')
  }
}
```

**Check 2: Client Directive Validation**
```typescript
// For each component, check if needs 'use client'
componentsToCreate.forEach(component => {
  if (needsClientDirective(component.code)) {
    if (!component.code.startsWith("'use client'")) {
      component.code = `'use client'\n\n${component.code}`
      console.log(`✅ Added 'use client' to ${component.name}`)
    }
  }
})
```

---

## Core Patterns

### Root Layout

```tsx
// app/layout.tsx
import { Inter } from "next/font/google"
import { Providers } from "@/components/providers"
import "@/app/globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: { default: "App", template: "%s | App" },
  description: "Description",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

### Server Component (Default)

```tsx
// app/posts/page.tsx
import { getPosts } from "@/lib/api/posts"

export default async function PostsPage() {
  const posts = await getPosts()

  return (
    <div>
      <h1>Posts</h1>
      {posts.map((post) => (
        <article key={post.id}>{post.title}</article>
      ))}
    </div>
  )
}
```

### Client Component (With 'use client')

**IMPORTANT**: Add 'use client' at the very first line (before imports) when component has:
- Event handlers (onClick, onChange, etc.)
- React hooks (useState, useEffect, etc.)
- Browser APIs (window, document, etc.)

```tsx
// components/counter.tsx
'use client' // ← REQUIRED for interactivity

import { useState } from 'react'
import { Button } from '@/components/ui/button'

export function Counter() {
  const [count, setCount] = useState(0)

  return (
    <Button onClick={() => setCount((c) => c + 1)}>
      Count: {count}
    </Button>
  )
}
```

**Common mistake**: Forgetting 'use client' on components that use shadcn/ui interactive components:

```tsx
// ❌ WRONG: Missing 'use client' but uses interactive Button
import { Button } from '@/components/ui/button'

export function Navbar() {
  return <Button onClick={() => console.log('click')}>Click</Button>
  // Error: Event handlers cannot be passed to Client Component props
}

// ✅ CORRECT: Has 'use client'
'use client'

import { Button } from '@/components/ui/button'

export function Navbar() {
  return <Button onClick={() => console.log('click')}>Click</Button>
}
```

### Server Action

```tsx
// actions/posts.ts
"use server"

import { revalidatePath } from "next/cache"
import { z } from "zod"
import { createPost } from "@/lib/api/posts"

const schema = z.object({
  title: z.string().min(1),
  content: z.string().min(1),
})

export async function createPostAction(formData: FormData) {
  const validated = schema.safeParse({
    title: formData.get("title"),
    content: formData.get("content"),
  })

  if (!validated.success) {
    return { error: validated.error.flatten().fieldErrors }
  }

  await createPost(validated.data)
  revalidatePath("/posts")

  return { success: true }
}
```

### API Client

```tsx
// lib/api/client.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function apiClient<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  })

  if (!res.ok) {
    throw new Error(`API Error: ${res.status}`)
  }

  return res.json()
}
```

---

## Standards

| Standard | Implementation |
|----------|----------------|
| **Components** | Server by default, `"use client"` only when needed |
| **Data fetching** | Fetch in server components, cache appropriately |
| **Mutations** | Server actions with zod validation |
| **Forms** | react-hook-form + zod + server actions |
| **Types** | Shared types in `types/`, infer from zod |
| **Errors** | Error boundaries, try-catch in actions |

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/app-router-pitfalls.md` | **CRITICAL** - Common issues and prevention patterns |
| `references/routing.md` | Layouts, pages, route groups, dynamic routes |
| `references/server-actions.md` | Mutations, form handling, revalidation |
| `references/data-fetching.md` | Caching, ISR, streaming, suspense |
| `references/forms.md` | react-hook-form + zod patterns |
| `references/api-client.md` | FastAPI integration, type-safe fetching |
| `references/patterns.md` | Error handling, loading, middleware, auth |

---

## Scripts

| Script | When to Use |
|--------|-------------|
| `scripts/validate-nextjs-structure.sh` | **Run after generation** - Validates route groups and 'use client' directives |
| `scripts/init-project.md` | Initialize new Next.js project with all dependencies |
| `scripts/generate-route.md` | Templates for new routes (basic, dynamic, protected) |
| `scripts/generate-crud.md` | Full CRUD for a resource (types, actions, components, pages) |

### Post-Generation Validation

After generating any Next.js code, run:
```bash
./.claude/skills/nextjs-pro/scripts/validate-nextjs-structure.sh
```

This will check for:
- Route group conflicts with root page.tsx
- Missing 'use client' directives on interactive components
- shadcn/ui components with incorrect directives

---

## Quick Commands

### Initialize Project
```bash
npx create-next-app@latest my-app --typescript --tailwind --eslint --app --src-dir=false
cd my-app
npm install react-hook-form @hookform/resolvers zod
```

### Add shadcn/ui
```bash
npx shadcn@latest init
npx shadcn@latest add button input form card
```

---

## Checklist

Before completing, verify:

### Structure & Routing
- [ ] App Router structure with layouts and pages
- [ ] **NO root `app/page.tsx` if using route groups at same level**
- [ ] Route groups properly structured (don't affect URLs)
- [ ] No conflicting page.tsx files

### Component Directives (CRITICAL)
- [ ] **ALL interactive components have 'use client' at line 1**
- [ ] shadcn/ui Button, Input, Dialog, etc. have 'use client'
- [ ] Components with onClick/onChange have 'use client'
- [ ] Components with useState/useEffect have 'use client'
- [ ] Server components don't have unnecessary 'use client'

### Data & Actions
- [ ] Server components for data fetching
- [ ] Client components only where needed
- [ ] Server actions with validation
- [ ] Error boundaries and loading states
- [ ] Type-safe API client (if using FastAPI)

### Configuration
- [ ] Middleware for auth/redirects (if needed)
- [ ] Metadata configured for SEO
- [ ] Environment variables documented
