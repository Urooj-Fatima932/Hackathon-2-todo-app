# Generate Route

Template for creating new routes with all common files.

## Basic Route

For a route like `/posts`:

### app/posts/page.tsx
```typescript
import { Metadata } from "next"

export const metadata: Metadata = {
  title: "Posts",
  description: "View all posts",
}

export default async function PostsPage() {
  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold mb-6">Posts</h1>
      {/* Content */}
    </div>
  )
}
```

### app/posts/loading.tsx
```typescript
import { Skeleton } from "@/components/ui/skeleton"

export default function Loading() {
  return (
    <div className="container py-8">
      <Skeleton className="h-10 w-48 mb-6" />
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    </div>
  )
}
```

### app/posts/error.tsx
```typescript
"use client"

import { Button } from "@/components/ui/button"

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="container py-8 text-center">
      <h2 className="text-2xl font-bold mb-4">Failed to load posts</h2>
      <p className="text-muted-foreground mb-4">{error.message}</p>
      <Button onClick={reset}>Try again</Button>
    </div>
  )
}
```

---

## Dynamic Route

For a route like `/posts/[slug]`:

### app/posts/[slug]/page.tsx
```typescript
import { Metadata } from "next"
import { notFound } from "next/navigation"

interface PageProps {
  params: Promise<{ slug: string }>
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params
  // const post = await getPost(slug)

  return {
    title: slug, // Replace with post.title
    description: `View post: ${slug}`,
  }
}

export default async function PostPage({ params }: PageProps) {
  const { slug } = await params
  // const post = await getPost(slug)

  // if (!post) notFound()

  return (
    <div className="container py-8">
      <article>
        <h1 className="text-3xl font-bold mb-4">{slug}</h1>
        {/* Content */}
      </article>
    </div>
  )
}
```

### app/posts/[slug]/loading.tsx
```typescript
import { Skeleton } from "@/components/ui/skeleton"

export default function Loading() {
  return (
    <div className="container py-8">
      <Skeleton className="h-10 w-3/4 mb-4" />
      <Skeleton className="h-6 w-1/4 mb-8" />
      <div className="space-y-4">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    </div>
  )
}
```

---

## Route with Layout

For a section like `/dashboard/*`:

### app/(dashboard)/layout.tsx
```typescript
import { Sidebar } from "@/components/dashboard/sidebar"
import { Header } from "@/components/dashboard/header"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1">
        <Header />
        <main className="p-6">{children}</main>
      </div>
    </div>
  )
}
```

### app/(dashboard)/dashboard/page.tsx
```typescript
import { Metadata } from "next"

export const metadata: Metadata = {
  title: "Dashboard",
}

export default async function DashboardPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      {/* Dashboard content */}
    </div>
  )
}
```

---

## Protected Route

For authenticated routes:

### app/(protected)/layout.tsx
```typescript
import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { redirect } from "next/navigation"

export default async function ProtectedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) {
    redirect("/login")
  }

  return <>{children}</>
}
```

---

## CRUD Route Set

For a full CRUD resource:

```
app/
└── posts/
    ├── page.tsx           # List posts (GET /posts)
    ├── loading.tsx
    ├── error.tsx
    ├── new/
    │   └── page.tsx       # Create post form
    └── [slug]/
        ├── page.tsx       # View post (GET /posts/:slug)
        ├── loading.tsx
        └── edit/
            └── page.tsx   # Edit post form
```

### app/posts/new/page.tsx
```typescript
import { Metadata } from "next"
import { CreatePostForm } from "@/components/posts/create-post-form"

export const metadata: Metadata = {
  title: "New Post",
}

export default function NewPostPage() {
  return (
    <div className="container py-8 max-w-2xl">
      <h1 className="text-3xl font-bold mb-6">Create New Post</h1>
      <CreatePostForm />
    </div>
  )
}
```

### app/posts/[slug]/edit/page.tsx
```typescript
import { Metadata } from "next"
import { notFound } from "next/navigation"
import { EditPostForm } from "@/components/posts/edit-post-form"

interface PageProps {
  params: Promise<{ slug: string }>
}

export const metadata: Metadata = {
  title: "Edit Post",
}

export default async function EditPostPage({ params }: PageProps) {
  const { slug } = await params
  // const post = await getPost(slug)
  // if (!post) notFound()

  return (
    <div className="container py-8 max-w-2xl">
      <h1 className="text-3xl font-bold mb-6">Edit Post</h1>
      {/* <EditPostForm post={post} /> */}
    </div>
  )
}
```
