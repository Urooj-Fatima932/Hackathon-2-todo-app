# Better Auth Setup

## Installation

```bash
npm install better-auth @neondatabase/serverless
```

## Project Structure

```
├── lib/
│   ├── auth.ts              # Server-side auth config
│   └── auth-client.ts       # Client-side auth utilities
├── app/
│   └── api/auth/[...all]/
│       └── route.ts         # Auth API handler
└── middleware.ts            # Route protection
```

## Server Configuration

### lib/auth.ts

```typescript
import { betterAuth } from "better-auth"
import { Pool } from "@neondatabase/serverless"

export const auth = betterAuth({
  // Database - Neon serverless
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update session every 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // 5 minutes
    },
  },

  // Email/password authentication
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Set true in production
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

  // Advanced options
  advanced: {
    generateId: () => crypto.randomUUID(),
    cookiePrefix: "better-auth",
    useSecureCookies: process.env.NODE_ENV === "production",
  },
})

// Export types for use in app
export type Session = typeof auth.$Infer.Session
export type User = typeof auth.$Infer.Session.user
```

### lib/auth-client.ts

```typescript
import { createAuthClient } from "better-auth/react"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
})

// Export individual functions for convenience
export const {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession,
} = authClient
```

## API Route Handler

### app/api/auth/[...all]/route.ts

```typescript
import { auth } from "@/lib/auth"
import { toNextJsHandler } from "better-auth/next-js"

export const { GET, POST } = toNextJsHandler(auth)
```

## Environment Variables

```bash
# .env.local

# App URL
NEXT_PUBLIC_APP_URL="http://localhost:3000"

# Better Auth Secret (generate with: openssl rand -base64 32)
BETTER_AUTH_SECRET="your-random-32-character-secret-key"

# Neon Database
DATABASE_URL="postgresql://user:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require"

# OAuth - GitHub
GITHUB_ID="your-github-client-id"
GITHUB_SECRET="your-github-client-secret"

# OAuth - Google
GOOGLE_ID="your-google-client-id.apps.googleusercontent.com"
GOOGLE_SECRET="your-google-client-secret"
```

## Generate Secret

```bash
# Using OpenSSL
openssl rand -base64 32

# Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

## Database Schema

Better Auth automatically creates these tables:

```sql
-- Users table
CREATE TABLE "user" (
  "id" TEXT PRIMARY KEY,
  "name" TEXT,
  "email" TEXT UNIQUE NOT NULL,
  "emailVerified" BOOLEAN DEFAULT FALSE,
  "image" TEXT,
  "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions table
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

-- Accounts table (OAuth)
CREATE TABLE "account" (
  "id" TEXT PRIMARY KEY,
  "userId" TEXT NOT NULL REFERENCES "user"("id") ON DELETE CASCADE,
  "accountId" TEXT NOT NULL,
  "providerId" TEXT NOT NULL,
  "accessToken" TEXT,
  "refreshToken" TEXT,
  "accessTokenExpiresAt" TIMESTAMP,
  "refreshTokenExpiresAt" TIMESTAMP,
  "scope" TEXT,
  "idToken" TEXT,
  "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Verification tokens
CREATE TABLE "verification" (
  "id" TEXT PRIMARY KEY,
  "identifier" TEXT NOT NULL,
  "value" TEXT NOT NULL,
  "expiresAt" TIMESTAMP NOT NULL,
  "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Auto-Migration

Better Auth can auto-create tables. Enable in development:

```typescript
// lib/auth.ts
export const auth = betterAuth({
  database: new Pool({ connectionString: process.env.DATABASE_URL }),
  // ... other config
})

// Run migration CLI
// npx better-auth migrate
```

## Manual Migration with Prisma

If using Prisma alongside:

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")
  directUrl = env("DIRECT_URL")
}

model User {
  id            String    @id @default(cuid())
  name          String?
  email         String    @unique
  emailVerified Boolean   @default(false)
  image         String?
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
  sessions      Session[]
  accounts      Account[]
}

model Session {
  id        String   @id @default(cuid())
  userId    String
  token     String   @unique
  expiresAt DateTime
  ipAddress String?
  userAgent String?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model Account {
  id                    String    @id @default(cuid())
  userId                String
  accountId             String
  providerId            String
  accessToken           String?
  refreshToken          String?
  accessTokenExpiresAt  DateTime?
  refreshTokenExpiresAt DateTime?
  scope                 String?
  idToken               String?
  createdAt             DateTime  @default(now())
  updatedAt             DateTime  @updatedAt
  user                  User      @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([providerId, accountId])
}

model Verification {
  id         String   @id @default(cuid())
  identifier String
  value      String
  expiresAt  DateTime
  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt
}
```

## Session Configuration Options

```typescript
export const auth = betterAuth({
  session: {
    // How long until session expires
    expiresIn: 60 * 60 * 24 * 7, // 7 days in seconds

    // How often to refresh session in DB
    updateAge: 60 * 60 * 24, // 24 hours

    // Cookie-based session caching
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // Cache for 5 minutes
    },

    // Fresh session on sign-in
    freshAge: 60 * 10, // 10 minutes
  },
})
```

## Cookie Configuration

```typescript
export const auth = betterAuth({
  advanced: {
    // Cookie name prefix
    cookiePrefix: "myapp",

    // Secure cookies in production
    useSecureCookies: process.env.NODE_ENV === "production",

    // Cookie options
    cookies: {
      session: {
        name: "session",
        options: {
          httpOnly: true,
          sameSite: "lax",
          path: "/",
          secure: process.env.NODE_ENV === "production",
        },
      },
    },
  },
})
```

## Cross-Origin Setup (if API on different domain)

```typescript
// lib/auth.ts
export const auth = betterAuth({
  trustedOrigins: [
    "http://localhost:3000",
    "https://yourdomain.com",
  ],
  advanced: {
    crossSubDomainCookies: {
      enabled: true,
      domain: ".yourdomain.com", // Shared across subdomains
    },
  },
})
```

## Verification

Test your setup:

```typescript
// Test script or API route
import { auth } from "@/lib/auth"

// Check if auth is configured
console.log("Auth configured:", !!auth)

// Test database connection
const session = await auth.api.getSession({
  headers: new Headers(),
})
console.log("Session:", session)
```
