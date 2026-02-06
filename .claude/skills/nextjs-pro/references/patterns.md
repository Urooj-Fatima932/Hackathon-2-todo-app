# Common Patterns

## Providers Setup

```tsx
// components/providers.tsx
"use client"

import { ThemeProvider } from "next-themes"
import { Toaster } from "@/components/ui/toaster"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      {children}
      <Toaster />
    </ThemeProvider>
  )
}
```

```tsx
// app/layout.tsx
import { Providers } from "@/components/providers"

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

## Middleware

### Basic Auth Middleware

```tsx
// middleware.ts
import { auth } from "@/lib/auth"
import { NextRequest, NextResponse } from "next/server"

const protectedRoutes = ["/dashboard", "/settings", "/profile"]
const authRoutes = ["/login", "/signup"]

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  const session = await auth.api.getSession({
    headers: request.headers,
  })

  // Protect routes
  const isProtected = protectedRoutes.some((r) => pathname.startsWith(r))
  if (isProtected && !session) {
    const url = new URL("/login", request.url)
    url.searchParams.set("callbackUrl", pathname)
    return NextResponse.redirect(url)
  }

  // Redirect logged-in users from auth pages
  const isAuthRoute = authRoutes.some((r) => pathname.startsWith(r))
  if (isAuthRoute && session) {
    return NextResponse.redirect(new URL("/dashboard", request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
}
```

### Rate Limiting Middleware

```tsx
// middleware.ts
import { NextRequest, NextResponse } from "next/server"

const rateLimit = new Map<string, { count: number; timestamp: number }>()

export function middleware(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith("/api")) {
    const ip = request.headers.get("x-forwarded-for") ?? "unknown"
    const now = Date.now()
    const windowMs = 60 * 1000 // 1 minute
    const maxRequests = 100

    const record = rateLimit.get(ip)

    if (record) {
      if (now - record.timestamp < windowMs) {
        if (record.count >= maxRequests) {
          return NextResponse.json(
            { error: "Too many requests" },
            { status: 429 }
          )
        }
        record.count++
      } else {
        record.count = 1
        record.timestamp = now
      }
    } else {
      rateLimit.set(ip, { count: 1, timestamp: now })
    }
  }

  return NextResponse.next()
}
```

## Error Boundary

```tsx
// app/error.tsx
"use client"

import { useEffect } from "react"
import { Button } from "@/components/ui/button"

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log to error reporting service
    console.error(error)
  }, [error])

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
      <h2 className="text-2xl font-bold">Something went wrong!</h2>
      <p className="text-muted-foreground">
        {error.message || "An unexpected error occurred"}
      </p>
      <Button onClick={reset}>Try again</Button>
    </div>
  )
}
```

## Loading Skeleton

```tsx
// components/skeletons/post-skeleton.tsx
import { Skeleton } from "@/components/ui/skeleton"

export function PostSkeleton() {
  return (
    <div className="space-y-3">
      <Skeleton className="h-8 w-3/4" />
      <Skeleton className="h-4 w-1/4" />
      <Skeleton className="h-32 w-full" />
    </div>
  )
}

export function PostListSkeleton() {
  return (
    <div className="space-y-6">
      {[...Array(5)].map((_, i) => (
        <PostSkeleton key={i} />
      ))}
    </div>
  )
}

// app/posts/loading.tsx
export { PostListSkeleton as default } from "@/components/skeletons/post-skeleton"
```

## Not Found Page

```tsx
// app/not-found.tsx
import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
      <h1 className="text-6xl font-bold">404</h1>
      <h2 className="text-2xl">Page not found</h2>
      <p className="text-muted-foreground">
        The page you're looking for doesn't exist.
      </p>
      <Button asChild>
        <Link href="/">Go home</Link>
      </Button>
    </div>
  )
}
```

## Authentication Check Component

```tsx
// components/auth-check.tsx
import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { redirect } from "next/navigation"

interface AuthCheckProps {
  children: React.ReactNode
  fallback?: React.ReactNode
  redirectTo?: string
}

export async function AuthCheck({
  children,
  fallback,
  redirectTo,
}: AuthCheckProps) {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) {
    if (redirectTo) {
      redirect(redirectTo)
    }
    return fallback ? <>{fallback}</> : null
  }

  return <>{children}</>
}

// Usage
<AuthCheck redirectTo="/login">
  <ProtectedContent />
</AuthCheck>

<AuthCheck fallback={<LoginPrompt />}>
  <UserMenu />
</AuthCheck>
```

## Toast Notifications

```tsx
// hooks/use-toast-action.ts
"use client"

import { useToast } from "@/hooks/use-toast"
import { useTransition } from "react"

export function useToastAction<T>(
  action: () => Promise<{ success?: boolean; error?: string; data?: T }>
) {
  const { toast } = useToast()
  const [isPending, startTransition] = useTransition()

  const execute = () => {
    startTransition(async () => {
      const result = await action()

      if (result.error) {
        toast({
          title: "Error",
          description: result.error,
          variant: "destructive",
        })
      } else if (result.success) {
        toast({
          title: "Success",
          description: "Operation completed successfully",
        })
      }
    })
  }

  return { execute, isPending }
}

// Usage
const { execute, isPending } = useToastAction(() => deletePost(postId))

<Button onClick={execute} disabled={isPending}>
  {isPending ? "Deleting..." : "Delete"}
</Button>
```

## Optimistic UI Update

```tsx
// components/like-button.tsx
"use client"

import { useOptimistic, useTransition } from "react"
import { likePost, unlikePost } from "@/actions/posts"
import { Heart } from "lucide-react"
import { cn } from "@/lib/utils"

interface LikeButtonProps {
  postId: string
  initialLikes: number
  initialLiked: boolean
}

export function LikeButton({
  postId,
  initialLikes,
  initialLiked,
}: LikeButtonProps) {
  const [isPending, startTransition] = useTransition()

  const [optimistic, setOptimistic] = useOptimistic(
    { likes: initialLikes, liked: initialLiked },
    (state, liked: boolean) => ({
      likes: liked ? state.likes + 1 : state.likes - 1,
      liked,
    })
  )

  const handleClick = () => {
    const newLiked = !optimistic.liked
    startTransition(async () => {
      setOptimistic(newLiked)
      if (newLiked) {
        await likePost(postId)
      } else {
        await unlikePost(postId)
      }
    })
  }

  return (
    <button
      onClick={handleClick}
      disabled={isPending}
      className="flex items-center gap-1"
    >
      <Heart
        className={cn(
          "h-5 w-5",
          optimistic.liked && "fill-red-500 text-red-500"
        )}
      />
      <span>{optimistic.likes}</span>
    </button>
  )
}
```

## Infinite Scroll

```tsx
// components/infinite-posts.tsx
"use client"

import { useEffect, useRef, useState } from "react"
import { useIntersectionObserver } from "@/hooks/use-intersection-observer"
import { getPosts } from "@/lib/api/posts"
import type { Post } from "@/types/post"

interface InfinitePostsProps {
  initialPosts: Post[]
  initialHasMore: boolean
}

export function InfinitePosts({
  initialPosts,
  initialHasMore,
}: InfinitePostsProps) {
  const [posts, setPosts] = useState(initialPosts)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(initialHasMore)
  const [loading, setLoading] = useState(false)

  const loadMoreRef = useRef<HTMLDivElement>(null)
  const entry = useIntersectionObserver(loadMoreRef, {})
  const isVisible = !!entry?.isIntersecting

  useEffect(() => {
    if (isVisible && hasMore && !loading) {
      loadMore()
    }
  }, [isVisible, hasMore, loading])

  const loadMore = async () => {
    setLoading(true)
    const nextPage = page + 1
    const { items, totalPages } = await getPosts({ page: nextPage })

    setPosts((prev) => [...prev, ...items])
    setPage(nextPage)
    setHasMore(nextPage < totalPages)
    setLoading(false)
  }

  return (
    <div>
      {posts.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}

      <div ref={loadMoreRef}>
        {loading && <Spinner />}
        {!hasMore && <p>No more posts</p>}
      </div>
    </div>
  )
}
```

## Search with Debounce

```tsx
// components/search.tsx
"use client"

import { useRouter, useSearchParams } from "next/navigation"
import { useDebouncedCallback } from "use-debounce"
import { Input } from "@/components/ui/input"
import { Search as SearchIcon } from "lucide-react"

export function Search() {
  const router = useRouter()
  const searchParams = useSearchParams()

  const handleSearch = useDebouncedCallback((term: string) => {
    const params = new URLSearchParams(searchParams)
    if (term) {
      params.set("q", term)
    } else {
      params.delete("q")
    }
    router.push(`/search?${params.toString()}`)
  }, 300)

  return (
    <div className="relative">
      <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <Input
        placeholder="Search..."
        defaultValue={searchParams.get("q") ?? ""}
        onChange={(e) => handleSearch(e.target.value)}
        className="pl-10"
      />
    </div>
  )
}
```

## Modal with Parallel Routes

```tsx
// app/@modal/(.)photo/[id]/page.tsx
import { Modal } from "@/components/modal"
import { getPhoto } from "@/lib/api/photos"

export default async function PhotoModal({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const photo = await getPhoto(id)

  return (
    <Modal>
      <img src={photo.url} alt={photo.title} className="w-full" />
    </Modal>
  )
}

// components/modal.tsx
"use client"

import { useRouter } from "next/navigation"
import { Dialog, DialogContent } from "@/components/ui/dialog"

export function Modal({ children }: { children: React.ReactNode }) {
  const router = useRouter()

  return (
    <Dialog open onOpenChange={() => router.back()}>
      <DialogContent>{children}</DialogContent>
    </Dialog>
  )
}
```

## Environment Variables

```tsx
// lib/env.ts
import { z } from "zod"

const envSchema = z.object({
  NODE_ENV: z.enum(["development", "production", "test"]),
  NEXT_PUBLIC_API_URL: z.string().url(),
  BETTER_AUTH_SECRET: z.string().min(32),
  DATABASE_URL: z.string(),
})

export const env = envSchema.parse({
  NODE_ENV: process.env.NODE_ENV,
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  BETTER_AUTH_SECRET: process.env.BETTER_AUTH_SECRET,
  DATABASE_URL: process.env.DATABASE_URL,
})

// Usage
import { env } from "@/lib/env"
console.log(env.NEXT_PUBLIC_API_URL)
```

## Conditional Rendering by Auth

```tsx
// Server Component
import { auth } from "@/lib/auth"
import { headers } from "next/headers"

export default async function Page() {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  return (
    <nav>
      {session ? (
        <>
          <span>{session.user.name}</span>
          <SignOutButton />
        </>
      ) : (
        <Link href="/login">Sign In</Link>
      )}
    </nav>
  )
}
```

```tsx
// Client Component
"use client"

import { useSession } from "@/lib/auth-client"

export function AuthButton() {
  const { data: session, isPending } = useSession()

  if (isPending) return <Skeleton className="h-10 w-24" />

  return session ? (
    <UserMenu user={session.user} />
  ) : (
    <Button asChild>
      <Link href="/login">Sign In</Link>
    </Button>
  )
}
```
