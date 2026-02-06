# Better Auth - OAuth Providers

## GitHub

### Setup

1. Go to GitHub → Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in:
   - Application name: Your app name
   - Homepage URL: `http://localhost:3000`
   - Authorization callback URL: `http://localhost:3000/api/auth/callback/github`
4. Save Client ID and Client Secret

### Configuration

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
    },
  },
})
```

### Environment Variables

```bash
GITHUB_ID="your-github-client-id"
GITHUB_SECRET="your-github-client-secret"
```

### Client Usage

```typescript
"use client"

import { signIn } from "@/lib/auth-client"

export function GitHubSignIn() {
  const handleSignIn = async () => {
    await signIn.social({
      provider: "github",
      callbackURL: "/dashboard",
    })
  }

  return (
    <button onClick={handleSignIn}>
      Continue with GitHub
    </button>
  )
}
```

## Google

### Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Go to APIs & Services → Credentials
4. Click "Create Credentials" → "OAuth client ID"
5. Configure consent screen if needed
6. Select "Web application"
7. Add authorized redirect URI: `http://localhost:3000/api/auth/callback/google`
8. Save Client ID and Client Secret

### Configuration

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_ID!,
      clientSecret: process.env.GOOGLE_SECRET!,
    },
  },
})
```

### Environment Variables

```bash
GOOGLE_ID="your-google-client-id.apps.googleusercontent.com"
GOOGLE_SECRET="your-google-client-secret"
```

### Client Usage

```typescript
"use client"

import { signIn } from "@/lib/auth-client"

export function GoogleSignIn() {
  const handleSignIn = async () => {
    await signIn.social({
      provider: "google",
      callbackURL: "/dashboard",
    })
  }

  return (
    <button onClick={handleSignIn}>
      Continue with Google
    </button>
  )
}
```

## Discord

### Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Go to OAuth2 → General
4. Add redirect: `http://localhost:3000/api/auth/callback/discord`
5. Copy Client ID and Client Secret

### Configuration

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  socialProviders: {
    discord: {
      clientId: process.env.DISCORD_ID!,
      clientSecret: process.env.DISCORD_SECRET!,
    },
  },
})
```

### Environment Variables

```bash
DISCORD_ID="your-discord-client-id"
DISCORD_SECRET="your-discord-client-secret"
```

## Twitter/X

### Setup

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a project and app
3. Set up OAuth 2.0
4. Add callback URL: `http://localhost:3000/api/auth/callback/twitter`

### Configuration

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  socialProviders: {
    twitter: {
      clientId: process.env.TWITTER_ID!,
      clientSecret: process.env.TWITTER_SECRET!,
    },
  },
})
```

## Apple

### Setup

1. Go to [Apple Developer Portal](https://developer.apple.com/)
2. Certificates, Identifiers & Profiles → Identifiers
3. Create App ID with Sign in with Apple capability
4. Create Services ID for web authentication
5. Configure domains and redirect URLs

### Configuration

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  socialProviders: {
    apple: {
      clientId: process.env.APPLE_ID!,
      clientSecret: process.env.APPLE_SECRET!,
    },
  },
})
```

## Microsoft/Azure AD

### Setup

1. Go to [Azure Portal](https://portal.azure.com/)
2. Azure Active Directory → App registrations
3. New registration
4. Add redirect URI: `http://localhost:3000/api/auth/callback/microsoft`

### Configuration

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  socialProviders: {
    microsoft: {
      clientId: process.env.MICROSOFT_ID!,
      clientSecret: process.env.MICROSOFT_SECRET!,
      tenantId: process.env.MICROSOFT_TENANT_ID, // Optional, for single-tenant
    },
  },
})
```

## Email/Password (Credentials)

### Configuration

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
    maxPasswordLength: 128,
    requireEmailVerification: false, // Set true in production
  },
})
```

### Sign Up

```typescript
"use client"

import { signUp } from "@/lib/auth-client"
import { useState } from "react"

export function SignUpForm() {
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)

    const { error } = await signUp.email({
      email: formData.get("email") as string,
      password: formData.get("password") as string,
      name: formData.get("name") as string,
      callbackURL: "/dashboard",
    })

    if (error) {
      setError(error.message)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="text-red-500">{error}</div>}
      <input name="name" type="text" placeholder="Name" required />
      <input name="email" type="email" placeholder="Email" required />
      <input name="password" type="password" placeholder="Password" required minLength={8} />
      <button type="submit">Sign Up</button>
    </form>
  )
}
```

### Sign In

```typescript
"use client"

import { signIn } from "@/lib/auth-client"
import { useState } from "react"

export function SignInForm() {
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)

    const { error } = await signIn.email({
      email: formData.get("email") as string,
      password: formData.get("password") as string,
      callbackURL: "/dashboard",
    })

    if (error) {
      setError(error.message)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="text-red-500">{error}</div>}
      <input name="email" type="email" placeholder="Email" required />
      <input name="password" type="password" placeholder="Password" required />
      <button type="submit">Sign In</button>
    </form>
  )
}
```

## Multiple Providers

### Full Configuration

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"
import { Pool } from "@neondatabase/serverless"

export const auth = betterAuth({
  database: new Pool({ connectionString: process.env.DATABASE_URL }),

  // Email/Password
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },

  // OAuth Providers
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
    },
    google: {
      clientId: process.env.GOOGLE_ID!,
      clientSecret: process.env.GOOGLE_SECRET!,
    },
    discord: {
      clientId: process.env.DISCORD_ID!,
      clientSecret: process.env.DISCORD_SECRET!,
    },
  },
})
```

### Complete Login Page

```typescript
// app/login/page.tsx
import { SignInForm } from "@/components/sign-in-form"
import { OAuthButtons } from "@/components/oauth-buttons"

export default function LoginPage() {
  return (
    <div className="max-w-md mx-auto mt-10 p-6">
      <h1 className="text-2xl font-bold mb-6">Sign In</h1>

      {/* OAuth Providers */}
      <OAuthButtons />

      <div className="relative my-6">
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

      <p className="mt-4 text-center text-sm">
        Don't have an account?{" "}
        <a href="/signup" className="text-blue-600">Sign up</a>
      </p>
    </div>
  )
}
```

### OAuth Buttons Component

```typescript
// components/oauth-buttons.tsx
"use client"

import { signIn } from "@/lib/auth-client"
import { useState } from "react"

export function OAuthButtons() {
  const [loading, setLoading] = useState<string | null>(null)

  const handleOAuth = async (provider: "github" | "google" | "discord") => {
    setLoading(provider)
    await signIn.social({
      provider,
      callbackURL: "/dashboard",
    })
  }

  return (
    <div className="space-y-2">
      <button
        onClick={() => handleOAuth("github")}
        disabled={loading !== null}
        className="w-full flex items-center justify-center gap-2 px-4 py-2 border rounded hover:bg-gray-50"
      >
        <GitHubIcon />
        {loading === "github" ? "Loading..." : "Continue with GitHub"}
      </button>

      <button
        onClick={() => handleOAuth("google")}
        disabled={loading !== null}
        className="w-full flex items-center justify-center gap-2 px-4 py-2 border rounded hover:bg-gray-50"
      >
        <GoogleIcon />
        {loading === "google" ? "Loading..." : "Continue with Google"}
      </button>

      <button
        onClick={() => handleOAuth("discord")}
        disabled={loading !== null}
        className="w-full flex items-center justify-center gap-2 px-4 py-2 border rounded hover:bg-gray-50"
      >
        <DiscordIcon />
        {loading === "discord" ? "Loading..." : "Continue with Discord"}
      </button>
    </div>
  )
}

// Icon components
function GitHubIcon() {
  return (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
    </svg>
  )
}

function GoogleIcon() {
  return (
    <svg className="w-5 h-5" viewBox="0 0 24 24">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
    </svg>
  )
}

function DiscordIcon() {
  return (
    <svg className="w-5 h-5" fill="#5865F2" viewBox="0 0 24 24">
      <path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189Z"/>
    </svg>
  )
}
```

## Account Linking

Better Auth handles account linking automatically. When a user signs in with a new provider using the same email, the accounts are linked.

### Check Linked Accounts

```typescript
// Get user's linked accounts (server-side)
import { auth } from "@/lib/auth"
import { headers } from "next/headers"

export default async function AccountsPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session) return null

  // Query accounts from database
  // This requires database access
  return (
    <div>
      <h2>Linked Accounts</h2>
      {/* Display linked accounts */}
    </div>
  )
}
```

## Production Callback URLs

Update callback URLs for production:

| Provider | Development | Production |
|----------|-------------|------------|
| GitHub | `http://localhost:3000/api/auth/callback/github` | `https://yourdomain.com/api/auth/callback/github` |
| Google | `http://localhost:3000/api/auth/callback/google` | `https://yourdomain.com/api/auth/callback/google` |
| Discord | `http://localhost:3000/api/auth/callback/discord` | `https://yourdomain.com/api/auth/callback/discord` |

Add both development and production URLs in each provider's OAuth settings.
