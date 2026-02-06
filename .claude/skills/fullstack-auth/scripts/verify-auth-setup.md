# Verify Auth Setup

## Overview

This script provides verification steps and tests to ensure the fullstack auth system is correctly configured.

## Quick Verification Checklist

```bash
# 1. Check environment variables
echo "Checking env vars..."
[ -z "$DATABASE_URL" ] && echo "ERROR: DATABASE_URL not set"
[ -z "$BETTER_AUTH_SECRET" ] && echo "ERROR: BETTER_AUTH_SECRET not set"

# 2. Test database connection
echo "Testing database..."
psql "$DATABASE_URL" -c "SELECT 1" > /dev/null && echo "OK: Database connected"

# 3. Check required tables
psql "$DATABASE_URL" -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
```

## Next.js Verification

### 1. Check Dependencies

```bash
# package.json should include:
npm list better-auth @neondatabase/serverless
```

### 2. Verify Auth Config

```typescript
// test/verify-auth.ts
import { auth } from "@/lib/auth"

async function verifyAuth() {
  console.log("Checking auth configuration...")

  // Check if auth is properly initialized
  if (!auth) {
    throw new Error("Auth not initialized")
  }

  // Check API methods exist
  const methods = ["getSession", "signIn", "signOut"]
  for (const method of methods) {
    if (typeof auth.api[method] !== "function") {
      throw new Error(`Missing auth method: ${method}`)
    }
  }

  console.log("Auth configuration OK")
}

verifyAuth().catch(console.error)
```

### 3. Test API Route

```bash
# Start dev server
npm run dev

# Test auth endpoint exists
curl -I http://localhost:3000/api/auth/session
# Should return 200 (with empty session) or redirect
```

### 4. Verify Middleware

```typescript
// Test middleware is working
// Visit a protected route without auth - should redirect to /login
// Visit /login while authenticated - should redirect to /dashboard
```

## FastAPI Verification

### 1. Check Dependencies

```bash
pip list | grep -E "sqlmodel|asyncpg|python-jose|passlib|pydantic-settings"
```

### 2. Database Connection Test

```python
# scripts/verify_db.py
import asyncio
from sqlalchemy import text
from app.core.db import engine


async def verify_database():
    """Verify database connection and tables."""
    print("Testing database connection...")

    async with engine.connect() as conn:
        # Test connection
        result = await conn.execute(text("SELECT 1"))
        print(f"Connection OK: {result.scalar()}")

        # Check tables
        result = await conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result]
        print(f"Tables found: {tables}")

        required = ["user", "session", "account", "verification"]
        missing = set(required) - set(tables)

        if missing:
            print(f"WARNING: Missing tables: {missing}")
            return False

        print("All required tables present")
        return True


if __name__ == "__main__":
    asyncio.run(verify_database())
```

### 3. Auth Dependencies Test

```python
# scripts/verify_auth.py
import asyncio
from datetime import datetime, timedelta, timezone

from app.auth.jwt import create_access_token, verify_token
from app.auth.utils import hash_password, verify_password


def test_jwt():
    """Test JWT creation and verification."""
    print("Testing JWT...")

    # Create token
    token = create_access_token({"sub": "test-user-id"})
    print(f"Token created: {token[:50]}...")

    # Verify token
    payload = verify_token(token)
    if not payload:
        raise Exception("Token verification failed")

    if payload.get("sub") != "test-user-id":
        raise Exception("Token payload mismatch")

    print("JWT OK")


def test_password():
    """Test password hashing."""
    print("Testing password hashing...")

    password = "test-password-123"
    hashed = hash_password(password)

    if not verify_password(password, hashed):
        raise Exception("Password verification failed")

    if verify_password("wrong-password", hashed):
        raise Exception("Wrong password should not verify")

    print("Password hashing OK")


if __name__ == "__main__":
    test_jwt()
    test_password()
    print("\nAll auth tests passed!")
```

### 4. API Endpoint Test

```bash
# Start FastAPI server
uvicorn app.main:app --reload

# Test health
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Test protected route (should fail with 401)
curl http://localhost:8000/api/me
# Expected: {"detail":"Not authenticated"}

# Test with invalid token
curl -H "Authorization: Bearer invalid-token" http://localhost:8000/api/me
# Expected: {"detail":"Not authenticated"}
```

## Integration Test

### End-to-End Auth Flow

```typescript
// test/e2e/auth.test.ts
import { expect, test } from "@playwright/test"

test.describe("Authentication Flow", () => {
  test("should redirect unauthenticated users to login", async ({ page }) => {
    await page.goto("/dashboard")
    await expect(page).toHaveURL(/\/login/)
  })

  test("should allow sign up with email", async ({ page }) => {
    await page.goto("/signup")
    await page.fill('input[name="name"]', "Test User")
    await page.fill('input[name="email"]', `test-${Date.now()}@example.com`)
    await page.fill('input[name="password"]', "password123")
    await page.click('button[type="submit"]')

    // Should redirect to dashboard after signup
    await expect(page).toHaveURL(/\/dashboard/)
  })

  test("should allow sign in with email", async ({ page }) => {
    await page.goto("/login")
    await page.fill('input[name="email"]', "existing@example.com")
    await page.fill('input[name="password"]', "password123")
    await page.click('button[type="submit"]')

    await expect(page).toHaveURL(/\/dashboard/)
  })

  test("should allow sign out", async ({ page }) => {
    // Login first
    await page.goto("/login")
    await page.fill('input[name="email"]', "existing@example.com")
    await page.fill('input[name="password"]', "password123")
    await page.click('button[type="submit"]')

    // Sign out
    await page.click('button:has-text("Sign Out")')
    await expect(page).toHaveURL(/\/login/)
  })
})
```

### Cross-Service Auth Test

```python
# scripts/test_cross_service.py
"""Test that FastAPI can validate sessions created by Better Auth."""
import asyncio
import httpx


async def test_session_sharing():
    """Test session sharing between Next.js and FastAPI."""

    async with httpx.AsyncClient() as client:
        # 1. Sign in via Next.js (get session cookie)
        login_response = await client.post(
            "http://localhost:3000/api/auth/sign-in/email",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return False

        # 2. Extract session cookie
        cookies = login_response.cookies
        session_cookie = cookies.get("better-auth.session_token")

        if not session_cookie:
            print("No session cookie received")
            return False

        print(f"Session cookie: {session_cookie[:20]}...")

        # 3. Use cookie with FastAPI
        fastapi_response = await client.get(
            "http://localhost:8000/api/me",
            cookies={"better-auth.session_token": session_cookie},
        )

        if fastapi_response.status_code != 200:
            print(f"FastAPI auth failed: {fastapi_response.text}")
            return False

        user_data = fastapi_response.json()
        print(f"User from FastAPI: {user_data}")

        return True


if __name__ == "__main__":
    result = asyncio.run(test_session_sharing())
    print(f"\nCross-service auth test: {'PASSED' if result else 'FAILED'}")
```

## Verification Report Template

```markdown
# Auth Setup Verification Report

Date: [DATE]
Project: [PROJECT_NAME]

## Environment
- [ ] DATABASE_URL configured
- [ ] BETTER_AUTH_SECRET configured (32+ chars)
- [ ] FRONTEND_URL configured
- [ ] OAuth credentials configured (if using)

## Database
- [ ] Connection successful
- [ ] user table exists
- [ ] session table exists
- [ ] account table exists
- [ ] verification table exists

## Next.js Frontend
- [ ] better-auth installed
- [ ] lib/auth.ts configured
- [ ] lib/auth-client.ts configured
- [ ] API route handler exists
- [ ] Middleware configured
- [ ] Login page works
- [ ] Sign up works
- [ ] Sign out works
- [ ] Protected routes redirect

## FastAPI Backend
- [ ] Dependencies installed
- [ ] JWT utilities work
- [ ] Password hashing works
- [ ] Auth dependencies work
- [ ] Protected routes return 401 without auth
- [ ] Protected routes work with valid token/session

## Integration
- [ ] Session created in Next.js works in FastAPI
- [ ] OAuth login creates user in database
- [ ] Session expiry works correctly

## Security
- [ ] Passwords are hashed (bcrypt)
- [ ] Tokens expire correctly
- [ ] HTTPS in production
- [ ] Secure cookies in production
- [ ] CORS configured correctly

## Notes
[Any issues or observations]
```

## Common Issues

### 1. Session Not Shared

```
Issue: FastAPI doesn't recognize session from Next.js
Fix: Ensure BETTER_AUTH_SECRET is identical in both services
```

### 2. Database Connection Failed

```
Issue: asyncpg connection error
Fix: Check DATABASE_URL format (postgresql+asyncpg://)
```

### 3. CORS Errors

```
Issue: Browser blocks requests to FastAPI
Fix: Add frontend URL to CORS allow_origins
```

### 4. Cookie Not Sent

```
Issue: Session cookie not sent to FastAPI
Fix: Ensure credentials: 'include' in fetch and CORS allow_credentials
```
