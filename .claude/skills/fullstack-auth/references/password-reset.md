# Password Reset

## Overview

Password reset allows users to recover access to their accounts when they forget their passwords. Better Auth provides built-in password reset functionality.

## Better Auth Configuration

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"
import { Pool } from "@neondatabase/serverless"

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),

  emailAndPassword: {
    enabled: true,
    // Password reset settings
    sendResetPasswordEmail: async ({ user, url, token }) => {
      await sendEmail({
        to: user.email,
        subject: "Reset your password",
        html: `
          <h1>Reset your password</h1>
          <p>Click the link below to reset your password:</p>
          <a href="${url}">Reset Password</a>
          <p>This link expires in 1 hour.</p>
          <p>If you didn't request this, you can ignore this email.</p>
        `,
      })
    },
    resetPasswordTokenExpiresIn: 60 * 60, // 1 hour
  },
})
```

## Password Reset Flow

### 1. Forgot Password Page

```typescript
// app/forgot-password/page.tsx
import { ForgotPasswordForm } from "@/components/auth/forgot-password-form"

export default function ForgotPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md p-8">
        <h1 className="text-2xl font-bold text-center mb-6">
          Forgot Password
        </h1>
        <ForgotPasswordForm />
      </div>
    </div>
  )
}
```

### 2. Forgot Password Form

```typescript
// components/auth/forgot-password-form.tsx
"use client"

import { useState } from "react"
import { authClient } from "@/lib/auth-client"

export function ForgotPasswordForm() {
  const [email, setEmail] = useState("")
  const [status, setStatus] = useState<"idle" | "pending" | "sent" | "error">(
    "idle"
  )
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setStatus("pending")
    setError(null)

    const { error } = await authClient.forgetPassword({
      email,
      redirectTo: "/reset-password",
    })

    if (error) {
      setError(error.message)
      setStatus("error")
    } else {
      setStatus("sent")
    }
  }

  if (status === "sent") {
    return (
      <div className="text-center space-y-4">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
          <svg
            className="w-8 h-8 text-green-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <h2 className="text-xl font-semibold">Check your email</h2>
        <p className="text-gray-600">
          We've sent password reset instructions to <strong>{email}</strong>
        </p>
        <p className="text-sm text-gray-500">
          Didn't receive the email? Check your spam folder or{" "}
          <button
            onClick={() => setStatus("idle")}
            className="text-blue-600 hover:underline"
          >
            try again
          </button>
        </p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <p className="text-gray-600 text-center">
        Enter your email address and we'll send you a link to reset your
        password.
      </p>

      {error && (
        <div className="p-3 bg-red-50 text-red-700 rounded text-sm">
          {error}
        </div>
      )}

      <div>
        <label htmlFor="email" className="block text-sm font-medium mb-1">
          Email
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
          placeholder="you@example.com"
        />
      </div>

      <button
        type="submit"
        disabled={status === "pending"}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {status === "pending" ? "Sending..." : "Send Reset Link"}
      </button>

      <p className="text-center text-sm">
        Remember your password?{" "}
        <a href="/login" className="text-blue-600 hover:underline">
          Sign in
        </a>
      </p>
    </form>
  )
}
```

### 3. Reset Password Page

```typescript
// app/reset-password/page.tsx
import { ResetPasswordForm } from "@/components/auth/reset-password-form"

interface Props {
  searchParams: Promise<{ token?: string }>
}

export default async function ResetPasswordPage({ searchParams }: Props) {
  const { token } = await searchParams

  if (!token) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center p-8">
          <h1 className="text-xl font-semibold text-red-600">Invalid Link</h1>
          <p className="mt-2 text-gray-600">
            The password reset link is invalid or has expired.
          </p>
          <a
            href="/forgot-password"
            className="mt-4 inline-block text-blue-600 hover:underline"
          >
            Request a new link
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md p-8">
        <h1 className="text-2xl font-bold text-center mb-6">
          Reset Password
        </h1>
        <ResetPasswordForm token={token} />
      </div>
    </div>
  )
}
```

### 4. Reset Password Form

```typescript
// components/auth/reset-password-form.tsx
"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { authClient } from "@/lib/auth-client"

interface Props {
  token: string
}

export function ResetPasswordForm({ token }: Props) {
  const router = useRouter()
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [status, setStatus] = useState<"idle" | "pending" | "success" | "error">(
    "idle"
  )
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validate passwords match
    if (password !== confirmPassword) {
      setError("Passwords do not match")
      return
    }

    // Validate password strength
    if (password.length < 8) {
      setError("Password must be at least 8 characters")
      return
    }

    setStatus("pending")

    const { error } = await authClient.resetPassword({
      token,
      newPassword: password,
    })

    if (error) {
      setError(error.message)
      setStatus("error")
    } else {
      setStatus("success")
      // Redirect to login after short delay
      setTimeout(() => {
        router.push("/login?reset=true")
      }, 2000)
    }
  }

  if (status === "success") {
    return (
      <div className="text-center space-y-4">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
          <svg
            className="w-8 h-8 text-green-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <h2 className="text-xl font-semibold">Password Reset!</h2>
        <p className="text-gray-600">
          Your password has been reset successfully. Redirecting to login...
        </p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-3 bg-red-50 text-red-700 rounded text-sm">
          {error}
        </div>
      )}

      <div>
        <label htmlFor="password" className="block text-sm font-medium mb-1">
          New Password
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
          className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
          placeholder="Enter new password"
        />
      </div>

      <div>
        <label
          htmlFor="confirmPassword"
          className="block text-sm font-medium mb-1"
        >
          Confirm Password
        </label>
        <input
          id="confirmPassword"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          minLength={8}
          className="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
          placeholder="Confirm new password"
        />
      </div>

      <div className="text-sm text-gray-600">
        <p>Password requirements:</p>
        <ul className="list-disc list-inside mt-1 space-y-1">
          <li className={password.length >= 8 ? "text-green-600" : ""}>
            At least 8 characters
          </li>
          <li
            className={
              password === confirmPassword && password.length > 0
                ? "text-green-600"
                : ""
            }
          >
            Passwords match
          </li>
        </ul>
      </div>

      <button
        type="submit"
        disabled={status === "pending"}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {status === "pending" ? "Resetting..." : "Reset Password"}
      </button>
    </form>
  )
}
```

## FastAPI Password Reset

### Password Change Endpoint

```python
# app/auth/router.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlmodel import select

from app.auth.dependencies import CurrentUser
from app.auth.utils import hash_password, verify_password
from app.core.deps import SessionDep
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/change-password")
async def change_password(
    user: CurrentUser,
    data: ChangePasswordRequest,
    db: SessionDep,
):
    """Change password for authenticated user."""
    # Verify current password
    if not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account uses OAuth login",
        )

    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Validate new password
    if len(data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )

    # Update password
    user.hashed_password = hash_password(data.new_password)
    db.add(user)
    await db.commit()

    return {"message": "Password changed successfully"}
```

## Email Templates

### Password Reset Email

```typescript
// lib/email-templates.ts
export function passwordResetEmailTemplate({
  name,
  resetUrl,
  expiresIn,
}: {
  name: string
  resetUrl: string
  expiresIn: string
}) {
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: sans-serif; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto;">
    <h1 style="color: #333;">Reset your password</h1>

    <p>Hi ${name || "there"},</p>

    <p>We received a request to reset your password. Click the button below to create a new password:</p>

    <div style="text-align: center; margin: 30px 0;">
      <a href="${resetUrl}"
         style="background-color: #0070f3; color: white; padding: 12px 24px;
                text-decoration: none; border-radius: 5px; display: inline-block;">
        Reset Password
      </a>
    </div>

    <p style="color: #666; font-size: 14px;">
      This link will expire in ${expiresIn}.
    </p>

    <p style="color: #666; font-size: 14px;">
      If you didn't request a password reset, you can safely ignore this email.
      Your password will remain unchanged.
    </p>

    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">

    <p style="color: #999; font-size: 12px;">
      If the button doesn't work, copy and paste this link into your browser:
      <br>
      <a href="${resetUrl}" style="color: #0070f3;">${resetUrl}</a>
    </p>
  </div>
</body>
</html>
`
}
```

## Security Considerations

### 1. Token Security

```typescript
// Tokens should be:
// - Cryptographically random
// - Single-use (invalidate after use)
// - Time-limited (1 hour recommended)
// - Hashed when stored in database
```

### 2. Rate Limiting

```typescript
// lib/rate-limit.ts
import { Ratelimit } from "@upstash/ratelimit"
import { Redis } from "@upstash/redis"

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(3, "1 h"), // 3 requests per hour
})

export async function checkPasswordResetRateLimit(email: string) {
  const { success } = await ratelimit.limit(`password-reset:${email}`)
  return success
}
```

### 3. Prevent User Enumeration

```typescript
// Always return same message regardless of whether email exists
const handleForgotPassword = async (email: string) => {
  // Don't reveal if email exists
  return {
    message: "If an account exists, we've sent reset instructions.",
  }
}
```

### 4. Invalidate Sessions

```typescript
// After password reset, invalidate all existing sessions
// This is handled automatically by Better Auth
```

## Password Validation

```typescript
// lib/password-validation.ts
export function validatePassword(password: string): {
  valid: boolean
  errors: string[]
} {
  const errors: string[] = []

  if (password.length < 8) {
    errors.push("Password must be at least 8 characters")
  }

  if (password.length > 128) {
    errors.push("Password must be less than 128 characters")
  }

  if (!/[a-z]/.test(password)) {
    errors.push("Password must contain a lowercase letter")
  }

  if (!/[A-Z]/.test(password)) {
    errors.push("Password must contain an uppercase letter")
  }

  if (!/[0-9]/.test(password)) {
    errors.push("Password must contain a number")
  }

  return {
    valid: errors.length === 0,
    errors,
  }
}
```

## Checklist

- [ ] Forgot password page implemented
- [ ] Reset password page implemented
- [ ] Email template configured
- [ ] Rate limiting in place
- [ ] Token expiration set (1 hour)
- [ ] Sessions invalidated after reset
- [ ] Password validation implemented
- [ ] User enumeration prevented
- [ ] Success/error messages are user-friendly
