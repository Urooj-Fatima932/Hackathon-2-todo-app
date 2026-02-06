# Better Auth - Next.js Integration

## Server Components

### Getting Session

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
      <p>Email: {session.user.email}</p>
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
      <main>{children}</main>
    </div>
  )
}
```

## Client Components

### useSession Hook

```typescript
"use client"

import { useSession } from "@/lib/auth-client"

export function UserProfile() {
  const { data: session, isPending, error } = useSession()

  if (isPending) {
    return <div>Loading...</div>
  }

  if (error) {
    return <div>Error: {error.message}</div>
  }

  if (!session) {
    return <div>Not authenticated</div>
  }

  return (
    <div>
      <h2>{session.user.name}</h2>
      <p>{session.user.email}</p>
      {session.user.image && (
        <img src={session.user.image} alt={session.user.name || "User"} />
      )}
    </div>
  )
}
```

### Sign In Button

```typescript
"use client"

import { signIn } from "@/lib/auth-client"
import { useState } from "react"

export function SignInButton() {
  const [loading, setLoading] = useState(false)

  const handleGitHubSignIn = async () => {
    setLoading(true)
    await signIn.social({
      provider: "github",
      callbackURL: "/dashboard",
    })
  }

  const handleGoogleSignIn = async () => {
    setLoading(true)
    await signIn.social({
      provider: "google",
      callbackURL: "/dashboard",
    })
  }

  return (
    <div className="space-y-2">
      <button
        onClick={handleGitHubSignIn}
        disabled={loading}
        className="w-full px-4 py-2 bg-gray-900 text-white rounded"
      >
        {loading ? "Loading..." : "Continue with GitHub"}
      </button>
      <button
        onClick={handleGoogleSignIn}
        disabled={loading}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded"
      >
        {loading ? "Loading..." : "Continue with Google"}
      </button>
    </div>
  )
}
```

### Sign Out Button

```typescript
"use client"

import { signOut } from "@/lib/auth-client"
import { useRouter } from "next/navigation"

export function SignOutButton() {
  const router = useRouter()

  const handleSignOut = async () => {
    await signOut({
      fetchOptions: {
        onSuccess: () => {
          router.push("/login")
          router.refresh()
        },
      },
    })
  }

  return (
    <button
      onClick={handleSignOut}
      className="px-4 py-2 bg-red-600 text-white rounded"
    >
      Sign Out
    </button>
  )
}
```

## Email/Password Forms

### Sign Up Form

```typescript
"use client"

import { signUp } from "@/lib/auth-client"
import { useRouter } from "next/navigation"
import { useState } from "react"

export function SignUpForm() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    const formData = new FormData(e.currentTarget)
    const email = formData.get("email") as string
    const password = formData.get("password") as string
    const name = formData.get("name") as string

    const { error } = await signUp.email({
      email,
      password,
      name,
      callbackURL: "/dashboard",
    })

    if (error) {
      setError(error.message)
      setLoading(false)
    } else {
      router.push("/dashboard")
      router.refresh()
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-3 bg-red-100 text-red-700 rounded">{error}</div>
      )}

      <div>
        <label htmlFor="name" className="block text-sm font-medium">
          Name
        </label>
        <input
          id="name"
          name="name"
          type="text"
          required
          className="mt-1 w-full px-3 py-2 border rounded"
        />
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium">
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          required
          className="mt-1 w-full px-3 py-2 border rounded"
        />
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium">
          Password
        </label>
        <input
          id="password"
          name="password"
          type="password"
          required
          minLength={8}
          className="mt-1 w-full px-3 py-2 border rounded"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
      >
        {loading ? "Creating account..." : "Sign Up"}
      </button>
    </form>
  )
}
```

### Sign In Form

```typescript
"use client"

import { signIn } from "@/lib/auth-client"
import { useRouter } from "next/navigation"
import { useState } from "react"

export function SignInForm() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    const formData = new FormData(e.currentTarget)
    const email = formData.get("email") as string
    const password = formData.get("password") as string

    const { error } = await signIn.email({
      email,
      password,
      callbackURL: "/dashboard",
    })

    if (error) {
      setError(error.message)
      setLoading(false)
    } else {
      router.push("/dashboard")
      router.refresh()
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-3 bg-red-100 text-red-700 rounded">{error}</div>
      )}

      <div>
        <label htmlFor="email" className="block text-sm font-medium">
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          required
          className="mt-1 w-full px-3 py-2 border rounded"
        />
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium">
          Password
        </label>
        <input
          id="password"
          name="password"
          type="password"
          required
          className="mt-1 w-full px-3 py-2 border rounded"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
      >
        {loading ? "Signing in..." : "Sign In"}
      </button>
    </form>
  )
}
```

## Middleware

### Basic Route Protection

```typescript
// middleware.ts
import { auth } from "@/lib/auth"
import { NextRequest, NextResponse } from "next/server"

export async function middleware(request: NextRequest) {
  const session = await auth.api.getSession({
    headers: request.headers,
  })

  const { pathname } = request.nextUrl

  // Protected routes
  const protectedRoutes = ["/dashboard", "/settings", "/profile"]
  const isProtectedRoute = protectedRoutes.some((route) =>
    pathname.startsWith(route)
  )

  // Auth routes (login, signup)
  const authRoutes = ["/login", "/signup"]
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

### Role-Based Protection

```typescript
// middleware.ts
import { auth } from "@/lib/auth"
import { NextRequest, NextResponse } from "next/server"

export async function middleware(request: NextRequest) {
  const session = await auth.api.getSession({
    headers: request.headers,
  })

  const { pathname } = request.nextUrl

  // Admin routes require admin role
  if (pathname.startsWith("/admin")) {
    if (!session) {
      return NextResponse.redirect(new URL("/login", request.url))
    }

    // Check for admin role (assumes role is stored on user)
    // Customize based on your user model
    if (session.user.role !== "admin") {
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

## Login Page Example

```typescript
// app/login/page.tsx
import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { redirect } from "next/navigation"
import { SignInForm } from "@/components/sign-in-form"
import { SignInButton } from "@/components/sign-in-button"

export default async function LoginPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (session) {
    redirect("/dashboard")
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-full max-w-md p-8 space-y-6">
        <h1 className="text-2xl font-bold text-center">Sign In</h1>

        {/* OAuth Providers */}
        <SignInButton />

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">
              Or continue with email
            </span>
          </div>
        </div>

        {/* Email/Password Form */}
        <SignInForm />

        <p className="text-center text-sm text-gray-600">
          Don't have an account?{" "}
          <a href="/signup" className="text-blue-600 hover:underline">
            Sign up
          </a>
        </p>
      </div>
    </div>
  )
}
```

## User Menu Component

```typescript
"use client"

import { useSession, signOut } from "@/lib/auth-client"
import { useRouter } from "next/navigation"
import { useState, useRef, useEffect } from "react"

export function UserMenu() {
  const { data: session } = useSession()
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  if (!session) return null

  const handleSignOut = async () => {
    await signOut({
      fetchOptions: {
        onSuccess: () => {
          router.push("/")
          router.refresh()
        },
      },
    })
  }

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center space-x-2"
      >
        {session.user.image ? (
          <img
            src={session.user.image}
            alt=""
            className="w-8 h-8 rounded-full"
          />
        ) : (
          <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
            {session.user.name?.[0] || session.user.email?.[0]}
          </div>
        )}
        <span className="hidden md:inline">{session.user.name}</span>
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border">
          <div className="p-3 border-b">
            <p className="font-medium">{session.user.name}</p>
            <p className="text-sm text-gray-500">{session.user.email}</p>
          </div>
          <a
            href="/settings"
            className="block px-4 py-2 hover:bg-gray-100"
          >
            Settings
          </a>
          <button
            onClick={handleSignOut}
            className="w-full text-left px-4 py-2 hover:bg-gray-100 text-red-600"
          >
            Sign Out
          </button>
        </div>
      )}
    </div>
  )
}
```

## API Routes

### Get Current User

```typescript
// app/api/user/route.ts
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

  return NextResponse.json({ user: session.user })
}
```

### Protected API Route

```typescript
// app/api/protected/route.ts
import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { NextResponse } from "next/server"

export async function POST(request: Request) {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
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

## Type Definitions

```typescript
// types/auth.d.ts
import { Session, User } from "@/lib/auth"

declare module "@/lib/auth-client" {
  interface Session {
    user: User & {
      role?: string
      // Add custom user fields
    }
  }
}
```
