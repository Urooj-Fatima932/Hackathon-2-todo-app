---
name: fastapi-nextjs-jwt-auth
description: |
  Implements JWT authentication for full-stack apps with Next.js 14+ frontend and FastAPI backend.
  Uses bcrypt for password hashing, PyJWT for token signing, and localStorage for client token storage.
  This skill should be used when users need email/password authentication with protected API routes.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

# FastAPI + Next.js JWT Authentication

Implement production-ready JWT authentication across Next.js frontend and FastAPI backend.

## What This Skill Does

- Creates User model with SQLModel (UUID, email, hashed_password, name, timestamps)
- Implements secure password hashing with bcrypt (with 72-byte truncation fix)
- Creates JWT token utilities with HS256 signing
- Generates FastAPI auth endpoints (register, login)
- Creates `get_current_user` dependency for protected routes
- Builds AuthProvider context for React with localStorage token storage
- Creates login/register pages in Next.js (auth) route group
- Updates API client to automatically add Authorization Bearer headers
- Updates Navigation to show auth state

## What This Skill Does NOT Do

- OAuth providers (Google, GitHub, etc.)
- Refresh tokens (uses single access token with 24h expiry)
- Email verification
- Password reset flow
- Two-factor authentication
- Role-based access control

---

## Before Implementation

Gather context:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing models, routes, frontend structure |
| **Conversation** | Additional user fields, token expiry, protected routes |
| **Skill References** | Code templates from `references/` and `templates/` |

---

## Clarifications (Ask User)

1. **Additional user fields?** - Beyond email, name, password?
2. **Token expiry?** - Default 24 hours, need different?
3. **Protected routes?** - Which frontend routes require auth?

---

## Architecture

```
┌─────────────────┐    HTTP + JWT    ┌─────────────────┐        ┌──────────────┐
│   Next.js       │◄────────────────►│   FastAPI       │◄──────►│  PostgreSQL  │
│   Frontend      │                  │   Backend       │        │  (Neon)      │
└─────────────────┘                  └─────────────────┘        └──────────────┘
     │                                     │
     │ localStorage                        │ bcrypt + PyJWT
     │ - auth_token                        │ - hash passwords
     │ - auth_user                         │ - sign/verify JWT
     └─────────────────────────────────────┘
```

## Auth Flow

```
1. User submits email/password
2. Frontend calls POST /api/auth/login or /api/auth/register
3. Backend verifies credentials, creates JWT with user_id + email
4. Frontend stores token in localStorage
5. All API requests include Authorization: Bearer <token>
6. Backend validates JWT, extracts user, returns user-specific data
```

---

## Critical Implementation Details

### ⚠️ Password Hashing - USE BCRYPT DIRECTLY

**DO NOT use passlib** - it has compatibility issues with newer bcrypt versions.

```python
# ❌ WRONG - causes "password cannot be longer than 72 bytes" error
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"])

# ✅ CORRECT - use bcrypt directly with truncation
import bcrypt

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]  # CRITICAL: truncate to 72 bytes
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')[:72]
    return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
```

### ⚠️ Field Naming Convention

Backend uses **snake_case**, frontend must match:

```typescript
// ✅ CORRECT - match backend field names
interface Task {
  id: string;
  user_id: string;
  is_completed: boolean;  // NOT "isCompleted"
  created_at: string;     // NOT "createdAt"
}
```

### ⚠️ Handle 401 on Frontend

Clear token and redirect when unauthorized:

```typescript
if (response.status === 401) {
  localStorage.removeItem("auth_token");
  localStorage.removeItem("auth_user");
  window.location.href = "/login";
}
```

---

## File Generation Order

```
1. Backend auth module (password.py, jwt.py, dependencies.py)
2. Backend schemas (UserCreate, UserLogin, TokenResponse)
3. Backend auth routes (/api/auth/register, /api/auth/login)
4. Update backend main.py (register auth router)
5. Frontend auth context (lib/auth/context.tsx)
6. Frontend API client (add auth headers)
7. Frontend auth pages (login, register)
8. Frontend layout (wrap with AuthProvider)
9. Update protected routes
10. Update navigation
```

---

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@host/db
JWT_SECRET=your-super-secret-32-char-minimum-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Dependencies

### Backend (requirements.txt)
```
fastapi>=0.115.0
uvicorn[standard]>=0.31.0
sqlmodel>=0.0.22
psycopg2-binary>=2.9.9
pydantic>=2.9.0
pydantic-settings>=2.5.0
PyJWT>=2.9.0
bcrypt>=4.0.0
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "react-hot-toast": "^2.4.0"
  }
}
```

---

## Reference Files

| File | Content |
|------|---------|
| `references/backend-auth.md` | Complete backend auth implementation |
| `references/frontend-auth.md` | Complete frontend auth implementation |
| `references/common-errors.md` | Error fixes and troubleshooting |
| `templates/backend/` | Ready-to-use Python files |
| `templates/frontend/` | Ready-to-use TypeScript files |

---

## Quick Implementation Checklist

### Backend
- [ ] Create `app/auth/__init__.py`
- [ ] Create `app/auth/password.py` (bcrypt with 72-byte truncation)
- [ ] Create `app/auth/jwt.py` (verify_jwt_token, extract_user_from_token)
- [ ] Create `app/auth/dependencies.py` (get_current_user)
- [ ] Add UserCreate, UserLogin, TokenResponse to `schemas.py`
- [ ] Add User model with hashed_password field to `models.py`
- [ ] Create `app/routes/auth.py` (register, login endpoints)
- [ ] Register auth router in `main.py`
- [ ] Add JWT_SECRET to `.env`
- [ ] Update config to load JWT settings
- [ ] Update task routes to use `get_current_user` dependency

### Frontend
- [ ] Create `lib/auth/context.tsx` (AuthProvider)
- [ ] Update `lib/api.ts` (add auth headers, handle 401)
- [ ] Update `lib/types.ts` (add auth types, snake_case fields)
- [ ] Create `app/(auth)/login/page.tsx`
- [ ] Create `app/(auth)/register/page.tsx`
- [ ] Create `app/(auth)/layout.tsx` (redirect if authenticated)
- [ ] Update `app/layout.tsx` (wrap with AuthProvider)
- [ ] Update `components/Navigation.tsx` (show auth state)
- [ ] Update protected pages to check auth and redirect

### Database
- [ ] Run migration to add/update users table with hashed_password column
