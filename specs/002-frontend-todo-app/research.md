# Research: Frontend Todo Web Application

**Date**: 2026-02-07
**Feature**: 002-frontend-todo-app
**Phase**: 0 - Research & Best Practices

## Research Areas

### 1. Next.js 14 App Router Best Practices

**Research Task**: Identify optimal patterns for server components, client components, and data fetching in App Router.

**Findings**:

**Decision**: Use Server Components by default; Client Components only for interactive UI
- Server Components for: layouts, static content, data fetching
- Client Components for: forms, buttons, interactive elements (use `'use client'` directive)
- Co-locate Server and Client components in same directory

**Rationale**:
- Reduces JavaScript bundle size
- Improves initial page load performance
- Server Components can directly access backend APIs
- Better SEO for landing page

**Alternatives Considered**:
- Pages Router: Rejected (older pattern, less performant)
- Client-only rendering: Rejected (worse SEO, larger bundles)

**Implementation Guidelines**:
```tsx
// Server Component (default) - no 'use client' needed
export default async function TasksPage() {
  const tasks = await fetchTasks(); // Server-side fetch
  return <TaskList tasks={tasks} />;
}

// Client Component - needs 'use client'
'use client';
export function TaskForm({ onSubmit }) {
  const [title, setTitle] = useState('');
  // Interactive form logic
}
```

---

### 2. State Management Approach

**Research Task**: Determine state management strategy for task list, filters, and optimistic updates.

**Findings**:

**Decision**: Use React Server Actions + URL state for filters; React Context for client-side state
- Server Actions for mutations (create, update, delete tasks)
- URL search params for filter state (enables shareable links)
- React Context for temporary UI state (modals, form state)
- No Redux/Zustand needed for this scope

**Rationale**:
- Server Actions integrate natively with Next.js 14
- URL state is shareable and bookmarkable
- Reduces dependency bloat
- Built-in revalidation with `revalidatePath()`

**Alternatives Considered**:
- Redux Toolkit: Rejected (overkill for scope, adds complexity)
- Zustand: Rejected (unnecessary for server-heavy approach)
- SWR/React Query: Rejected (Server Actions + cache handles it)

**Implementation Guidelines**:
```tsx
// Server Action for task creation
'use server';
export async function createTask(formData: FormData) {
  const task = await api.post('/tasks', { title: formData.get('title') });
  revalidatePath('/tasks');
  return task;
}

// URL-based filtering
export default function TasksPage({ searchParams }) {
  const filter = searchParams.filter || 'all'; // from URL: /tasks?filter=completed
  // ...
}
```

---

### 3. API Client Design

**Research Task**: Design API client for backend communication with error handling and type safety.

**Findings**:

**Decision**: Create typed API client with fetch wrapper, error boundaries, and retry logic
- Centralized `lib/api.ts` for all backend calls
- TypeScript interfaces matching backend schemas
- Consistent error handling with toast notifications
- Bearer token support (prepared for auth, but not used yet)

**Rationale**:
- Single source of truth for API calls
- Type safety across frontend-backend boundary
- Easy to mock for testing
- Prepared for auth integration later

**Alternatives Considered**:
- Direct fetch calls: Rejected (code duplication, inconsistent error handling)
- Axios: Rejected (fetch is native, sufficient for needs)
- tRPC: Rejected (requires backend changes, overkill)

**Implementation Guidelines**:
```typescript
// lib/api.ts
class ApiClient {
  private baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  async get<T>(endpoint: string): Promise<T> {
    const res = await fetch(`${this.baseURL}${endpoint}`, {
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
  }

  // Similar for post, put, delete...
}

export const api = new ApiClient();
```

---

### 4. Optimistic UI Updates

**Research Task**: Implement optimistic updates for task operations to meet <500ms UI response requirement.

**Findings**:

**Decision**: Use `useOptimistic` hook + Server Actions for instant UI feedback
- Immediately update UI on user action
- Revert if server request fails
- Show loading states for network operations
- Success/error toasts for user feedback

**Rationale**:
- Meets <500ms requirement (instant visual feedback)
- Improved perceived performance
- Native Next.js 14 pattern with `useOptimistic`

**Alternatives Considered**:
- Wait for server response: Rejected (slow, violates requirements)
- Manual state sync: Rejected (error-prone, complex)

**Implementation Guidelines**:
```tsx
'use client';
import { useOptimistic } from 'react';

export function TaskList({ tasks }) {
  const [optimisticTasks, addOptimisticTask] = useOptimistic(
    tasks,
    (state, newTask) => [...state, { ...newTask, pending: true }]
  );

  async function handleCreate(formData) {
    addOptimisticTask({ title: formData.get('title'), id: 'temp' });
    await createTask(formData); // Server Action
  }

  return (/* render optimisticTasks */);
}
```

---

### 5. Styling & Component Library

**Research Task**: Select UI component library and styling approach aligned with Tailwind CSS.

**Findings**:

**Decision**: Tailwind CSS + shadcn/ui for base components
- Tailwind for all styling (utility-first)
- shadcn/ui for complex components (dialogs, dropdowns, forms)
- No component library dependencies (shadcn copies code into project)
- Custom components for domain-specific UI (TaskCard, TaskForm)

**Rationale**:
- Already specified in `frontend/CLAUDE.md`
- shadcn/ui is copy-paste (no runtime dependency)
- Highly customizable, accessible by default
- Smaller bundle than Material-UI or Chakra

**Alternatives Considered**:
- Material-UI: Rejected (heavy, opinionated styles)
- Chakra UI: Rejected (runtime CSS-in-JS overhead)
- Headless UI: Considered (lightweight, but shadcn provides more)

**Implementation Guidelines**:
- Install shadcn/ui: `npx shadcn-ui@latest init`
- Add components as needed: `npx shadcn-ui@latest add button dialog form`
- All custom styles via Tailwind classes
- No `className` prop overrides on shadcn components

---

### 6. Landing Page Design Patterns

**Research Task**: Identify effective landing page structure for todo app.

**Findings**:

**Decision**: Hero section + Features + CTA structure
- Hero: Value proposition, screenshot/demo, primary CTA ("Get Started")
- Features: 3-4 key benefits with icons (Fast, Simple, Organized)
- Social Proof: Optional testimonials or stats (can be mocked)
- Footer: Links, privacy policy placeholder

**Rationale**:
- Industry standard for SaaS apps
- Clear conversion funnel
- Mobile-responsive by default with Tailwind
- Quick to implement

**Alternatives Considered**:
- Video hero: Rejected (adds complexity, not in scope)
- Multi-page marketing site: Rejected (scope limited to single landing page)

**Implementation Guidelines**:
```tsx
// app/(marketing)/page.tsx
export default function LandingPage() {
  return (
    <>
      <Hero />
      <Features />
      <CTA />
      <Footer />
    </>
  );
}
```

---

### 7. Error Handling & Loading States

**Research Task**: Design error boundaries and loading UIs for optimal UX.

**Findings**:

**Decision**: Next.js built-in error.tsx + loading.tsx + toast notifications
- `error.tsx` for route-level error boundaries
- `loading.tsx` for Suspense fallbacks
- `react-hot-toast` for user-facing messages
- Retry buttons on error states

**Rationale**:
- Native Next.js patterns
- Consistent UX across all pages
- Minimal setup required

**Alternatives Considered**:
- react-error-boundary: Rejected (Next.js has built-in)
- Custom error components: Rejected (reinventing wheel)

**Implementation Guidelines**:
```tsx
// app/tasks/error.tsx
'use client';
export default function Error({ error, reset }) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  );
}

// app/tasks/loading.tsx
export default function Loading() {
  return <Skeleton />;
}
```

---

## Technology Stack Summary

| Layer | Technology | Version | Justification |
|-------|-----------|---------|---------------|
| Framework | Next.js | 14.x (App Router) | Modern, performant, great DX |
| Language | TypeScript | 5.x | Type safety, better tooling |
| Styling | Tailwind CSS | 3.x | Utility-first, fast, customizable |
| Components | shadcn/ui | Latest | Accessible, no runtime deps |
| State | React Server Actions | Built-in | Native Next.js 14 pattern |
| API Client | fetch (wrapped) | Native | Sufficient, no extra deps |
| Notifications | react-hot-toast | Latest | Lightweight, good UX |
| Testing | Jest + RTL + Playwright | Latest | Industry standard |

---

## Dependencies to Install

```json
{
  "dependencies": {
    "next": "^14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-hot-toast": "^2.4.1"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "eslint": "^8.56.0",
    "eslint-config-next": "^14.1.0"
  }
}
```

**shadcn/ui** will be added via CLI (no package dependency).

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Backend API changes | High | Define TypeScript interfaces early; coordinate with backend team |
| Performance on large task lists | Medium | Implement virtualization if >1000 tasks; pagination as fallback |
| Auth integration later | Medium | Design API client with token support; use mock user for now |
| Browser compatibility | Low | Target modern browsers only (last 2 versions) |

---

## Next Steps (Phase 1)

With research complete, proceed to:
1. **data-model.md**: Define TypeScript interfaces for Task, User, API responses
2. **contracts/**: Document API endpoints (GET /tasks, POST /tasks, etc.)
3. **quickstart.md**: Setup instructions for local development
4. **Update agent context**: Add Next.js 14 + Tailwind to .claude/ or .gemini/ context

All NEEDS CLARIFICATION items resolved. Ready for Phase 1 design.
