---
name: fullstack-auth
description: |
  Implements authentication for full-stack apps with Next.js frontend and FastAPI backend.
  Uses Better Auth for unified authentication, SQLModel for type-safe database models,
  and Neon PostgreSQL for serverless database storage.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

# Fullstack Auth

Implement unified authentication across Next.js frontend and FastAPI backend using Better Auth with SQLModel and Neon DB.

## What This Skill Does

- Sets up Better Auth for unified frontend/backend authentication
- Implements SQLModel for type-safe database models in FastAPI
- Configures OAuth providers (Google, GitHub, Discord, etc.)
- Creates protected routes (frontend and backend)
- Stores users/sessions in Neon PostgreSQL
- Syncs authentication seamlessly between frontend and backend

## What This Skill Does NOT Do

- Implement authorization/RBAC (separate concern)
- Handle payment/subscription gating
- Create custom OAuth providers
- Manage multi-tenancy
- Implement Two-Factor Authentication (2FA/MFA)
- Handle magic link authentication

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing auth setup, .env files, database schema |
| **Conversation** | Auth providers needed, session strategy, protected routes |
| **Skill References** | Auth patterns from `references/` |
| **User Guidelines** | Security requirements, user model fields |

---

## Clarifications (Ask User)

Ask before generating:

1. **Auth providers?** - Google, GitHub, email/password, or multiple?
2. **Session strategy?** - Cookie-based sessions or JWT tokens?
3. **User fields?** - Additional fields beyond email/name?
4. **Protected routes?** - Which routes require authentication?

---

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js App   │────▶│    FastAPI      │────▶│    Neon DB      │
│  (Better Auth)  │     │  (Better Auth)  │     │   (PostgreSQL)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │  1. OAuth/Credentials │                       │
        │  2. Create Session    │                       │
        │  3. Shared Session    │                       │
        └──────────────────────▶│  4. Validate Session  │
                                │  5. Query User        │
                                └──────────────────────▶│
```

## Why Better Auth + SQLModel?

| Aspect | Benefit |
|--------|---------|
| **Unified Auth** | Single auth system for frontend + backend |
| **Type Safety** | SQLModel = SQLAlchemy + Pydantic in one |
| **Less Boilerplate** | No separate schemas, automatic validation |
| **Framework Agnostic** | Better Auth works across any framework |
| **Modern Stack** | Built for serverless, edge-ready |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14+ (App Router) |
| **Frontend Auth** | Better Auth (client) |
| **Backend** | FastAPI |
| **Backend Auth** | Better Auth (server) + JWT validation |
| **ORM** | SQLModel (async) |
| **Database** | Neon PostgreSQL (serverless) |

---

## Generation Process

```
Check existing setup → Configure Better Auth → Set up SQLModel → Create protected routes
```

### Step 1: Check Existing Setup

```
# Find existing auth
Glob: **/auth.ts, **/auth.config.ts, **/**/auth/**

# Check for Better Auth
Grep: "better-auth" in package.json

# Find user model
Grep: "class User|model User" in *.py
```

### Step 2: Install Dependencies

**Next.js:**
```bash
npm install better-auth
```

**FastAPI:**
```bash
pip install sqlmodel asyncpg python-jose[cryptography] passlib[bcrypt] pydantic-settings
```

### Step 3: Generate Files

| Component | Files |
|-----------|-------|
| Better Auth config | `lib/auth.ts`, `lib/auth-client.ts` |
| Next.js API route | `app/api/auth/[...all]/route.ts` |
| Next.js middleware | `middleware.ts` |
| FastAPI auth | `app/auth/`, `app/core/deps.py` |
| SQLModel models | `app/models/user.py`, `app/models/session.py` |
| Database setup | `app/core/db.py` |

---

## Project Structure

### Next.js (Frontend)
```
├── lib/
│   ├── auth.ts                    # Better Auth server config
│   └── auth-client.ts             # Better Auth client
├── app/
│   ├── api/auth/[...all]/
│   │   └── route.ts               # Auth API handler
│   ├── login/
│   │   └── page.tsx               # Login page
│   └── (protected)/               # Protected route group
│       └── dashboard/
│           └── page.tsx
├── middleware.ts                   # Route protection
└── components/
    ├── sign-in-button.tsx
    └── user-menu.tsx
```

### FastAPI (Backend)
```
app/
├── core/
│   ├── config.py                  # Settings
│   ├── db.py                      # SQLModel + Neon setup
│   └── deps.py                    # Dependencies
├── auth/
│   ├── __init__.py
│   ├── router.py                  # Auth endpoints
│   ├── jwt.py                     # JWT utilities
│   └── dependencies.py            # Auth dependencies
├── models/
│   ├── user.py                    # User model
│   ├── session.py                 # Session model
│   └── account.py                 # OAuth account model
└── main.py
```

---

## Standards

| Standard | Implementation |
|----------|----------------|
| **Passwords** | bcrypt hash, never store plain |
| **JWT secrets** | 32+ char random string, env var |
| **Token expiry** | Access: 15-30min, Refresh: 7 days |
| **HTTPS only** | Secure cookies in production |
| **CSRF protection** | Built into Better Auth |

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/better-auth-setup.md` | Core Better Auth configuration |
| `references/better-auth-nextjs.md` | Next.js App Router integration |
| `references/better-auth-fastapi.md` | FastAPI integration patterns |
| `references/better-auth-providers.md` | OAuth provider setup |
| `references/sqlmodel-setup.md` | SQLModel + Neon configuration |
| `references/sqlmodel-models.md` | User, Session, Account models |
| `references/protected-routes.md` | Route protection patterns |
| `references/email-verification.md` | Email verification flow |
| `references/password-reset.md` | Password reset flow |
| `references/session-management.md` | Session handling patterns |
| `references/error-handling.md` | Auth error handling |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/init-nextjs-auth.md` | Initialize Better Auth in Next.js |
| `scripts/init-fastapi-auth.md` | Initialize auth in FastAPI backend |
| `scripts/init-db-migration.md` | Database migration setup |
| `scripts/verify-auth-setup.md` | Verify auth configuration |
| `scripts/generate-env.md` | Generate environment variables |

---

## Quick Patterns

### Better Auth Server Config
```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"
import { Pool } from "@neondatabase/serverless"

export const auth = betterAuth({
  database: new Pool({ connectionString: process.env.DATABASE_URL }),
  emailAndPassword: { enabled: true },
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
})
```

### Better Auth Client
```typescript
// lib/auth-client.ts
import { createAuthClient } from "better-auth/react"

export const { signIn, signUp, signOut, useSession } = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
})
```

### Protected Server Component
```typescript
import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { redirect } from "next/navigation"

export default async function ProtectedPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) redirect("/login")

  return <div>Welcome {session.user.name}</div>
}
```

### SQLModel User
```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str | None = None
    email_verified: bool = Field(default=False)
    image: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### FastAPI Auth Dependency
```python
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt import verify_token
from app.models.user import User
from app.core.deps import get_session

security = HTTPBearer()

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: AsyncSession = Depends(get_session),
) -> User:
    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = await session.get(User, payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

CurrentUser = Annotated[User, Depends(get_current_user)]
```

---

## Environment Variables

```bash
# .env.local (Next.js)
NEXT_PUBLIC_APP_URL="http://localhost:3000"
BETTER_AUTH_SECRET="your-random-32-char-secret"
DATABASE_URL="postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require"

# OAuth Providers
GITHUB_ID="your-github-client-id"
GITHUB_SECRET="your-github-client-secret"
GOOGLE_ID="your-google-client-id"
GOOGLE_SECRET="your-google-client-secret"

# .env (FastAPI)
DATABASE_URL="postgresql+asyncpg://user:pass@ep-xxx.neon.tech/dbname?sslmode=require"
DIRECT_URL="postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require"
JWT_SECRET_KEY="your-jwt-secret-min-32-chars"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Edge Cases & Considerations

### Session Handling
- **Concurrent sessions**: User logged in on multiple devices
- **Session invalidation**: Sign out should invalidate all or current session
- **Token refresh race conditions**: Multiple requests refreshing token simultaneously
- **Cross-subdomain cookies**: Sharing auth across app.example.com and api.example.com

### Security
- **Timing attacks**: Use constant-time comparison for tokens/passwords
- **User enumeration**: Don't reveal if email exists during login/reset
- **Rate limiting**: Protect login, signup, and password reset endpoints
- **Session fixation**: Generate new session ID after login

### Error Scenarios
- **Database connection failures**: Graceful degradation
- **OAuth provider errors**: Handle provider downtime
- **Token expiration mid-request**: Handle gracefully on frontend
- **CORS issues**: Ensure credentials included in cross-origin requests

---

## Testing Patterns

### Unit Tests (FastAPI)
```python
import pytest
from app.auth.utils import hash_password, verify_password
from app.auth.jwt import create_access_token, verify_token

def test_password_hashing():
    password = "test-password"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)

def test_jwt_creation():
    token = create_access_token({"sub": "user-id"})
    payload = verify_token(token)
    assert payload["sub"] == "user-id"
```

### Integration Tests (Next.js)
```typescript
// __tests__/auth.test.ts
import { auth } from "@/lib/auth"

describe("Auth", () => {
  it("should create session on sign in", async () => {
    // Test auth flow
  })

  it("should invalidate session on sign out", async () => {
    // Test sign out
  })
})
```

### E2E Tests (Playwright)
```typescript
test("complete auth flow", async ({ page }) => {
  // Sign up
  await page.goto("/signup")
  await page.fill('[name="email"]', "test@example.com")
  await page.fill('[name="password"]', "password123")
  await page.click('button[type="submit"]')

  // Verify redirected to dashboard
  await expect(page).toHaveURL("/dashboard")

  // Sign out
  await page.click('button:has-text("Sign Out")')
  await expect(page).toHaveURL("/login")
})
```

---

## Checklist

Before completing, verify:

- [ ] Better Auth configured with providers
- [ ] SQLModel models created for User, Session, Account
- [ ] Neon DB connection working (pooled + direct)
- [ ] Next.js middleware protects routes
- [ ] FastAPI JWT validation works
- [ ] Passwords hashed with bcrypt
- [ ] Secrets in environment variables
- [ ] CSRF protection enabled
- [ ] Secure cookies in production
- [ ] Email verification flow (if required)
- [ ] Password reset flow (if required)
- [ ] Error handling covers all auth scenarios
- [ ] Rate limiting on auth endpoints
- [ ] Session management UI (list/revoke sessions)
