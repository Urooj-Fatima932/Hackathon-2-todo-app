# Protected Routes

## Next.js - Server Components

### Using auth.api.getSession()

```typescript
// app/dashboard/page.tsx
import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { redirect } from "next/navigation"

export default async function DashboardPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) {
    redirect("/login")
  }

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome, {session.user.name}</p>
    </div>
  )
}
```

### Protected Layout

```typescript
// app/(protected)/layout.tsx
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

  return (
    <div className="min-h-screen">
      <nav className="border-b p-4">
        <span>Logged in as {session.user.email}</span>
      </nav>
      <main className="p-4">{children}</main>
    </div>
  )
}
```

### Helper Function

```typescript
// lib/auth-utils.ts
import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { redirect } from "next/navigation"

export async function requireAuth() {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) {
    redirect("/login")
  }

  return session
}

export async function getOptionalSession() {
  return await auth.api.getSession({
    headers: await headers(),
  })
}

// Usage
export default async function ProtectedPage() {
  const session = await requireAuth()
  return <div>Hello {session.user.name}</div>
}
```

## Next.js - Middleware

### Basic Route Protection

```typescript
// middleware.ts
import { auth } from "@/lib/auth"
import { NextRequest, NextResponse } from "next/server"

// Routes that require authentication
const protectedRoutes = ["/dashboard", "/settings", "/profile"]

// Routes that should redirect to dashboard if authenticated
const authRoutes = ["/login", "/signup", "/forgot-password"]

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  const session = await auth.api.getSession({
    headers: request.headers,
  })

  const isProtectedRoute = protectedRoutes.some((route) =>
    pathname.startsWith(route)
  )
  const isAuthRoute = authRoutes.some((route) => pathname.startsWith(route))

  // Redirect unauthenticated users to login
  if (isProtectedRoute && !session) {
    const loginUrl = new URL("/login", request.url)
    loginUrl.searchParams.set("callbackUrl", pathname)
    return NextResponse.redirect(loginUrl)
  }

  // Redirect authenticated users away from auth pages
  if (isAuthRoute && session) {
    return NextResponse.redirect(new URL("/dashboard", request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico|public).*)",
  ],
}
```

### Role-Based Middleware

```typescript
// middleware.ts
import { auth } from "@/lib/auth"
import { NextRequest, NextResponse } from "next/server"

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  const session = await auth.api.getSession({
    headers: request.headers,
  })

  // Admin routes
  if (pathname.startsWith("/admin")) {
    if (!session) {
      return NextResponse.redirect(new URL("/login", request.url))
    }
    // Check admin role (customize based on your user model)
    if (session.user.role !== "admin") {
      return NextResponse.redirect(new URL("/unauthorized", request.url))
    }
  }

  // Moderator routes
  if (pathname.startsWith("/moderate")) {
    if (!session) {
      return NextResponse.redirect(new URL("/login", request.url))
    }
    if (!["admin", "moderator"].includes(session.user.role)) {
      return NextResponse.redirect(new URL("/unauthorized", request.url))
    }
  }

  // Regular protected routes
  if (pathname.startsWith("/dashboard") && !session) {
    return NextResponse.redirect(new URL("/login", request.url))
  }

  return NextResponse.next()
}
```

## Next.js - Client Components

### useSession Hook

```typescript
"use client"

import { useSession } from "@/lib/auth-client"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

export function ProtectedComponent() {
  const { data: session, isPending } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (!isPending && !session) {
      router.push("/login")
    }
  }, [session, isPending, router])

  if (isPending) {
    return <div>Loading...</div>
  }

  if (!session) {
    return null
  }

  return <div>Protected content for {session.user.name}</div>
}
```

### Protected Component Wrapper

```typescript
"use client"

import { useSession } from "@/lib/auth-client"
import { useRouter } from "next/navigation"
import { useEffect, ReactNode } from "react"

interface ProtectedProps {
  children: ReactNode
  fallback?: ReactNode
  redirectTo?: string
}

export function Protected({
  children,
  fallback = <div>Loading...</div>,
  redirectTo = "/login",
}: ProtectedProps) {
  const { data: session, isPending } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (!isPending && !session) {
      router.push(redirectTo)
    }
  }, [session, isPending, router, redirectTo])

  if (isPending) {
    return <>{fallback}</>
  }

  if (!session) {
    return null
  }

  return <>{children}</>
}

// Usage
export default function ProtectedPage() {
  return (
    <Protected>
      <DashboardContent />
    </Protected>
  )
}
```

## Next.js - API Routes

### Protected API Route

```typescript
// app/api/protected/route.ts
import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { NextResponse } from "next/server"

export async function GET() {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) {
    return NextResponse.json(
      { error: "Unauthorized" },
      { status: 401 }
    )
  }

  return NextResponse.json({
    message: "Protected data",
    user: session.user,
  })
}

export async function POST(request: Request) {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) {
    return NextResponse.json(
      { error: "Unauthorized" },
      { status: 401 }
    )
  }

  const body = await request.json()

  // Process authenticated request
  return NextResponse.json({
    success: true,
    userId: session.user.id,
    data: body,
  })
}
```

### Role-Protected API Route

```typescript
// app/api/admin/users/route.ts
import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { NextResponse } from "next/server"

export async function GET() {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  if (session.user.role !== "admin") {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 })
  }

  // Return admin data
  return NextResponse.json({ users: [] })
}
```

## Next.js - Server Actions

### Protected Server Action

```typescript
// app/actions/posts.ts
"use server"

import { auth } from "@/lib/auth"
import { headers } from "next/headers"

export async function createPost(formData: FormData) {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) {
    throw new Error("Unauthorized")
  }

  const title = formData.get("title") as string
  const content = formData.get("content") as string

  // Create post with session.user.id
  const post = await db.post.create({
    data: {
      title,
      content,
      authorId: session.user.id,
    },
  })

  return post
}
```

---

## FastAPI - Protected Endpoints

### Basic Protection

```python
from fastapi import APIRouter

from app.auth.dependencies import CurrentUser, OptionalUser

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/me")
async def get_current_user(user: CurrentUser):
    """Get current authenticated user."""
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
    }


@router.get("/posts")
async def list_posts(user: OptionalUser):
    """List posts - personalized if authenticated."""
    if user:
        return {"posts": [], "personalized": True}
    return {"posts": [], "personalized": False}
```

### Role-Based Protection

```python
from typing import Annotated
from fastapi import Depends, HTTPException, status

from app.auth.dependencies import CurrentUser
from app.models.user import User


def require_role(*roles: str):
    """Dependency that requires user to have one of the specified roles."""
    async def role_checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {' or '.join(roles)}",
            )
        return user
    return role_checker


# Type aliases
AdminUser = Annotated[User, Depends(require_role("admin"))]
ModeratorUser = Annotated[User, Depends(require_role("admin", "moderator"))]


@router.get("/admin/users")
async def list_all_users(admin: AdminUser):
    """Admin only: List all users."""
    return {"users": []}


@router.delete("/posts/{post_id}")
async def delete_post(post_id: int, moderator: ModeratorUser):
    """Admin or Moderator: Delete a post."""
    return {"deleted": post_id}
```

### Router-Level Protection

```python
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user

# All routes require authentication
protected_router = APIRouter(
    prefix="/protected",
    tags=["protected"],
    dependencies=[Depends(get_current_user)],
)


@protected_router.get("/data")
async def get_data():
    """Already authenticated via router dependency."""
    return {"data": "secret"}


@protected_router.post("/action")
async def do_action():
    """Already authenticated via router dependency."""
    return {"success": True}
```

### Optional Authentication

```python
from app.auth.dependencies import OptionalUser


@router.get("/feed")
async def get_feed(user: OptionalUser):
    """
    Get feed - personalized if authenticated.
    Does not require authentication.
    """
    if user:
        # Return personalized feed
        return {"feed": [], "for_user": user.id}

    # Return public feed
    return {"feed": [], "public": True}
```

### Owner-Only Access

```python
from fastapi import HTTPException

from app.auth.dependencies import CurrentUser
from app.models.post import Post


@router.put("/posts/{post_id}")
async def update_post(
    post_id: int,
    user: CurrentUser,
    post_data: PostUpdate,
    db: SessionDep,
):
    """Update post - only owner can update."""
    post = await db.get(Post, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="Not your post")

    # Update post
    for key, value in post_data.model_dump(exclude_unset=True).items():
        setattr(post, key, value)

    await db.commit()
    return post
```

### Admin Override Pattern

```python
@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    user: CurrentUser,
    db: SessionDep,
):
    """Delete post - owner or admin."""
    post = await db.get(Post, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Allow owner or admin
    is_owner = post.author_id == user.id
    is_admin = user.role == "admin"

    if not (is_owner or is_admin):
        raise HTTPException(status_code=403, detail="Permission denied")

    await db.delete(post)
    await db.commit()

    return {"deleted": True}
```

## Common Patterns

### Redirect with Callback URL

```typescript
// Next.js middleware
const loginUrl = new URL("/login", request.url)
loginUrl.searchParams.set("callbackUrl", pathname)
return NextResponse.redirect(loginUrl)

// Login page - redirect after success
const callbackUrl = searchParams.get("callbackUrl") || "/dashboard"
await signIn.email({ email, password, callbackURL: callbackUrl })
```

### Show Different Content Based on Auth

```typescript
// Server Component
export default async function HomePage() {
  const session = await getOptionalSession()

  return (
    <div>
      {session ? (
        <LoggedInContent user={session.user} />
      ) : (
        <PublicContent />
      )}
    </div>
  )
}
```

### API Error Responses

```python
# FastAPI - consistent error responses
from fastapi import HTTPException, status

# 401 - Not authenticated
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)

# 403 - Authenticated but not authorized
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Insufficient permissions",
)

# 404 - Resource not found (don't leak existence)
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found",
)
```
