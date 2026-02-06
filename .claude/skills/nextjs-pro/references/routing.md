# Next.js App Router - Routing

## File Conventions

| File | Purpose |
|------|---------|
| `layout.tsx` | Shared UI, persists across navigations |
| `page.tsx` | Unique route content |
| `loading.tsx` | Suspense fallback while loading |
| `error.tsx` | Error boundary |
| `not-found.tsx` | 404 page |
| `route.ts` | API route handler |
| `template.tsx` | Re-renders on each navigation |
| `default.tsx` | Fallback for parallel routes |

## Basic Routing

```
app/
├── page.tsx              → /
├── about/
│   └── page.tsx          → /about
├── blog/
│   ├── page.tsx          → /blog
│   └── [slug]/
│       └── page.tsx      → /blog/hello-world
```

## Layouts

### Root Layout (Required)

```tsx
// app/layout.tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

### Nested Layouts

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1">{children}</main>
    </div>
  )
}
```

## Route Groups

Organize routes without affecting URL:

```
app/
├── (marketing)/
│   ├── layout.tsx        # Marketing layout
│   ├── page.tsx          → /
│   └── about/page.tsx    → /about
├── (app)/
│   ├── layout.tsx        # App layout (with sidebar)
│   └── dashboard/
│       └── page.tsx      → /dashboard
```

### Multiple Root Layouts

```
app/
├── (marketing)/
│   ├── layout.tsx        # Layout A
│   └── page.tsx
├── (app)/
│   ├── layout.tsx        # Layout B
│   └── dashboard/page.tsx
```

## Dynamic Routes

### Single Segment

```tsx
// app/posts/[id]/page.tsx
export default async function PostPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  return <div>Post {id}</div>
}
```

### Multiple Segments

```tsx
// app/shop/[category]/[product]/page.tsx
export default async function ProductPage({
  params,
}: {
  params: Promise<{ category: string; product: string }>
}) {
  const { category, product } = await params
  return <div>{category} - {product}</div>
}
```

### Catch-All Segments

```tsx
// app/docs/[...slug]/page.tsx
// Matches /docs/a, /docs/a/b, /docs/a/b/c

export default async function DocsPage({
  params,
}: {
  params: Promise<{ slug: string[] }>
}) {
  const { slug } = await params
  // slug = ["a", "b", "c"] for /docs/a/b/c
  return <div>{slug.join("/")}</div>
}
```

### Optional Catch-All

```tsx
// app/shop/[[...slug]]/page.tsx
// Matches /shop, /shop/a, /shop/a/b
```

## Static Params Generation

```tsx
// app/posts/[slug]/page.tsx
export async function generateStaticParams() {
  const posts = await getPosts()

  return posts.map((post) => ({
    slug: post.slug,
  }))
}

export default async function PostPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const post = await getPost(slug)
  return <article>{post.title}</article>
}
```

## Parallel Routes

Render multiple pages simultaneously in the same layout:

```
app/
├── layout.tsx
├── @team/
│   └── page.tsx
├── @analytics/
│   └── page.tsx
└── page.tsx
```

```tsx
// app/layout.tsx
export default function Layout({
  children,
  team,
  analytics,
}: {
  children: React.ReactNode
  team: React.ReactNode
  analytics: React.ReactNode
}) {
  return (
    <div>
      {children}
      <div className="grid grid-cols-2">
        {team}
        {analytics}
      </div>
    </div>
  )
}
```

### Default Fallback

```tsx
// app/@team/default.tsx
export default function Default() {
  return null // or fallback UI
}
```

## Intercepting Routes

Intercept routes to show in modal while preserving URL:

```
app/
├── feed/
│   └── page.tsx
├── @modal/
│   └── (.)photo/[id]/
│       └── page.tsx      # Intercepted modal
└── photo/[id]/
    └── page.tsx          # Full page (direct navigation)
```

| Convention | Matches |
|------------|---------|
| `(.)` | Same level |
| `(..)` | One level up |
| `(..)(..)` | Two levels up |
| `(...)` | Root |

## Loading States

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-1/4 mb-4" />
      <div className="h-64 bg-gray-200 rounded" />
    </div>
  )
}
```

### With Suspense Boundaries

```tsx
// app/dashboard/page.tsx
import { Suspense } from "react"

export default function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<ChartSkeleton />}>
        <Chart />
      </Suspense>
      <Suspense fallback={<TableSkeleton />}>
        <RecentActivity />
      </Suspense>
    </div>
  )
}
```

## Error Handling

```tsx
// app/dashboard/error.tsx
"use client"

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}
```

### Global Error

```tsx
// app/global-error.tsx
"use client"

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html>
      <body>
        <h2>Something went wrong!</h2>
        <button onClick={() => reset()}>Try again</button>
      </body>
    </html>
  )
}
```

## Not Found

```tsx
// app/not-found.tsx
import Link from "next/link"

export default function NotFound() {
  return (
    <div>
      <h2>Not Found</h2>
      <p>Could not find requested resource</p>
      <Link href="/">Return Home</Link>
    </div>
  )
}
```

### Trigger Not Found

```tsx
import { notFound } from "next/navigation"

export default async function PostPage({ params }) {
  const post = await getPost(params.slug)

  if (!post) {
    notFound()
  }

  return <article>{post.title}</article>
}
```

## Navigation

### Link Component

```tsx
import Link from "next/link"

// Basic
<Link href="/about">About</Link>

// Dynamic
<Link href={`/posts/${post.slug}`}>{post.title}</Link>

// With query params
<Link href={{ pathname: "/search", query: { q: "hello" } }}>
  Search
</Link>

// Replace history
<Link href="/login" replace>Login</Link>

// Scroll to top disabled
<Link href="/posts" scroll={false}>Posts</Link>

// Prefetch disabled
<Link href="/heavy-page" prefetch={false}>Heavy Page</Link>
```

### useRouter (Client Components)

```tsx
"use client"

import { useRouter } from "next/navigation"

export function NavigateButton() {
  const router = useRouter()

  return (
    <button onClick={() => router.push("/dashboard")}>
      Go to Dashboard
    </button>
  )
}

// Methods
router.push("/path")      // Navigate
router.replace("/path")   // Replace current history entry
router.refresh()          // Refresh current route
router.back()             // Go back
router.forward()          // Go forward
router.prefetch("/path")  // Prefetch route
```

### redirect (Server)

```tsx
import { redirect } from "next/navigation"

export default async function Page() {
  const session = await getSession()

  if (!session) {
    redirect("/login")
  }

  return <Dashboard />
}
```

### permanentRedirect

```tsx
import { permanentRedirect } from "next/navigation"

// For permanent URL changes (301)
permanentRedirect("/new-path")
```

## Metadata

### Static Metadata

```tsx
// app/about/page.tsx
export const metadata = {
  title: "About Us",
  description: "Learn about our company",
}
```

### Dynamic Metadata

```tsx
// app/posts/[slug]/page.tsx
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const post = await getPost(slug)

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [post.image],
    },
  }
}
```

### Template Titles

```tsx
// app/layout.tsx
export const metadata = {
  title: {
    default: "My App",
    template: "%s | My App",
  },
}

// app/about/page.tsx
export const metadata = {
  title: "About", // Results in "About | My App"
}
```
