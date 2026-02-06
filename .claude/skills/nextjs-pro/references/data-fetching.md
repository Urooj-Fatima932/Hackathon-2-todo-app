# Data Fetching

## Server Components (Default)

Fetch data directly in server components:

```tsx
// app/posts/page.tsx
async function getPosts() {
  const res = await fetch("https://api.example.com/posts")
  if (!res.ok) throw new Error("Failed to fetch posts")
  return res.json()
}

export default async function PostsPage() {
  const posts = await getPosts()

  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```

## Caching Strategies

### Default (Cached)

```tsx
// Cached indefinitely (default in Next.js 14)
const data = await fetch("https://api.example.com/data")
```

### Revalidate (ISR)

```tsx
// Revalidate every hour
const data = await fetch("https://api.example.com/data", {
  next: { revalidate: 3600 },
})
```

### No Cache

```tsx
// Always fetch fresh
const data = await fetch("https://api.example.com/data", {
  cache: "no-store",
})
```

### Tagged Cache

```tsx
// Tag for on-demand revalidation
const data = await fetch("https://api.example.com/posts", {
  next: { tags: ["posts"] },
})

// Later, invalidate by tag
import { revalidateTag } from "next/cache"
revalidateTag("posts")
```

## Parallel Data Fetching

```tsx
export default async function DashboardPage() {
  // Fetch in parallel
  const [user, posts, analytics] = await Promise.all([
    getUser(),
    getPosts(),
    getAnalytics(),
  ])

  return (
    <div>
      <UserCard user={user} />
      <PostsList posts={posts} />
      <AnalyticsChart data={analytics} />
    </div>
  )
}
```

## Sequential Data Fetching

```tsx
export default async function PostPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  // Sequential: author depends on post
  const post = await getPost(id)
  const author = await getUser(post.authorId)

  return (
    <article>
      <h1>{post.title}</h1>
      <p>By {author.name}</p>
    </article>
  )
}
```

## Streaming with Suspense

```tsx
import { Suspense } from "react"

export default function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>

      {/* Fast: renders immediately */}
      <WelcomeMessage />

      {/* Slow: streams when ready */}
      <Suspense fallback={<ChartSkeleton />}>
        <SlowChart />
      </Suspense>

      <Suspense fallback={<TableSkeleton />}>
        <SlowTable />
      </Suspense>
    </div>
  )
}

// Async component that takes time
async function SlowChart() {
  const data = await getChartData() // Takes 2s
  return <Chart data={data} />
}
```

## Request Memoization

Same fetch in same render pass is automatically deduped:

```tsx
// lib/data.ts
export async function getUser(id: string) {
  // This fetch is memoized
  const res = await fetch(`/api/users/${id}`)
  return res.json()
}

// Both components call getUser(1), but only 1 request is made
// app/page.tsx
export default async function Page() {
  const user = await getUser("1")
  return <UserProfile user={user} />
}

// components/sidebar.tsx
export default async function Sidebar() {
  const user = await getUser("1") // Reuses cached result
  return <UserCard user={user} />
}
```

## Dynamic Rendering

Force dynamic rendering:

```tsx
// Option 1: Export dynamic config
export const dynamic = "force-dynamic"

// Option 2: Use dynamic functions
import { cookies, headers } from "next/headers"

export default async function Page() {
  const cookieStore = await cookies() // Makes page dynamic
  const headersList = await headers() // Makes page dynamic

  return <div>...</div>
}
```

## Fetch Wrapper for FastAPI

```tsx
// lib/api/client.ts
const API_URL = process.env.API_URL || "http://localhost:8000"

type FetchOptions = RequestInit & {
  next?: { revalidate?: number; tags?: string[] }
}

export async function api<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const url = `${API_URL}${endpoint}`

  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Unknown error" }))
    throw new Error(error.detail || `API Error: ${res.status}`)
  }

  return res.json()
}

// Usage
const posts = await api<Post[]>("/api/posts", {
  next: { revalidate: 60, tags: ["posts"] },
})
```

## With Authentication

```tsx
// lib/api/client.ts
import { auth } from "@/lib/auth"
import { headers } from "next/headers"

export async function authApi<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) {
    throw new Error("Unauthorized")
  }

  return api<T>(endpoint, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${session.accessToken}`,
    },
  })
}
```

## generateStaticParams

Pre-render dynamic routes at build time:

```tsx
// app/posts/[slug]/page.tsx
export async function generateStaticParams() {
  const posts = await api<Post[]>("/api/posts")

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
  const post = await api<Post>(`/api/posts/${slug}`)

  return <article>{post.title}</article>
}
```

## Route Segment Config

```tsx
// app/posts/page.tsx

// Dynamic behavior
export const dynamic = "auto" | "force-dynamic" | "error" | "force-static"

// Revalidation
export const revalidate = false | 0 | number

// Runtime
export const runtime = "nodejs" | "edge"

// Preferred region
export const preferredRegion = "auto" | "global" | "home" | string | string[]
```

## Error Handling

```tsx
// lib/api/client.ts
export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string
  ) {
    super(detail)
    this.name = "ApiError"
  }
}

export async function api<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const res = await fetch(`${API_URL}${endpoint}`, options)

  if (!res.ok) {
    const error = await res.json().catch(() => ({}))
    throw new ApiError(res.status, error.detail || "Request failed")
  }

  return res.json()
}

// Usage with error boundary
export default async function PostsPage() {
  try {
    const posts = await api<Post[]>("/api/posts")
    return <PostsList posts={posts} />
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound()
    }
    throw error // Let error boundary handle it
  }
}
```

## Loading States

```tsx
// app/posts/loading.tsx
export default function Loading() {
  return (
    <div className="space-y-4">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-3/4 mb-2" />
          <div className="h-4 bg-gray-200 rounded w-1/2" />
        </div>
      ))}
    </div>
  )
}
```

## SWR for Client-Side

For client components that need real-time updates:

```tsx
"use client"

import useSWR from "swr"

const fetcher = (url: string) => fetch(url).then((r) => r.json())

export function LivePosts() {
  const { data, error, isLoading, mutate } = useSWR("/api/posts", fetcher, {
    refreshInterval: 5000, // Poll every 5s
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error loading posts</div>

  return (
    <div>
      {data.map((post) => (
        <div key={post.id}>{post.title}</div>
      ))}
      <button onClick={() => mutate()}>Refresh</button>
    </div>
  )
}
```

## React Query for Complex Cases

```tsx
"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"

export function Posts() {
  const queryClient = useQueryClient()

  const { data: posts, isLoading } = useQuery({
    queryKey: ["posts"],
    queryFn: () => fetch("/api/posts").then((r) => r.json()),
  })

  const createPost = useMutation({
    mutationFn: (newPost) =>
      fetch("/api/posts", {
        method: "POST",
        body: JSON.stringify(newPost),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["posts"] })
    },
  })

  if (isLoading) return <div>Loading...</div>

  return (
    <div>
      {posts.map((post) => (
        <div key={post.id}>{post.title}</div>
      ))}
    </div>
  )
}
```
