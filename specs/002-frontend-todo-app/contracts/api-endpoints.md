# API Contracts: Backend Endpoints

**Date**: 2026-02-07
**Feature**: 002-frontend-todo-app
**Backend Base URL**: `http://localhost:8000` (development)

## Overview

This document specifies the HTTP API contracts for the todo application. The frontend consumes these endpoints from the existing FastAPI backend.

**Authentication**: Deferred in current phase. All endpoints will eventually require `Authorization: Bearer <token>` header.

---

## Tasks API

### List Tasks

**Endpoint**: `GET /api/tasks`

**Query Parameters**:
- `filter` (optional): `all` | `pending` | `completed` (default: `all`)
- `page` (optional): Page number for pagination (default: 1)
- `page_size` (optional): Items per page (default: 50, max: 100)

**Request Headers**:
```http
Content-Type: application/json
Authorization: Bearer <token>  # Deferred
```

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "userId": "550e8400-e29b-41d4-a716-446655440001",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "createdAt": "2026-02-07T10:30:00Z",
      "updatedAt": "2026-02-07T10:30:00Z"
    }
  ],
  "total": 42
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token (when auth implemented)
- `500 Internal Server Error`: Database error

**Filtering Logic**:
- `filter=all`: Return all tasks for user
- `filter=pending`: Return tasks where `completed = false`
- `filter=completed`: Return tasks where `completed = true`

---

### Get Single Task

**Endpoint**: `GET /api/tasks/{id}`

**Path Parameters**:
- `id`: Task UUID

**Request Headers**:
```http
Content-Type: application/json
Authorization: Bearer <token>  # Deferred
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "userId": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "createdAt": "2026-02-07T10:30:00Z",
  "updatedAt": "2026-02-07T10:30:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Task belongs to different user
- `404 Not Found`: Task does not exist
- `500 Internal Server Error`: Database error

---

### Create Task

**Endpoint**: `POST /api/tasks`

**Request Headers**:
```http
Content-Type: application/json
Authorization: Bearer <token>  # Deferred
```

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"  // Optional
}
```

**Validation**:
- `title`: Required, 1-200 characters
- `description`: Optional, max 1000 characters

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "userId": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "createdAt": "2026-02-07T10:30:00Z",
  "updatedAt": "2026-02-07T10:30:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Validation error (missing title, too long, etc.)
- `401 Unauthorized`: Missing or invalid token
- `500 Internal Server Error`: Database error

**Idempotency**: Not idempotent. Multiple requests create multiple tasks.

---

### Update Task

**Endpoint**: `PATCH /api/tasks/{id}`

**Path Parameters**:
- `id`: Task UUID

**Request Headers**:
```http
Content-Type: application/json
Authorization: Bearer <token>  # Deferred
```

**Request Body** (all fields optional):
```json
{
  "title": "Buy groceries and cook dinner",
  "description": "Updated description",
  "completed": true
}
```

**Validation**:
- `title`: 1-200 characters (if provided)
- `description`: Max 1000 characters (if provided)
- `completed`: Boolean (if provided)

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "userId": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries and cook dinner",
  "description": "Updated description",
  "completed": true,
  "createdAt": "2026-02-07T10:30:00Z",
  "updatedAt": "2026-02-07T11:45:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Task belongs to different user
- `404 Not Found`: Task does not exist
- `500 Internal Server Error`: Database error

**Idempotency**: Idempotent. Multiple identical requests produce same result.

**Notes**:
- `updatedAt` timestamp is automatically updated by backend
- Partial updates supported (only send changed fields)

---

### Delete Task

**Endpoint**: `DELETE /api/tasks/{id}`

**Path Parameters**:
- `id`: Task UUID

**Request Headers**:
```http
Authorization: Bearer <token>  # Deferred
```

**Response** (204 No Content):
- Empty body

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Task belongs to different user
- `404 Not Found`: Task does not exist
- `500 Internal Server Error`: Database error

**Idempotency**: Idempotent. Deleting non-existent task returns 404 (not 204).

**Notes**:
- Hard delete (task permanently removed from database)
- No soft delete or "trash" functionality in this phase

---

## Authentication API (Deferred)

**Note**: These endpoints exist in the backend but are NOT implemented in frontend during this phase.

### Register

**Endpoint**: `POST /api/auth/register`

**Request Body**:
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepassword123"
}
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "email": "user@example.com",
  "name": "John Doe",
  "createdAt": "2026-02-07T10:00:00Z"
}
```

---

### Login

**Endpoint**: `POST /api/auth/login`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

---

## Error Response Format

All error responses follow this structure:

```json
{
  "error": "ValidationError",
  "message": "Title is required and must be 1-200 characters",
  "details": {
    "field": "title",
    "constraint": "length"
  },
  "statusCode": 400
}
```

**Common Error Types**:
- `ValidationError`: Input validation failed
- `AuthenticationError`: Missing or invalid token
- `AuthorizationError`: User lacks permission
- `NotFoundError`: Resource does not exist
- `InternalError`: Server error

---

## Rate Limiting

**Current Phase**: No rate limiting

**Future Consideration**:
- 100 requests/minute per user
- 429 Too Many Requests response
- `Retry-After` header

---

## CORS Configuration

**Allowed Origins** (development):
- `http://localhost:3000` (Next.js dev server)
- `http://localhost:8000` (FastAPI dev server)

**Allowed Methods**: GET, POST, PATCH, DELETE, OPTIONS

**Allowed Headers**: Content-Type, Authorization

**Credentials**: Allowed (for cookies/tokens)

---

## API Versioning

**Current Version**: No versioning (implicit v1)

**Future Strategy**:
- URL versioning: `/api/v2/tasks`
- Maintain backward compatibility for 6 months
- Deprecation notices in response headers

---

## Testing Endpoints

For local development and testing:

**Health Check**:
```http
GET /health
Response: {"status": "ok"}
```

**API Documentation**:
```http
GET /docs          # Swagger UI
GET /redoc         # ReDoc UI
GET /openapi.json  # OpenAPI schema
```

---

## Frontend Integration Notes

### Base URL Configuration

```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

### Environment Variables

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Timeout Configuration

- Default timeout: 10 seconds
- Long-running operations: 30 seconds
- Show loading spinner after 500ms

### Retry Logic

- Retry on 5xx errors: 3 attempts with exponential backoff
- No retry on 4xx errors (client error)
- Network errors: Retry 3 times

---

## Contract Testing

**Recommendation**: Implement contract tests to verify frontend/backend compatibility

**Example** (using MSW for mocking):
```typescript
// tests/mocks/handlers.ts
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/tasks', (req, res, ctx) => {
    return res(ctx.json({ tasks: [], total: 0 }));
  }),
];
```

**Validates**:
- Request/response structure matches types
- Status codes match documentation
- Error handling works correctly

---

## Summary

**Total Endpoints**: 5 (tasks) + 2 (auth, deferred)

**Required for MVP**:
- ✅ GET /api/tasks (with filter)
- ✅ GET /api/tasks/{id}
- ✅ POST /api/tasks
- ✅ PATCH /api/tasks/{id}
- ✅ DELETE /api/tasks/{id}

**Deferred**:
- ❌ POST /api/auth/register
- ❌ POST /api/auth/login

All endpoints are RESTful, use JSON, and return consistent error formats. Frontend API client will wrap these with TypeScript types from `data-model.md`.
