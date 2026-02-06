# Next.js App Router Common Pitfalls & Prevention

This document details the most common App Router issues and how to prevent them.

## Issue 1: Route Group Conflicts

### The Problem

Having both a root `app/page.tsx` and route group pages like `app/(public)/page.tsx` creates a conflict where the root page takes precedence, making the route group page unreachable.

### Why It Happens

- Route groups `(name)` are used for organization and don't affect URLs
- `(public)/page.tsx` serves at `/` just like `page.tsx`
- Next.js prioritizes the root `page.tsx` over route group pages
- Developers create default Next.js template (which includes root page.tsx) then add route groups

### Real-World Example

```
❌ BROKEN STRUCTURE:
app/
├── page.tsx              # Default Next.js homepage
└── (public)/
    ├── layout.tsx
    └── page.tsx          # Custom portfolio homepage (never reached!)

User visits / → Sees default Next.js page, not custom portfolio
```

### Prevention Strategy

1. **When using route groups for root-level pages, never create root page.tsx**
2. **Delete template page.tsx immediately after `create-next-app`**
3. **Check for conflicts before generating any pages**

### Correct Patterns

```
✅ PATTERN 1: Route groups for organization
app/
├── layout.tsx            # Root layout
├── (public)/
│   ├── layout.tsx        # Public pages layout
│   ├── page.tsx          # Homepage at /
│   ├── about/
│   │   └── page.tsx      # /about
│   └── contact/
│       └── page.tsx      # /contact
└── (admin)/
    ├── layout.tsx        # Admin layout
    └── dashboard/
        └── page.tsx      # /dashboard

✅ PATTERN 2: Mixed route groups and regular routes
app/
├── layout.tsx
├── (marketing)/
│   ├── page.tsx          # / (homepage)
│   └── pricing/
│       └── page.tsx      # /pricing
├── blog/
│   └── page.tsx          # /blog (regular route, not grouped)
└── (app)/
    ├── dashboard/
    │   └── page.tsx      # /dashboard
    └── settings/
        └── page.tsx      # /settings

✅ PATTERN 3: No route groups, regular structure
app/
├── layout.tsx
├── page.tsx              # OK when NOT using route groups at this level
├── about/
│   └── page.tsx
└── contact/
    └── page.tsx
```

### Detection Script

```typescript
function detectRouteGroupConflict(files: string[]): string | null {
  const hasRootPage = files.some(f => f === 'app/page.tsx')
  const routeGroupPages = files.filter(f =>
    /^app\/\([^)]+\)\/page\.tsx$/.test(f)
  )

  if (hasRootPage && routeGroupPages.length > 0) {
    return `Conflict: Root page.tsx exists with route groups: ${routeGroupPages.join(', ')}`
  }

  return null
}
```

### Fix for Existing Projects

```bash
# Check for conflict
if [ -f "app/page.tsx" ] && ls -d app/\(*\) 2>/dev/null | grep -q .; then
  echo "❌ Conflict detected!"
  echo "Root page.tsx exists with route groups"
  echo "Choose one:"
  echo "1. Remove app/page.tsx (recommended if using route groups)"
  echo "2. Move route group content to regular routes"
fi
```

---

## Issue 2: Missing 'use client' Directive

### The Problem

Components with interactivity (event handlers, hooks, browser APIs) need `'use client'` directive. Without it, Next.js throws:
```
Error: Event handlers cannot be passed to Client Component props.
  <button onClick={function onClick}>
```

### Why It Happens

1. **Default is Server Components** - All components are Server Components unless marked otherwise
2. **Server Components can't be interactive** - They render on the server and can't have event handlers
3. **Easy to forget** - Especially with shadcn/ui components that look like regular React components

### Real-World Scenarios

#### Scenario 1: Button Component

```tsx
// ❌ WRONG: components/ui/button.tsx
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"

export function Button({ onClick, children, ...props }) {
  const Comp = props.asChild ? Slot : "button"
  return <Comp onClick={onClick} {...props}>{children}</Comp>
  // Error when onClick is passed!
}

// ✅ CORRECT: Add 'use client'
'use client'

import * as React from "react"
import { Slot } from "@radix-ui/react-slot"

export function Button({ onClick, children, ...props }) {
  const Comp = props.asChild ? Slot : "button"
  return <Comp onClick={onClick} {...props}>{children}</Comp>
}
```

#### Scenario 2: Navbar with Mobile Menu

```tsx
// ❌ WRONG: components/navbar.tsx
import { useState } from 'react'
import { Button } from '@/components/ui/button'

export function Navbar() {
  const [isOpen, setIsOpen] = useState(false) // ❌ useState without 'use client'

  return (
    <nav>
      <Button onClick={() => setIsOpen(true)}>Menu</Button>
      {/* ... */}
    </nav>
  )
}

// ✅ CORRECT: Add 'use client'
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'

export function Navbar() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <nav>
      <Button onClick={() => setIsOpen(true)}>Menu</Button>
      {/* ... */}
    </nav>
  )
}
```

#### Scenario 3: Form with react-hook-form

```tsx
// ❌ WRONG: components/contact-form.tsx
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'

export function ContactForm() {
  const form = useForm() // ❌ Hook without 'use client'

  return <form onSubmit={form.handleSubmit(onSubmit)}>...</form>
}

// ✅ CORRECT: Add 'use client'
'use client'

import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'

export function ContactForm() {
  const form = useForm()

  return <form onSubmit={form.handleSubmit(onSubmit)}>...</form>
}
```

### Prevention Strategy

1. **Check every component before writing** - Does it have interactivity?
2. **Auto-detect patterns** - Use regex to identify hooks, events, browser APIs
3. **Reference list** - Know which shadcn/ui components need it
4. **Add proactively** - Better to add unnecessarily than forget

### Detection Patterns

```typescript
function needsClientDirective(code: string): boolean {
  const indicators = [
    // Event handlers
    /\b(onClick|onChange|onSubmit|onFocus|onBlur|onKeyDown|onKeyUp|onKeyPress|onMouseEnter|onMouseLeave|onScroll)\w*\s*=/,

    // React hooks
    /\buse(State|Effect|Context|Ref|Reducer|Callback|Memo|ImperativeHandle|LayoutEffect|DebugValue|Transition|DeferredValue|Id)\b/,

    // Browser APIs
    /\b(window|document|localStorage|sessionStorage|navigator|location|history|alert|confirm|prompt)\./,

    // Third-party interactive libraries
    /from ['"]framer-motion['"]/,
    /from ['"]react-hook-form['"]/,
    /from ['"]@radix-ui/,
    /from ['"]react-hot-toast['"]/,
    /from ['"]sonner['"]/,

    // Animation libraries
    /from ['"]gsap['"]/,
    /from ['"]@react-spring/,
  ]

  return indicators.some(pattern => pattern.test(code))
}
```

### shadcn/ui Component Reference

| Component | Needs 'use client'? | Why |
|-----------|---------------------|-----|
| **Interactive (needs 'use client')** | | |
| Button | ✅ | Uses Slot, receives onClick |
| Input | ✅ | onChange, onFocus events |
| Textarea | ✅ | onChange event |
| Checkbox | ✅ | onChange event |
| Switch | ✅ | onChange event |
| Select | ✅ | Radix UI with state |
| Combobox | ✅ | Radix UI with state |
| Command | ✅ | Keyboard navigation, state |
| Dialog | ✅ | Open/close state |
| Alert Dialog | ✅ | Open/close state |
| Sheet | ✅ | Open/close state |
| Popover | ✅ | Open/close state |
| Tooltip | ✅ | Hover state |
| Hover Card | ✅ | Hover state |
| Dropdown Menu | ✅ | Open/close state |
| Context Menu | ✅ | Right-click state |
| Navigation Menu | ✅ | Hover/focus state |
| Menubar | ✅ | Keyboard navigation |
| Tabs | ✅ | Active tab state |
| Accordion | ✅ | Expanded state |
| Collapsible | ✅ | Expanded state |
| Slider | ✅ | onChange event |
| Scroll Area | ✅ | Custom scrolling |
| Toast / Toaster | ✅ | Dynamic notifications |
| Form (with react-hook-form) | ✅ | Uses hooks |
| **Presentational (no directive needed)** | | |
| Card | ❌ | Pure markup |
| Badge | ❌ | Pure markup |
| Separator | ❌ | Pure markup |
| Avatar | ❌ | Pure markup (unless fallback uses state) |
| Skeleton | ❌ | Pure markup |
| Progress | ❌ | Just displays value |
| Table | ❌ | Pure markup |
| Typography elements | ❌ | Pure markup |

### Composition Pattern (Best Practice)

Keep Server Components as the default, compose with Client Components:

```tsx
// ✅ BEST: Server Component with Client Component children
// app/products/page.tsx (Server Component - no directive)
import { db } from '@/lib/db'
import { ProductCard } from '@/components/product-card' // Client Component

export default async function ProductsPage() {
  const products = await db.product.findMany()

  return (
    <div>
      <h1>Products</h1>
      <div className="grid grid-cols-3 gap-4">
        {products.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  )
}

// components/product-card.tsx (Client Component)
'use client'

import { Button } from '@/components/ui/button'

export function ProductCard({ product }) {
  return (
    <div>
      <h2>{product.name}</h2>
      <Button onClick={() => addToCart(product.id)}>
        Add to Cart
      </Button>
    </div>
  )
}
```

---

## Issue 3: Passing Functions from Server to Client

### The Problem

You cannot pass functions (callbacks, event handlers) directly from Server Components to Client Components.

```tsx
// ❌ WRONG
// app/page.tsx (Server Component)
import { ClientButton } from '@/components/client-button'

export default function Page() {
  const handleClick = () => console.log('clicked')

  return <ClientButton onClick={handleClick} /> // ❌ Cannot serialize function
}
```

### Solution Patterns

**Pattern 1: Define handler in Client Component**
```tsx
// ✅ CORRECT
// app/page.tsx (Server Component)
import { ClientButton } from '@/components/client-button'

export default function Page() {
  return <ClientButton /> // Pass data, not functions
}

// components/client-button.tsx (Client Component)
'use client'

export function ClientButton() {
  const handleClick = () => console.log('clicked')
  return <button onClick={handleClick}>Click</button>
}
```

**Pattern 2: Use Server Actions**
```tsx
// ✅ CORRECT with Server Actions
// app/actions.ts
'use server'

export async function handleSubmit(formData: FormData) {
  const data = Object.fromEntries(formData)
  // Server-side processing
}

// components/form.tsx (Client Component)
'use client'

import { handleSubmit } from '@/app/actions'

export function Form() {
  return (
    <form action={handleSubmit}>
      <input name="title" />
      <button type="submit">Submit</button>
    </form>
  )
}
```

---

## Prevention Checklist

Before writing any Next.js App Router code:

### Route Structure
- [ ] Identified if using route groups
- [ ] Confirmed no root page.tsx when using route groups at same level
- [ ] Verified no overlapping routes

### Component Classification
- [ ] Classified each component as Server or Client
- [ ] Added 'use client' to components with:
  - [ ] Event handlers (onClick, onChange, etc.)
  - [ ] React hooks (useState, useEffect, etc.)
  - [ ] Browser APIs (window, document, etc.)
  - [ ] Third-party interactive libraries
- [ ] Verified shadcn/ui components have correct directives

### Data Flow
- [ ] Server Components fetch data directly
- [ ] Client Components receive data as props
- [ ] No functions passed from Server to Client
- [ ] Server Actions used for mutations

### Testing
- [ ] Build passes without directive errors
- [ ] No "Event handlers cannot be passed" errors
- [ ] Routes resolve correctly
- [ ] Interactive features work
