---
name: nextjs-ui-pro
description: |
  Generates modern, responsive UI components for Next.js using Tailwind CSS and shadcn/ui.
  This skill should be used when users want to create landing pages, marketing sites,
  dashboards, or any React UI with Next.js App Router. Builds accessible, performant
  components following modern patterns and best practices.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

# Next.js UI Pro

Generate modern, responsive UI components for Next.js using Tailwind CSS and shadcn/ui.

## What This Skill Does

- Creates landing pages, hero sections, feature grids, testimonials, CTAs
- Generates reusable UI components with shadcn/ui patterns
- Builds responsive layouts for all screen sizes
- Implements dark mode and theming
- Follows Next.js App Router best practices (Server/Client components)
- Ensures accessibility (ARIA, keyboard navigation, focus states)

## What This Skill Does NOT Do

- Set up hosting or deployment
- Create backend APIs or database schemas
- Handle authentication flows (use auth libraries)
- Generate full applications (builds components/pages)

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing components, theme config, tailwind.config, shadcn setup |
| **Conversation** | User's specific requirements, brand colors, content |
| **Skill References** | Component patterns from `references/` |
| **User Guidelines** | Design system, naming conventions |

---

## Clarifications (Ask User)

Ask before generating:

1. **What component/page?** - Hero, features, pricing, testimonials, contact?
2. **Content available?** - Headlines, descriptions, images, or use placeholders?
3. **Brand colors?** - Use existing theme or specific colors?
4. **Animations?** - Static, subtle transitions, or motion library?

---

## Generation Process

```
Analyze existing setup → Check shadcn components → Generate code → Validate
```

### Step 1: Check Project Setup

```
# Find existing components
Glob: **/components/**/*.tsx

# Check shadcn config
Glob: **/components.json

# Check Tailwind config
Glob: **/tailwind.config.*

# Find existing pages
Glob: **/app/**/page.tsx
```

### Step 2: Determine Component Strategy

| Scenario | Approach |
|----------|----------|
| shadcn installed | Use existing components from `@/components/ui` |
| No shadcn | Suggest installation or create standalone |
| Custom theme | Use CSS variables from `globals.css` |

### Step 3: Generate Files

1. **Check required shadcn components**
   - Run `npx shadcn@latest add <component>` if missing

2. **Create component file**
   - Place in `components/` or `components/sections/`
   - Use Server Components by default
   - Add "use client" only when needed

3. **Update page if needed**
   - Import and use component in `app/page.tsx`

---

## Server vs Client Components

**Default to Server Components** unless you need:

| Need Client? | Examples |
|--------------|----------|
| Yes | onClick, onChange, useState, useEffect |
| Yes | Browser APIs (window, localStorage) |
| Yes | Interactive animations (framer-motion) |
| No | Static content, data fetching |
| No | Mapping over data, conditional rendering |

```tsx
// Server Component (default) - no directive needed
export function HeroSection() {
  return <section>...</section>
}

// Client Component - needs directive
"use client"
export function ContactForm() {
  const [email, setEmail] = useState("")
  return <form>...</form>
}
```

---

## Output Structure

```
components/
├── ui/                    # shadcn components
│   ├── button.tsx
│   └── card.tsx
├── sections/              # Page sections
│   ├── hero.tsx
│   ├── features.tsx
│   └── testimonials.tsx
└── layout/                # Layout components
    ├── header.tsx
    └── footer.tsx
```

---

## Standards

| Standard | Implementation |
|----------|----------------|
| **Accessibility** | Semantic HTML, ARIA labels, focus visible |
| **Responsive** | Mobile-first, breakpoints (sm, md, lg, xl) |
| **Performance** | Server Components, next/image, lazy loading |
| **Types** | Full TypeScript with interfaces |
| **Styling** | Tailwind utilities, cn() for conditionals |
| **Dark Mode** | CSS variables, `dark:` variants |

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/landing-sections.md` | Hero, features, testimonials, CTA patterns |
| `references/components.md` | Reusable component patterns |
| `references/shadcn-patterns.md` | shadcn/ui usage and customization |
| `references/tailwind-patterns.md` | Tailwind utilities and responsive design |
| `references/layout.md` | Header, footer, navigation patterns |
| `references/forms.md` | Form components and validation |
| `references/animations.md` | CSS and Framer Motion animations |
| `references/theming.md` | Dark mode, CSS variables, colors |

---

## Quick Patterns

### cn() Utility (Required)
```tsx
import { cn } from "@/lib/utils"

<div className={cn(
  "base-classes",
  condition && "conditional-classes",
  className
)} />
```

### Responsive Container
```tsx
<div className="container mx-auto px-4 sm:px-6 lg:px-8">
  {children}
</div>
```

### Section Wrapper
```tsx
<section className="py-16 md:py-24 lg:py-32">
  <div className="container mx-auto px-4">
    {/* content */}
  </div>
</section>
```

### Button with Variants
```tsx
import { Button } from "@/components/ui/button"

<Button variant="default" size="lg">Get Started</Button>
<Button variant="outline">Learn More</Button>
```

---

## Checklist

Before completing, verify:

- [ ] Component is Server Component unless interactivity required
- [ ] Responsive on mobile, tablet, desktop
- [ ] Dark mode works (if theme enabled)
- [ ] Accessible (semantic HTML, ARIA, keyboard nav)
- [ ] TypeScript types defined
- [ ] Uses cn() for conditional classes
- [ ] Images use next/image
- [ ] No hardcoded colors (use theme variables)
