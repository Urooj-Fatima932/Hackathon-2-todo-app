# Initialize Next.js Project

## Quick Start Commands

```bash
# Create new Next.js project with TypeScript, Tailwind, ESLint, App Router
npx create-next-app@latest my-app --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*"

cd my-app

# Install core dependencies
npm install zod react-hook-form @hookform/resolvers

# Install shadcn/ui
npx shadcn@latest init -y

# Add common components
npx shadcn@latest add button input label form card textarea select checkbox dialog dropdown-menu avatar skeleton toast

# Install additional utilities
npm install clsx tailwind-merge lucide-react
```

## Project Structure Setup

After running commands above, create this structure:

```bash
# Create directories
mkdir -p lib/api lib/validations actions types components/ui hooks
```

## Essential Files to Create

### lib/utils.ts
```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### lib/api/client.ts
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string
  ) {
    super(detail)
    this.name = "ApiError"
  }
}

export async function api<T>(
  endpoint: string,
  options: RequestInit & { next?: NextFetchRequestConfig } = {}
): Promise<T> {
  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }))
    throw new ApiError(res.status, error.detail)
  }

  const text = await res.text()
  return text ? JSON.parse(text) : null
}
```

### components/providers.tsx
```typescript
"use client"

import { ThemeProvider } from "next-themes"
import { Toaster } from "@/components/ui/toaster"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      {children}
      <Toaster />
    </ThemeProvider>
  )
}
```

### app/layout.tsx (update)
```typescript
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { Providers } from "@/components/providers"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: {
    default: "My App",
    template: "%s | My App",
  },
  description: "My awesome app",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

### app/error.tsx
```typescript
"use client"

import { Button } from "@/components/ui/button"

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
      <h2 className="text-2xl font-bold">Something went wrong!</h2>
      <p className="text-muted-foreground">{error.message}</p>
      <Button onClick={reset}>Try again</Button>
    </div>
  )
}
```

### app/not-found.tsx
```typescript
import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
      <h1 className="text-6xl font-bold">404</h1>
      <h2 className="text-2xl">Page not found</h2>
      <Button asChild>
        <Link href="/">Go home</Link>
      </Button>
    </div>
  )
}
```

### app/loading.tsx
```typescript
export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
    </div>
  )
}
```

### middleware.ts (basic)
```typescript
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  // Add custom headers, auth checks, etc.
  return NextResponse.next()
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
}
```

## Environment Variables

### .env.local
```bash
# API
NEXT_PUBLIC_API_URL="http://localhost:8000"

# Auth (if using fullstack-auth)
BETTER_AUTH_SECRET="generate-32-char-secret"
DATABASE_URL="postgresql://..."

# OAuth (optional)
GITHUB_ID=""
GITHUB_SECRET=""
GOOGLE_ID=""
GOOGLE_SECRET=""
```

### .env.example
```bash
NEXT_PUBLIC_API_URL="http://localhost:8000"
BETTER_AUTH_SECRET=""
DATABASE_URL=""
```

## With Authentication (fullstack-auth)

```bash
# Additional dependencies for auth
npm install better-auth @neondatabase/serverless
```

Then follow `fullstack-auth` skill for setup.

## With FastAPI Backend

Ensure your FastAPI backend has CORS configured:

```python
# FastAPI main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Verify Setup

```bash
npm run dev
```

Visit http://localhost:3000 to confirm everything works.
