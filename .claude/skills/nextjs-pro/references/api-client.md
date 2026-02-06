# FastAPI Integration

## API Client Setup

### Base Client

```tsx
// lib/api/client.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
    public errors?: Record<string, string[]>
  ) {
    super(detail)
    this.name = "ApiError"
  }
}

type FetchOptions = Omit<RequestInit, "body"> & {
  body?: unknown
  next?: { revalidate?: number; tags?: string[] }
}

export async function api<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { body, ...init } = options

  const res = await fetch(`${API_URL}${endpoint}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init.headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }))
    throw new ApiError(res.status, error.detail, error.errors)
  }

  // Handle empty responses
  const text = await res.text()
  return text ? JSON.parse(text) : null
}
```

### Authenticated Client

```tsx
// lib/api/auth-client.ts
import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { api, FetchOptions } from "./client"

export async function authApi<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
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

## Type Definitions

### Shared Types

```tsx
// types/api.ts

// Pagination
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface PaginationParams {
  page?: number
  pageSize?: number
}

// API Error
export interface ApiErrorResponse {
  detail: string
  errors?: Record<string, string[]>
}
```

### Resource Types

```tsx
// types/post.ts
export interface Post {
  id: string
  title: string
  content: string
  slug: string
  published: boolean
  authorId: string
  createdAt: string
  updatedAt: string
}

export interface CreatePostInput {
  title: string
  content: string
  published?: boolean
}

export interface UpdatePostInput {
  title?: string
  content?: string
  published?: boolean
}
```

## Resource-Specific API Functions

### Posts API

```tsx
// lib/api/posts.ts
import { api, authApi } from "./client"
import type { Post, CreatePostInput, UpdatePostInput } from "@/types/post"
import type { PaginatedResponse, PaginationParams } from "@/types/api"

const BASE_PATH = "/api/v1/posts"

// Public endpoints (cached)
export async function getPosts(
  params?: PaginationParams
): Promise<PaginatedResponse<Post>> {
  const searchParams = new URLSearchParams()
  if (params?.page) searchParams.set("page", String(params.page))
  if (params?.pageSize) searchParams.set("page_size", String(params.pageSize))

  const query = searchParams.toString()
  return api<PaginatedResponse<Post>>(
    `${BASE_PATH}${query ? `?${query}` : ""}`,
    { next: { revalidate: 60, tags: ["posts"] } }
  )
}

export async function getPost(slug: string): Promise<Post> {
  return api<Post>(`${BASE_PATH}/${slug}`, {
    next: { revalidate: 60, tags: ["posts", `post-${slug}`] },
  })
}

// Protected endpoints
export async function createPost(data: CreatePostInput): Promise<Post> {
  return authApi<Post>(BASE_PATH, {
    method: "POST",
    body: data,
  })
}

export async function updatePost(
  id: string,
  data: UpdatePostInput
): Promise<Post> {
  return authApi<Post>(`${BASE_PATH}/${id}`, {
    method: "PATCH",
    body: data,
  })
}

export async function deletePost(id: string): Promise<void> {
  return authApi<void>(`${BASE_PATH}/${id}`, {
    method: "DELETE",
  })
}
```

### Users API

```tsx
// lib/api/users.ts
import { api, authApi } from "./client"
import type { User, UpdateUserInput } from "@/types/user"

const BASE_PATH = "/api/v1/users"

export async function getUser(id: string): Promise<User> {
  return api<User>(`${BASE_PATH}/${id}`)
}

export async function getCurrentUser(): Promise<User> {
  return authApi<User>(`${BASE_PATH}/me`)
}

export async function updateCurrentUser(data: UpdateUserInput): Promise<User> {
  return authApi<User>(`${BASE_PATH}/me`, {
    method: "PATCH",
    body: data,
  })
}
```

## Usage in Server Components

```tsx
// app/posts/page.tsx
import { getPosts } from "@/lib/api/posts"
import { PostCard } from "@/components/post-card"

export default async function PostsPage() {
  const { items: posts, totalPages } = await getPosts({ page: 1, pageSize: 10 })

  return (
    <div>
      <h1>Posts</h1>
      <div className="grid gap-4">
        {posts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>
    </div>
  )
}
```

## Usage in Server Actions

```tsx
// actions/posts.ts
"use server"

import { revalidateTag } from "next/cache"
import { redirect } from "next/navigation"
import { createPost, updatePost, deletePost } from "@/lib/api/posts"
import { createPostSchema } from "@/lib/validations/post"

export async function createPostAction(formData: FormData) {
  const validated = createPostSchema.safeParse({
    title: formData.get("title"),
    content: formData.get("content"),
  })

  if (!validated.success) {
    return { error: validated.error.flatten().fieldErrors }
  }

  try {
    const post = await createPost(validated.data)
    revalidateTag("posts")
    redirect(`/posts/${post.slug}`)
  } catch (error) {
    if (error instanceof ApiError) {
      return { error: error.detail }
    }
    return { error: "Failed to create post" }
  }
}

export async function deletePostAction(id: string) {
  try {
    await deletePost(id)
    revalidateTag("posts")
  } catch (error) {
    if (error instanceof ApiError) {
      return { error: error.detail }
    }
    return { error: "Failed to delete post" }
  }
}
```

## Client-Side Fetching (SWR)

```tsx
// hooks/use-posts.ts
"use client"

import useSWR from "swr"
import type { Post } from "@/types/post"
import type { PaginatedResponse } from "@/types/api"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

const fetcher = async (url: string) => {
  const res = await fetch(url)
  if (!res.ok) throw new Error("Failed to fetch")
  return res.json()
}

export function usePosts(page = 1, pageSize = 10) {
  const { data, error, isLoading, mutate } = useSWR<PaginatedResponse<Post>>(
    `${API_URL}/api/v1/posts?page=${page}&page_size=${pageSize}`,
    fetcher
  )

  return {
    posts: data?.items ?? [],
    total: data?.total ?? 0,
    totalPages: data?.totalPages ?? 0,
    isLoading,
    error,
    refresh: mutate,
  }
}

export function usePost(slug: string) {
  const { data, error, isLoading, mutate } = useSWR<Post>(
    slug ? `${API_URL}/api/v1/posts/${slug}` : null,
    fetcher
  )

  return { post: data, isLoading, error, refresh: mutate }
}
```

## OpenAPI Type Generation

Generate TypeScript types from FastAPI OpenAPI schema:

```bash
# Install openapi-typescript
npm install -D openapi-typescript

# Generate types from running FastAPI server
npx openapi-typescript http://localhost:8000/openapi.json -o types/api-schema.ts

# Or from exported schema file
npx openapi-typescript ./openapi.json -o types/api-schema.ts
```

### Usage with Generated Types

```tsx
// types/api-schema.ts (generated)
export interface paths {
  "/api/v1/posts": {
    get: {
      responses: {
        200: {
          content: {
            "application/json": components["schemas"]["PaginatedPost"]
          }
        }
      }
    }
    post: {
      requestBody: {
        content: {
          "application/json": components["schemas"]["CreatePost"]
        }
      }
      responses: {
        201: {
          content: {
            "application/json": components["schemas"]["Post"]
          }
        }
      }
    }
  }
}

export interface components {
  schemas: {
    Post: {
      id: string
      title: string
      // ...
    }
    CreatePost: {
      title: string
      content: string
    }
  }
}
```

```tsx
// lib/api/typed-client.ts
import type { paths, components } from "@/types/api-schema"

type Post = components["schemas"]["Post"]
type CreatePost = components["schemas"]["CreatePost"]

// Type-safe API calls
export async function createPost(data: CreatePost): Promise<Post> {
  return authApi<Post>("/api/v1/posts", {
    method: "POST",
    body: data,
  })
}
```

## Environment Configuration

```bash
# .env.local
NEXT_PUBLIC_API_URL="http://localhost:8000"

# .env.production
NEXT_PUBLIC_API_URL="https://api.yourdomain.com"
```

## Error Handling Pattern

```tsx
// app/posts/[slug]/page.tsx
import { notFound } from "next/navigation"
import { getPost } from "@/lib/api/posts"
import { ApiError } from "@/lib/api/client"

export default async function PostPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params

  try {
    const post = await getPost(slug)
    return <PostContent post={post} />
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound()
    }
    throw error // Let error boundary handle
  }
}
```

## CORS Configuration (FastAPI)

Ensure FastAPI allows requests from Next.js:

```python
# FastAPI main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
