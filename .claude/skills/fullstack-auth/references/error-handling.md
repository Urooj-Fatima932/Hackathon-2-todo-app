# Auth Error Handling

## Overview

Proper error handling in authentication flows is critical for security and user experience. This guide covers error patterns for both Next.js and FastAPI.

## Error Types

### Authentication Errors

| Error | Code | Description |
|-------|------|-------------|
| `INVALID_CREDENTIALS` | 401 | Wrong email/password |
| `USER_NOT_FOUND` | 401 | No user with that email |
| `ACCOUNT_LOCKED` | 403 | Too many failed attempts |
| `EMAIL_NOT_VERIFIED` | 403 | Email verification required |
| `SESSION_EXPIRED` | 401 | Session has expired |
| `INVALID_TOKEN` | 401 | Token is invalid or expired |

### Authorization Errors

| Error | Code | Description |
|-------|------|-------------|
| `UNAUTHORIZED` | 401 | Not authenticated |
| `FORBIDDEN` | 403 | Authenticated but not allowed |
| `INSUFFICIENT_ROLE` | 403 | Missing required role |

### Validation Errors

| Error | Code | Description |
|-------|------|-------------|
| `INVALID_EMAIL` | 400 | Email format invalid |
| `WEAK_PASSWORD` | 400 | Password doesn't meet requirements |
| `EMAIL_TAKEN` | 409 | Email already registered |
| `RATE_LIMITED` | 429 | Too many requests |

## Next.js Error Handling

### Client-Side Error Handling

```typescript
"use client"

import { signIn, signUp } from "@/lib/auth-client"
import { useState } from "react"

// Error message mapping
const errorMessages: Record<string, string> = {
  INVALID_CREDENTIALS: "Invalid email or password",
  USER_NOT_FOUND: "No account found with this email",
  EMAIL_NOT_VERIFIED: "Please verify your email first",
  EMAIL_TAKEN: "An account with this email already exists",
  WEAK_PASSWORD: "Password is too weak",
  RATE_LIMITED: "Too many attempts. Please try again later.",
  UNKNOWN: "Something went wrong. Please try again.",
}

function getErrorMessage(error: { code?: string; message?: string }): string {
  if (error.code && errorMessages[error.code]) {
    return errorMessages[error.code]
  }
  return error.message || errorMessages.UNKNOWN
}

export function LoginForm() {
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)

    const formData = new FormData(e.currentTarget)

    const { error } = await signIn.email({
      email: formData.get("email") as string,
      password: formData.get("password") as string,
    })

    if (error) {
      setError(getErrorMessage(error))
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div
          role="alert"
          className="p-3 mb-4 text-sm text-red-700 bg-red-100 rounded"
        >
          {error}
        </div>
      )}
      {/* Form fields */}
    </form>
  )
}
```

### Error Component

```typescript
// components/auth/auth-error.tsx
"use client"

interface AuthErrorProps {
  error: string | null
  onDismiss?: () => void
}

export function AuthError({ error, onDismiss }: AuthErrorProps) {
  if (!error) return null

  return (
    <div
      role="alert"
      className="flex items-center justify-between p-4 mb-4 text-red-700 bg-red-50 border border-red-200 rounded-lg"
    >
      <div className="flex items-center gap-2">
        <svg
          className="w-5 h-5"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
            clipRule="evenodd"
          />
        </svg>
        <span>{error}</span>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-red-500 hover:text-red-700"
          aria-label="Dismiss"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      )}
    </div>
  )
}
```

### Server-Side Error Handling

```typescript
// app/api/protected/route.ts
import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { NextResponse } from "next/server"

export async function GET() {
  try {
    const session = await auth.api.getSession({
      headers: await headers(),
    })

    if (!session) {
      return NextResponse.json(
        { error: "Unauthorized", code: "UNAUTHORIZED" },
        { status: 401 }
      )
    }

    // Check email verification
    if (!session.user.emailVerified) {
      return NextResponse.json(
        { error: "Email not verified", code: "EMAIL_NOT_VERIFIED" },
        { status: 403 }
      )
    }

    return NextResponse.json({ data: "Protected data" })
  } catch (error) {
    console.error("Auth error:", error)

    return NextResponse.json(
      { error: "Internal server error", code: "INTERNAL_ERROR" },
      { status: 500 }
    )
  }
}
```

### Middleware Error Handling

```typescript
// middleware.ts
import { auth } from "@/lib/auth"
import { NextRequest, NextResponse } from "next/server"

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  try {
    const session = await auth.api.getSession({
      headers: request.headers,
    })

    // Protected routes
    if (pathname.startsWith("/dashboard") && !session) {
      const loginUrl = new URL("/login", request.url)
      loginUrl.searchParams.set("error", "SESSION_REQUIRED")
      loginUrl.searchParams.set("callbackUrl", pathname)
      return NextResponse.redirect(loginUrl)
    }

    return NextResponse.next()
  } catch (error) {
    console.error("Middleware auth error:", error)

    // On error, redirect to login with error
    if (pathname.startsWith("/dashboard")) {
      const loginUrl = new URL("/login", request.url)
      loginUrl.searchParams.set("error", "AUTH_ERROR")
      return NextResponse.redirect(loginUrl)
    }

    return NextResponse.next()
  }
}
```

### Display URL Errors

```typescript
// app/login/page.tsx
import { LoginForm } from "@/components/auth/login-form"

interface Props {
  searchParams: Promise<{ error?: string; callbackUrl?: string }>
}

const urlErrorMessages: Record<string, string> = {
  SESSION_REQUIRED: "Please sign in to access this page",
  SESSION_EXPIRED: "Your session has expired. Please sign in again.",
  AUTH_ERROR: "An authentication error occurred. Please try again.",
}

export default async function LoginPage({ searchParams }: Props) {
  const { error, callbackUrl } = await searchParams
  const urlError = error ? urlErrorMessages[error] : null

  return (
    <div>
      {urlError && (
        <div className="p-4 mb-4 text-amber-700 bg-amber-50 rounded">
          {urlError}
        </div>
      )}
      <LoginForm callbackUrl={callbackUrl} />
    </div>
  )
}
```

## FastAPI Error Handling

### Custom Exceptions

```python
# app/auth/exceptions.py
from fastapi import HTTPException, status


class AuthException(HTTPException):
    """Base authentication exception."""

    def __init__(
        self,
        detail: str,
        code: str,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
    ):
        super().__init__(
            status_code=status_code,
            detail={"message": detail, "code": code},
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidCredentialsError(AuthException):
    def __init__(self):
        super().__init__(
            detail="Invalid email or password",
            code="INVALID_CREDENTIALS",
        )


class UserNotFoundError(AuthException):
    def __init__(self):
        super().__init__(
            detail="User not found",
            code="USER_NOT_FOUND",
        )


class EmailNotVerifiedError(AuthException):
    def __init__(self):
        super().__init__(
            detail="Email not verified",
            code="EMAIL_NOT_VERIFIED",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class SessionExpiredError(AuthException):
    def __init__(self):
        super().__init__(
            detail="Session has expired",
            code="SESSION_EXPIRED",
        )


class InsufficientRoleError(AuthException):
    def __init__(self, required_role: str):
        super().__init__(
            detail=f"Requires {required_role} role",
            code="INSUFFICIENT_ROLE",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class RateLimitedError(AuthException):
    def __init__(self):
        super().__init__(
            detail="Too many requests. Please try again later.",
            code="RATE_LIMITED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )
```

### Global Exception Handler

```python
# app/core/exceptions.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request, exc: SQLAlchemyError
    ):
        # Log the error
        import logging
        logging.error(f"Database error: {exc}")

        return JSONResponse(
            status_code=500,
            content={
                "message": "Database error occurred",
                "code": "DATABASE_ERROR",
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        # Log the error
        import logging
        logging.error(f"Unhandled error: {exc}")

        return JSONResponse(
            status_code=500,
            content={
                "message": "An unexpected error occurred",
                "code": "INTERNAL_ERROR",
            },
        )
```

### Auth Dependencies with Error Handling

```python
# app/auth/dependencies.py
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth.exceptions import (
    EmailNotVerifiedError,
    SessionExpiredError,
    InsufficientRoleError,
)
from app.auth.jwt import verify_token
from app.core.db import get_session
from app.models.session import Session as AuthSession
from app.models.user import User

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_session)],
    session_token: str | None = Cookie(
        default=None, alias="better-auth.session_token"
    ),
) -> User:
    """Get current user with detailed error handling."""
    user = None

    # Try JWT token first
    if credentials:
        payload = verify_token(credentials.credentials)
        if payload:
            user_id = payload.get("sub")
            if user_id:
                user = await db.get(User, user_id)

    # Try session cookie
    if not user and session_token:
        result = await db.execute(
            select(AuthSession).where(AuthSession.token == session_token)
        )
        session = result.scalar_one_or_none()

        if session:
            if session.expires_at < datetime.now(timezone.utc):
                raise SessionExpiredError()
            user = await db.get(User, session.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Not authenticated", "code": "UNAUTHORIZED"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def require_verified_email(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Require verified email."""
    if not user.email_verified:
        raise EmailNotVerifiedError()
    return user


def require_role(*roles: str):
    """Factory for role requirement dependency."""

    async def role_checker(
        user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if user.role not in roles:
            raise InsufficientRoleError(", ".join(roles))
        return user

    return role_checker


# Type aliases
CurrentUser = Annotated[User, Depends(get_current_user)]
VerifiedUser = Annotated[User, Depends(require_verified_email)]
AdminUser = Annotated[User, Depends(require_role("admin"))]
```

### Error Response Schema

```python
# app/schemas/error.py
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    message: str
    code: str
    details: dict | None = None

    model_config = {"json_schema_extra": {"example": {
        "message": "Invalid credentials",
        "code": "INVALID_CREDENTIALS",
        "details": None,
    }}}


class ValidationErrorResponse(BaseModel):
    """Validation error response schema."""

    message: str
    code: str = "VALIDATION_ERROR"
    errors: list[dict]

    model_config = {"json_schema_extra": {"example": {
        "message": "Validation failed",
        "code": "VALIDATION_ERROR",
        "errors": [
            {"field": "email", "message": "Invalid email format"},
            {"field": "password", "message": "Password too short"},
        ],
    }}}
```

### Route with Error Responses

```python
# app/api/routes/auth.py
from fastapi import APIRouter

from app.auth.dependencies import CurrentUser
from app.schemas.error import ErrorResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get(
    "/me",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Email not verified"},
    },
)
async def get_me(user: CurrentUser):
    """Get current user info."""
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
    }
```

## Error Logging

### Structured Logging

```python
# app/core/logging.py
import logging
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data)


def setup_logging():
    """Configure structured logging."""
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    logger = logging.getLogger("auth")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


auth_logger = setup_logging()
```

### Log Auth Events

```python
# app/auth/events.py
from app.core.logging import auth_logger


def log_login_attempt(email: str, success: bool, reason: str | None = None):
    """Log login attempt."""
    auth_logger.info(
        "Login attempt",
        extra={
            "email": email,
            "success": success,
            "reason": reason,
        },
    )


def log_session_created(user_id: str, session_id: str):
    """Log session creation."""
    auth_logger.info(
        "Session created",
        extra={
            "user_id": user_id,
            "session_id": session_id,
        },
    )


def log_auth_error(error_code: str, user_id: str | None = None):
    """Log authentication error."""
    auth_logger.warning(
        "Auth error",
        extra={
            "error_code": error_code,
            "user_id": user_id,
        },
    )
```

## Security Considerations

### 1. Don't Reveal User Existence

```typescript
// Bad: Reveals if email exists
if (!user) {
  throw new Error("User not found")
}
if (!passwordMatch) {
  throw new Error("Wrong password")
}

// Good: Generic message
if (!user || !passwordMatch) {
  throw new Error("Invalid email or password")
}
```

### 2. Rate Limit Error Responses

```python
# Avoid timing attacks by adding consistent delay
import asyncio
import random

async def authenticate(email: str, password: str):
    # Add random delay to prevent timing attacks
    await asyncio.sleep(random.uniform(0.1, 0.3))

    user = await get_user_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError()
```

### 3. Log Security Events

```python
# Always log security-relevant events
def handle_auth_error(error: AuthException, request: Request):
    auth_logger.warning(
        f"Auth error: {error.code}",
        extra={
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "path": request.url.path,
        },
    )
```

## Checklist

- [ ] Error messages are user-friendly
- [ ] Error codes are consistent
- [ ] Sensitive info not leaked in errors
- [ ] Errors are properly logged
- [ ] Rate limiting in place
- [ ] Generic messages for auth failures
- [ ] Proper HTTP status codes used
- [ ] Client displays errors appropriately
