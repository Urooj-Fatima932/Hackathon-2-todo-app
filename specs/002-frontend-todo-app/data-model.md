# Data Model: Frontend Todo Web Application

**Date**: 2026-02-07
**Feature**: 002-frontend-todo-app
**Phase**: 1 - Data Model Definition

## Overview

This document defines the TypeScript interfaces and data structures for the frontend application. These types mirror the backend SQLModel schemas and ensure type safety across the API boundary.

---

## Core Entities

### User

Represents a registered user of the application.

```typescript
interface User {
  id: string;           // UUID from backend
  email: string;        // User's email address
  name: string;         // User's display name
  createdAt: string;    // ISO 8601 timestamp
}
```

**Validation Rules**:
- `email`: Must be valid email format
- `name`: 1-100 characters
- `id`: UUID v4 format

**State Transitions**: None (user is created and read-only in frontend)

**Notes**:
- Authentication deferred in this phase
- Frontend will assume a mock user for development

---

### Task

Represents a single todo item.

```typescript
interface Task {
  id: string;              // UUID from backend
  userId: string;          // Foreign key to User
  title: string;           // Task title
  description?: string;    // Optional detailed description
  completed: boolean;      // Completion status
  createdAt: string;       // ISO 8601 timestamp
  updatedAt: string;       // ISO 8601 timestamp
}
```

**Validation Rules**:
- `title`: Required, 1-200 characters
- `description`: Optional, max 1000 characters
- `completed`: Boolean (default: false)
- `userId`: Must match authenticated user (enforced by backend)

**State Transitions**:
```
[New] --create--> [Pending] --toggle--> [Completed] --toggle--> [Pending]
                      |                                            |
                      +------------------delete------------------+
```

**Business Rules**:
- Tasks can only be created by authenticated users
- Users can only view/edit/delete their own tasks
- Soft delete not implemented (hard delete only)
- Completed tasks remain visible (can be filtered out)

---

## API Request/Response Types

### CreateTaskRequest

```typescript
interface CreateTaskRequest {
  title: string;
  description?: string;
}
```

**Usage**: `POST /api/tasks`

---

### UpdateTaskRequest

```typescript
interface UpdateTaskRequest {
  title?: string;
  description?: string;
  completed?: boolean;
}
```

**Usage**: `PATCH /api/tasks/{id}`

**Notes**: All fields optional (partial update)

---

### TaskListResponse

```typescript
interface TaskListResponse {
  tasks: Task[];
  total: number;
  page?: number;       // If pagination implemented
  pageSize?: number;   // If pagination implemented
}
```

**Usage**: `GET /api/tasks?filter=all|pending|completed`

---

### ApiError

```typescript
interface ApiError {
  error: string;         // Error type (e.g., "ValidationError")
  message: string;       // Human-readable message
  details?: unknown;     // Optional additional context
  statusCode: number;    // HTTP status code
}
```

**Usage**: Returned by API client on error responses

---

## Derived Types

### TaskFilter

```typescript
type TaskFilter = 'all' | 'pending' | 'completed';
```

**Usage**: URL search params for filtering tasks

**Behavior**:
- `all`: Show all tasks
- `pending`: Show tasks where `completed === false`
- `completed`: Show tasks where `completed === true`

---

### TaskFormData

```typescript
interface TaskFormData {
  title: string;
  description: string;
}
```

**Usage**: Form state for create/edit dialogs

**Validation**:
- Client-side validation before submission
- Matches backend validation rules

---

## Client-Side State Types

### OptimisticTask

```typescript
interface OptimisticTask extends Task {
  pending?: boolean;     // True while server request in flight
  error?: string;        // Error message if operation failed
}
```

**Usage**: For optimistic UI updates

**Behavior**:
- `pending: true` → show loading indicator on task card
- `error` → show error state, provide retry option

---

### UIState

```typescript
interface UIState {
  isCreateDialogOpen: boolean;
  editingTaskId: string | null;
  isLoading: boolean;
  error: string | null;
}
```

**Usage**: Global UI state (managed by Context or local state)

---

## File Locations

All type definitions will be located in:

```
frontend/lib/types.ts          # Core entities (User, Task, etc.)
frontend/lib/api-types.ts      # Request/response types
frontend/lib/ui-types.ts       # UI-specific types (optional)
```

**Import Example**:
```typescript
import { Task, CreateTaskRequest } from '@/lib/types';
```

---

## Validation Schema

While TypeScript provides compile-time type safety, runtime validation is handled by:

1. **Backend**: FastAPI Pydantic models (authoritative)
2. **Frontend**: Form validation libraries (e.g., zod) - optional for this phase
3. **API Client**: Type guards for response validation

**Example Type Guard**:
```typescript
function isTask(obj: unknown): obj is Task {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'title' in obj &&
    'completed' in obj
  );
}
```

---

## Relationships

```
User (1) ----< (many) Task
```

- One user has many tasks
- Each task belongs to exactly one user
- Enforced by backend via `userId` foreign key

**Frontend Handling**:
- Frontend does not manage users (auth deferred)
- All tasks fetched via `/api/tasks` are scoped to authenticated user
- No need to filter by `userId` on frontend

---

## Migration Notes

**Current State**: No existing frontend types

**Changes Required**:
1. Create `frontend/lib/types.ts` with interfaces above
2. Import in API client (`lib/api.ts`)
3. Import in components as needed

**Backward Compatibility**: N/A (new feature)

---

## Testing Considerations

**Mock Data**:
```typescript
export const mockUser: User = {
  id: '00000000-0000-0000-0000-000000000001',
  email: 'test@example.com',
  name: 'Test User',
  createdAt: '2026-02-07T00:00:00Z',
};

export const mockTasks: Task[] = [
  {
    id: '00000000-0000-0000-0000-000000000002',
    userId: mockUser.id,
    title: 'Sample Task',
    description: 'This is a sample task',
    completed: false,
    createdAt: '2026-02-07T10:00:00Z',
    updatedAt: '2026-02-07T10:00:00Z',
  },
];
```

**Usage**: Component tests, Storybook, local development

---

## Performance Considerations

**Large Task Lists** (>1000 tasks):
- Frontend should handle up to 1000 tasks per user
- If backend returns more, implement:
  - Virtual scrolling (react-window)
  - Pagination (page size: 50)
  - Infinite scroll

**Optimization**:
- Memoize task list components
- Debounce filter changes
- Use React.memo for TaskCard

---

## Security Notes

- **XSS Prevention**: All user input (title, description) must be sanitized
  - React automatically escapes text content
  - Avoid `dangerouslySetInnerHTML`
- **CSRF**: Not applicable (auth deferred)
- **Data Exposure**: All task data visible to owner only (enforced by backend)

---

## Summary

This data model establishes:
- 2 core entities: User, Task
- 4 request/response types for API calls
- 2 derived types for filtering and forms
- Type safety across frontend-backend boundary
- Foundation for API client implementation (next step)

All types align with backend SQLModel schemas in `backend/app/models.py`.
