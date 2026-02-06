# Email Verification

## Overview

Email verification ensures users own the email addresses they register with. Better Auth provides built-in email verification support.

## Better Auth Configuration

### Enable Email Verification

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
    requireEmailVerification: true, // Enable verification
    sendVerificationOnSignUp: true, // Auto-send on signup
    verificationTokenExpiresIn: 60 * 60 * 24, // 24 hours
  },

  // Email configuration
  email: {
    sendVerificationEmail: async ({ user, url, token }) => {
      // Implement email sending
      await sendEmail({
        to: user.email,
        subject: "Verify your email",
        html: `
          <h1>Verify your email</h1>
          <p>Click the link below to verify your email address:</p>
          <a href="${url}">Verify Email</a>
          <p>This link expires in 24 hours.</p>
        `,
      })
    },
  },
})
```

## Email Providers

### Using Resend

```typescript
// lib/email.ts
import { Resend } from "resend"

const resend = new Resend(process.env.RESEND_API_KEY)

export async function sendEmail({
  to,
  subject,
  html,
}: {
  to: string
  subject: string
  html: string
}) {
  const { error } = await resend.emails.send({
    from: "noreply@yourdomain.com",
    to,
    subject,
    html,
  })

  if (error) {
    console.error("Email send error:", error)
    throw new Error("Failed to send email")
  }
}
```

### Using Nodemailer (SMTP)

```typescript
// lib/email.ts
import nodemailer from "nodemailer"

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: parseInt(process.env.SMTP_PORT || "587"),
  secure: process.env.SMTP_SECURE === "true",
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASSWORD,
  },
})

export async function sendEmail({
  to,
  subject,
  html,
}: {
  to: string
  subject: string
  html: string
}) {
  await transporter.sendMail({
    from: process.env.SMTP_FROM,
    to,
    subject,
    html,
  })
}
```

## Verification Flow

### 1. Sign Up with Verification

```typescript
"use client"

import { signUp } from "@/lib/auth-client"
import { useState } from "react"

export function SignUpForm() {
  const [status, setStatus] = useState<"idle" | "pending" | "sent">("idle")
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setStatus("pending")
    setError(null)

    const formData = new FormData(e.currentTarget)

    const { error } = await signUp.email({
      email: formData.get("email") as string,
      password: formData.get("password") as string,
      name: formData.get("name") as string,
    })

    if (error) {
      setError(error.message)
      setStatus("idle")
    } else {
      setStatus("sent")
    }
  }

  if (status === "sent") {
    return (
      <div className="text-center p-6">
        <h2 className="text-xl font-semibold">Check your email</h2>
        <p className="text-gray-600 mt-2">
          We've sent a verification link to your email address.
          Please click the link to verify your account.
        </p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="text-red-500">{error}</div>}
      {/* Form fields */}
    </form>
  )
}
```

### 2. Verification Page

```typescript
// app/verify-email/page.tsx
import { auth } from "@/lib/auth"
import { redirect } from "next/navigation"

interface Props {
  searchParams: Promise<{ token?: string }>
}

export default async function VerifyEmailPage({ searchParams }: Props) {
  const { token } = await searchParams

  if (!token) {
    return (
      <div className="text-center p-6">
        <h1 className="text-xl font-semibold text-red-600">Invalid Link</h1>
        <p>The verification link is invalid or has expired.</p>
      </div>
    )
  }

  try {
    await auth.api.verifyEmail({ token })
    redirect("/login?verified=true")
  } catch {
    return (
      <div className="text-center p-6">
        <h1 className="text-xl font-semibold text-red-600">
          Verification Failed
        </h1>
        <p>The verification link is invalid or has expired.</p>
        <a href="/resend-verification" className="text-blue-600">
          Request a new verification link
        </a>
      </div>
    )
  }
}
```

### 3. Resend Verification

```typescript
"use client"

import { useState } from "react"

export function ResendVerification() {
  const [email, setEmail] = useState("")
  const [status, setStatus] = useState<"idle" | "pending" | "sent" | "error">(
    "idle"
  )

  const handleResend = async () => {
    setStatus("pending")

    const response = await fetch("/api/auth/resend-verification", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    })

    if (response.ok) {
      setStatus("sent")
    } else {
      setStatus("error")
    }
  }

  return (
    <div className="space-y-4">
      {status === "sent" ? (
        <p className="text-green-600">Verification email sent!</p>
      ) : (
        <>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            className="w-full px-3 py-2 border rounded"
          />
          <button
            onClick={handleResend}
            disabled={status === "pending"}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded"
          >
            {status === "pending" ? "Sending..." : "Resend Verification"}
          </button>
          {status === "error" && (
            <p className="text-red-500">Failed to send. Please try again.</p>
          )}
        </>
      )}
    </div>
  )
}
```

## FastAPI Integration

### Check Verification Status

```python
# app/auth/dependencies.py
from fastapi import HTTPException, status

from app.auth.dependencies import CurrentUser


async def require_verified_email(user: CurrentUser) -> CurrentUser:
    """Require user to have verified email."""
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )
    return user


# Type alias
VerifiedUser = Annotated[User, Depends(require_verified_email)]
```

### Protected Route with Verification

```python
from app.auth.dependencies import VerifiedUser

@router.post("/create-post")
async def create_post(user: VerifiedUser, data: PostCreate):
    """Only verified users can create posts."""
    # ... create post logic
```

## Email Templates

### Verification Email Template

```typescript
// lib/email-templates.ts
export function verificationEmailTemplate({
  name,
  verifyUrl,
  expiresIn,
}: {
  name: string
  verifyUrl: string
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
    <h1 style="color: #333;">Verify your email</h1>

    <p>Hi ${name || "there"},</p>

    <p>Thanks for signing up! Please verify your email address by clicking the button below:</p>

    <div style="text-align: center; margin: 30px 0;">
      <a href="${verifyUrl}"
         style="background-color: #0070f3; color: white; padding: 12px 24px;
                text-decoration: none; border-radius: 5px; display: inline-block;">
        Verify Email
      </a>
    </div>

    <p style="color: #666; font-size: 14px;">
      This link will expire in ${expiresIn}.
    </p>

    <p style="color: #666; font-size: 14px;">
      If you didn't create an account, you can safely ignore this email.
    </p>

    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">

    <p style="color: #999; font-size: 12px;">
      If the button doesn't work, copy and paste this link into your browser:
      <br>
      <a href="${verifyUrl}" style="color: #0070f3;">${verifyUrl}</a>
    </p>
  </div>
</body>
</html>
`
}
```

## Database Schema

Better Auth stores verification tokens in the `verification` table:

```sql
CREATE TABLE "verification" (
  "id" TEXT PRIMARY KEY,
  "identifier" TEXT NOT NULL,     -- Usually the email
  "value" TEXT NOT NULL,          -- The token
  "expiresAt" TIMESTAMP NOT NULL,
  "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Best Practices

1. **Token Security**
   - Use cryptographically secure random tokens
   - Set reasonable expiration times (24-48 hours)
   - Invalidate token after use

2. **Rate Limiting**
   - Limit verification email sends (e.g., 3 per hour)
   - Prevent abuse of resend functionality

3. **User Experience**
   - Show clear messages about verification status
   - Provide easy resend option
   - Allow login but limit functionality until verified

4. **Email Deliverability**
   - Use authenticated sending domain
   - Include plain text version
   - Avoid spam trigger words

## Environment Variables

```bash
# Email Provider (Resend)
RESEND_API_KEY="re_xxxxx"

# Or SMTP
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_SECURE="false"
SMTP_USER="your@email.com"
SMTP_PASSWORD="app-password"
SMTP_FROM="noreply@yourdomain.com"
```
