# Session Management

## Overview

Session management handles user authentication state across requests. Better Auth uses database-backed sessions with optional cookie caching for performance.

## Session Configuration

### Better Auth Session Settings

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  session: {
    // Session lifetime
    expiresIn: 60 * 60 * 24 * 7, // 7 days in seconds

    // How often to refresh session in database
    updateAge: 60 * 60 * 24, // Update every 24 hours

    // Cookie-based session caching (reduces DB queries)
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // Cache for 5 minutes
    },

    // Fresh session threshold (for sensitive operations)
    freshAge: 60 * 10, // 10 minutes
  },

  advanced: {
    // Cookie settings
    cookiePrefix: "better-auth",
    useSecureCookies: process.env.NODE_ENV === "production",

    // Cross-subdomain cookies
    // crossSubDomainCookies: {
    //   enabled: true,
    //   domain: ".yourdomain.com",
    // },
  },
})
```

## Session Types

### 1. Database Sessions (Default)

Sessions stored in database, validated on each request.

```sql
-- Session table structure
CREATE TABLE "session" (
  "id" TEXT PRIMARY KEY,
  "userId" TEXT NOT NULL REFERENCES "user"("id") ON DELETE CASCADE,
  "token" TEXT UNIQUE NOT NULL,
  "expiresAt" TIMESTAMP NOT NULL,
  "ipAddress" TEXT,
  "userAgent" TEXT,
  "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. JWT Sessions

For stateless authentication (useful for APIs).

```typescript
// lib/auth.ts
export const auth = betterAuth({
  session: {
    strategy: "jwt", // Use JWT instead of database sessions
    expiresIn: 60 * 60, // 1 hour
  },
})
```

## Getting Sessions

### Server Components

```typescript
// app/dashboard/page.tsx
import { auth } from "@/lib/auth"
import { headers } from "next/headers"

export default async function DashboardPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) {
    redirect("/login")
  }

  return <div>Welcome, {session.user.name}</div>
}
```

### Client Components

```typescript
"use client"

import { useSession } from "@/lib/auth-client"

export function UserMenu() {
  const { data: session, isPending, error, refetch } = useSession()

  if (isPending) return <div>Loading...</div>
  if (!session) return <div>Not logged in</div>

  return (
    <div>
      <span>{session.user.email}</span>
      <button onClick={() => refetch()}>Refresh</button>
    </div>
  )
}
```

### API Routes

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
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  return NextResponse.json({ user: session.user })
}
```

## Session Refresh

### Automatic Refresh

Better Auth automatically refreshes sessions based on `updateAge`.

### Manual Refresh

```typescript
"use client"

import { useSession } from "@/lib/auth-client"

export function SessionRefresh() {
  const { refetch } = useSession()

  // Refresh session data
  const handleRefresh = async () => {
    await refetch()
  }

  return <button onClick={handleRefresh}>Refresh Session</button>
}
```

## Session Invalidation

### Sign Out (Current Session)

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

  return <button onClick={handleSignOut}>Sign Out</button>
}
```

### Revoke All Sessions

```typescript
"use client"

import { authClient } from "@/lib/auth-client"

export function RevokeAllSessionsButton() {
  const handleRevokeAll = async () => {
    await authClient.revokeAllSessions()
  }

  return (
    <button onClick={handleRevokeAll} className="text-red-600">
      Sign Out All Devices
    </button>
  )
}
```

### List Active Sessions

```typescript
"use client"

import { authClient } from "@/lib/auth-client"
import { useEffect, useState } from "react"

interface Session {
  id: string
  createdAt: Date
  ipAddress: string | null
  userAgent: string | null
  current: boolean
}

export function ActiveSessions() {
  const [sessions, setSessions] = useState<Session[]>([])

  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    const { data } = await authClient.listSessions()
    setSessions(data || [])
  }

  const revokeSession = async (sessionId: string) => {
    await authClient.revokeSession({ id: sessionId })
    loadSessions()
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Active Sessions</h2>
      {sessions.map((session) => (
        <div
          key={session.id}
          className="flex justify-between items-center p-4 border rounded"
        >
          <div>
            <p className="font-medium">
              {session.current ? "Current Session" : "Other Session"}
            </p>
            <p className="text-sm text-gray-500">
              {session.userAgent || "Unknown device"}
            </p>
            <p className="text-sm text-gray-500">
              IP: {session.ipAddress || "Unknown"}
            </p>
          </div>
          {!session.current && (
            <button
              onClick={() => revokeSession(session.id)}
              className="text-red-600 hover:underline"
            >
              Revoke
            </button>
          )}
        </div>
      ))}
    </div>
  )
}
```

## FastAPI Session Validation

### Session Cookie Validation

```python
# app/auth/dependencies.py
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.models.session import Session as AuthSession
from app.models.user import User


async def get_user_from_session(
    db: Annotated[AsyncSession, Depends(get_session)],
    session_token: str | None = Cookie(
        default=None,
        alias="better-auth.session_token"
    ),
) -> User | None:
    """Validate Better Auth session cookie."""
    if not session_token:
        return None

    # Look up session in database
    result = await db.execute(
        select(AuthSession)
        .where(AuthSession.token == session_token)
        .where(AuthSession.expires_at > datetime.now(timezone.utc))
    )
    session = result.scalar_one_or_none()

    if not session:
        return None

    # Get user
    return await db.get(User, session.user_id)
```

### Session Cleanup

```python
# app/auth/tasks.py
from datetime import datetime, timezone

from sqlmodel import delete

from app.core.db import get_session_context
from app.models.session import Session


async def cleanup_expired_sessions():
    """Remove expired sessions from database."""
    async with get_session_context() as db:
        await db.execute(
            delete(Session).where(
                Session.expires_at < datetime.now(timezone.utc)
            )
        )
        await db.commit()


# Run periodically via scheduler (e.g., APScheduler, Celery)
```

## Fresh Session Requirement

For sensitive operations, require a fresh session (recently authenticated).

```typescript
// lib/auth-utils.ts
import { auth } from "@/lib/auth"
import { headers } from "next/headers"

export async function requireFreshSession() {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) {
    throw new Error("Not authenticated")
  }

  // Check if session is fresh (within 10 minutes of login)
  const freshAge = 10 * 60 * 1000 // 10 minutes in ms
  const sessionAge = Date.now() - new Date(session.session.createdAt).getTime()

  if (sessionAge > freshAge) {
    throw new Error("Session not fresh - please re-authenticate")
  }

  return session
}
```

```typescript
// Usage in sensitive operation
export async function changeEmailAction(newEmail: string) {
  const session = await requireFreshSession()

  // Proceed with email change
}
```

## Cross-Domain Sessions

For apps with multiple subdomains sharing auth.

```typescript
// lib/auth.ts
export const auth = betterAuth({
  advanced: {
    crossSubDomainCookies: {
      enabled: true,
      domain: ".yourdomain.com", // Share across *.yourdomain.com
    },
  },
})
```

## Session Security Best Practices

### 1. Secure Cookie Settings

```typescript
export const auth = betterAuth({
  advanced: {
    useSecureCookies: process.env.NODE_ENV === "production",
    // Cookies will have:
    // - Secure flag (HTTPS only)
    // - HttpOnly flag (no JS access)
    // - SameSite=Lax (CSRF protection)
  },
})
```

### 2. Session Binding

```typescript
// Bind session to IP/User-Agent for extra security
export const auth = betterAuth({
  session: {
    // Store IP and User-Agent with session
    // Check on validation
  },
})
```

### 3. Absolute Session Timeout

```typescript
// Force re-authentication after max lifetime
export const auth = betterAuth({
  session: {
    expiresIn: 60 * 60 * 24 * 7, // Max 7 days regardless of activity
  },
})
```

### 4. Concurrent Session Limits

```typescript
// app/api/auth/hooks.ts
// Limit number of active sessions per user

export const auth = betterAuth({
  // Use hooks to enforce session limits
  hooks: {
    after: {
      signIn: async ({ user, session }) => {
        // Check session count
        const sessions = await db.query.sessions.findMany({
          where: eq(sessions.userId, user.id),
        })

        // If more than 5, revoke oldest
        if (sessions.length > 5) {
          const oldest = sessions.sort(
            (a, b) => a.createdAt - b.createdAt
          )[0]
          await db.delete(sessions).where(eq(sessions.id, oldest.id))
        }
      },
    },
  },
})
```

## Troubleshooting

### Session Not Persisting

```typescript
// Check cookie settings
// 1. Ensure HTTPS in production
// 2. Check SameSite settings
// 3. Verify domain matches

// Debug session
const session = await auth.api.getSession({
  headers: await headers(),
})
console.log("Session:", session)
```

### Session Expired Unexpectedly

```typescript
// Check expiresIn configuration
// Verify server time is correct
// Check for timezone issues
```

### CORS Issues with Sessions

```typescript
// Ensure credentials are included
fetch("/api/protected", {
  credentials: "include", // Required for cookies
})

// FastAPI CORS
app.add_middleware(
  CORSMiddleware,
  allow_credentials=True,  // Required
  allow_origins=["http://localhost:3000"],
)
```

## Checklist

- [ ] Session expiration configured
- [ ] Cookie security settings correct
- [ ] Session refresh working
- [ ] Sign out invalidates session
- [ ] Expired sessions cleaned up
- [ ] Fresh session required for sensitive ops
- [ ] Session listing/management UI
- [ ] Cross-domain cookies (if needed)
