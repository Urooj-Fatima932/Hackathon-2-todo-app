# Initialize Better Auth in Next.js

## Installation

```bash
npm install better-auth @neondatabase/serverless
```

## Environment Variables

```bash
# .env.local

# App URL
NEXT_PUBLIC_APP_URL="http://localhost:3000"

# Better Auth Secret (generate: openssl rand -base64 32)
BETTER_AUTH_SECRET="your-random-32-character-secret-key"

# Database (Neon)
DATABASE_URL="postgresql://user:password@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require"

# OAuth Providers (optional)
GITHUB_ID="your-github-client-id"
GITHUB_SECRET="your-github-client-secret"
GOOGLE_ID="your-google-client-id"
GOOGLE_SECRET="your-google-client-secret"
```

## Auth Server Configuration

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"
import { Pool } from "@neondatabase/serverless"

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),

  // Email/password auth
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },

  // OAuth providers
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
    },
    google: {
      clientId: process.env.GOOGLE_ID!,
      clientSecret: process.env.GOOGLE_SECRET!,
    },
  },

  // Session config
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update every 24 hours
  },
})

// Export types
export type Session = typeof auth.$Infer.Session
export type User = typeof auth.$Infer.Session.user
```

## Auth Client

```typescript
// lib/auth-client.ts
import { createAuthClient } from "better-auth/react"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
})

export const {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession,
} = authClient
```

## API Route Handler

```typescript
// app/api/auth/[...all]/route.ts
import { auth } from "@/lib/auth"
import { toNextJsHandler } from "better-auth/next-js"

export const { GET, POST } = toNextJsHandler(auth)
```

## Middleware

```typescript
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
  if (protectedRoutes.some((r) => pathname.startsWith(r)) && !session) {
    const url = new URL("/login", request.url)
    url.searchParams.set("callbackUrl", pathname)
    return NextResponse.redirect(url)
  }

  // Redirect authenticated users from auth pages
  if (authRoutes.some((r) => pathname.startsWith(r)) && session) {
    return NextResponse.redirect(new URL("/dashboard", request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
}
```

## Login Page

```typescript
// app/login/page.tsx
import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { redirect } from "next/navigation"
import { LoginForm } from "@/components/auth/login-form"

export default async function LoginPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (session) {
    redirect("/dashboard")
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md space-y-6 p-8">
        <h1 className="text-2xl font-bold text-center">Sign In</h1>
        <LoginForm />
      </div>
    </div>
  )
}
```

## Login Form Component

```typescript
// components/auth/login-form.tsx
"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { signIn } from "@/lib/auth-client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export function LoginForm() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleEmailSignIn = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    const formData = new FormData(e.currentTarget)

    const { error } = await signIn.email({
      email: formData.get("email") as string,
      password: formData.get("password") as string,
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

  const handleOAuthSignIn = async (provider: "github" | "google") => {
    setLoading(true)
    await signIn.social({
      provider,
      callbackURL: "/dashboard",
    })
  }

  return (
    <div className="space-y-4">
      {/* OAuth Buttons */}
      <div className="space-y-2">
        <Button
          variant="outline"
          className="w-full"
          onClick={() => handleOAuthSignIn("github")}
          disabled={loading}
        >
          Continue with GitHub
        </Button>
        <Button
          variant="outline"
          className="w-full"
          onClick={() => handleOAuthSignIn("google")}
          disabled={loading}
        >
          Continue with Google
        </Button>
      </div>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="bg-background px-2 text-muted-foreground">
            Or continue with email
          </span>
        </div>
      </div>

      {/* Email/Password Form */}
      <form onSubmit={handleEmailSignIn} className="space-y-4">
        {error && (
          <div className="text-sm text-red-500 bg-red-50 p-3 rounded">
            {error}
          </div>
        )}

        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input id="email" name="email" type="email" required />
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input id="password" name="password" type="password" required />
        </div>

        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? "Signing in..." : "Sign In"}
        </Button>
      </form>

      <p className="text-center text-sm">
        Don't have an account?{" "}
        <a href="/signup" className="text-primary hover:underline">
          Sign up
        </a>
      </p>
    </div>
  )
}
```

## Sign Up Form Component

```typescript
// components/auth/signup-form.tsx
"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { signUp } from "@/lib/auth-client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export function SignUpForm() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    const formData = new FormData(e.currentTarget)

    const { error } = await signUp.email({
      email: formData.get("email") as string,
      password: formData.get("password") as string,
      name: formData.get("name") as string,
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
        <div className="text-sm text-red-500 bg-red-50 p-3 rounded">
          {error}
        </div>
      )}

      <div className="space-y-2">
        <Label htmlFor="name">Name</Label>
        <Input id="name" name="name" type="text" required />
      </div>

      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input id="email" name="email" type="email" required />
      </div>

      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>
        <Input id="password" name="password" type="password" required minLength={8} />
      </div>

      <Button type="submit" className="w-full" disabled={loading}>
        {loading ? "Creating account..." : "Sign Up"}
      </Button>
    </form>
  )
}
```

## Sign Out Button

```typescript
// components/auth/sign-out-button.tsx
"use client"

import { signOut } from "@/lib/auth-client"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"

export function SignOutButton() {
  const router = useRouter()

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
    <Button variant="ghost" onClick={handleSignOut}>
      Sign Out
    </Button>
  )
}
```

## Getting Session in Server Components

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
      <p>Welcome, {session.user.name}!</p>
      <p>Email: {session.user.email}</p>
    </div>
  )
}
```

## Using Session in Client Components

```typescript
// components/user-menu.tsx
"use client"

import { useSession } from "@/lib/auth-client"
import { SignOutButton } from "./auth/sign-out-button"

export function UserMenu() {
  const { data: session, isPending } = useSession()

  if (isPending) return <div>Loading...</div>
  if (!session) return null

  return (
    <div className="flex items-center gap-4">
      <span>{session.user.name}</span>
      <SignOutButton />
    </div>
  )
}
```

## Verify Setup

1. Start the dev server: `npm run dev`
2. Visit `/login` - should see login form
3. Create an account at `/signup`
4. Check that session works at `/dashboard`
5. Test sign out functionality
