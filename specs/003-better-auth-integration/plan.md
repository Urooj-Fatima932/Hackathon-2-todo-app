# Implementation Plan: Better Auth JWT Integration for Task Management

**Branch**: `003-better-auth-integration` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-better-auth-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integrate Better Auth authentication library on Next.js frontend with JWT token-based authorization for FastAPI backend task management API. Users authenticate through Better Auth which issues HS256-signed JWT tokens containing user identity (user ID, email). The backend validates these tokens on every task API request to authorize user-specific CRUD operations (create, read, update, delete, toggle completion). All task data is isolated by user ownership, enforced through JWT token verification and decoded user identity claims.

## Technical Context

**Language/Version**:
- Frontend: TypeScript with Next.js 14 (App Router)
- Backend: Python 3.11+

**Primary Dependencies**:
- Frontend: Better Auth (authentication library), Next.js 14, React 18, Tailwind CSS
- Backend: FastAPI 0.115+, SQLModel 0.0.22, PyJWT 2.9.0, psycopg2-binary 2.9.9

**Storage**: PostgreSQL (Neon serverless) via SQLModel ORM

**Testing**:
- Frontend: Jest/React Testing Library (to be added)
- Backend: pytest (to be added)

**Target Platform**: Web application (browser-based frontend, Linux/containerized backend)

**Project Type**: Web (frontend + backend architecture)

**Performance Goals**:
- Task API responses <500ms p95 latency
- Authentication flow <1 second end-to-end
- Support 100+ concurrent users

**Constraints**:
- JWT tokens must use HS256 symmetric signing
- HTTPS enforced in production
- Shared secret between frontend and backend for JWT verification
- User data isolation enforced at database query level

**Scale/Scope**: MVP for 100-1000 users, extensible to 10k+ users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Constitution file contains template placeholders. Proceeding with standard best practices for web applications:

✅ **Test-First Development**: All new authentication and task authorization logic will have tests written before implementation (TDD cycle)

✅ **Security First**:
- JWT secrets stored in environment variables
- Password hashing enforced (bcrypt/argon2)
- HTTPS in production
- Authorization checks on every protected endpoint

✅ **Simplicity**:
- Direct database access via SQLModel (no repository pattern overhead for MVP)
- HS256 signing (simpler than RS256 for single-service architecture)
- RESTful API design (standard patterns)

✅ **Observability**: Structured logging for authentication events and authorization failures

**Status**: ✅ PASS - No violations detected

## Project Structure

### Documentation (this feature)

```text
specs/003-better-auth-integration/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── auth-api.yaml    # Authentication endpoints (Better Auth on frontend)
│   └── tasks-api.yaml   # Task management endpoints (FastAPI backend)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment configuration
│   ├── database.py             # Database connection/session
│   ├── models.py               # SQLModel database models (User, Task)
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt.py              # JWT token verification utilities (NEW)
│   │   └── dependencies.py     # FastAPI dependencies for auth (NEW)
│   ├── routes/
│   │   ├── __init__.py
│   │   └── tasks.py            # Task CRUD endpoints (MODIFY)
│   └── utils/
│       ├── __init__.py
│       └── exceptions.py        # Custom exception handlers
├── tests/
│   ├── test_auth.py            # JWT verification tests (NEW)
│   ├── test_tasks.py           # Task API integration tests (MODIFY)
│   └── conftest.py             # pytest fixtures (NEW)
├── requirements.txt            # Python dependencies (PyJWT already present)
└── .env.example                # Environment variables template

frontend/
├── app/
│   ├── (auth)/                 # Route group for auth pages (NEW)
│   │   ├── login/
│   │   │   └── page.tsx        # Login page
│   │   └── register/
│   │       └── page.tsx        # Registration page
│   ├── dashboard/              # Protected dashboard (NEW)
│   │   └── page.tsx            # Task list and management UI
│   ├── layout.tsx              # Root layout (MODIFY - add auth provider)
│   └── page.tsx                # Landing page
├── components/
│   ├── ui/                     # shadcn/ui components (existing)
│   ├── auth/                   # Auth-specific components (NEW)
│   │   ├── auth-provider.tsx   # Better Auth context provider
│   │   └── protected-route.tsx # Client component for route protection
│   └── tasks/                  # Task management components (NEW)
│       ├── task-list.tsx
│       ├── task-item.tsx
│       ├── task-form.tsx
│       └── task-dialog.tsx
├── lib/
│   ├── api.ts                  # API client with auth headers (MODIFY)
│   ├── auth.ts                 # Better Auth configuration (NEW)
│   └── utils.ts                # Utility functions
├── .env.local.example          # Environment variables template (NEW)
└── package.json                # Add better-auth dependency
```

**Structure Decision**: Web application with frontend/backend separation. Backend uses existing FastAPI structure with new auth module. Frontend follows Next.js App Router patterns with route groups for auth pages and protected dashboard. No monorepo tooling needed - simple dual-service architecture.

## Complexity Tracking

**No violations detected** - all choices follow standard practices for web applications with JWT authentication.

---

## Phase 0: Research & Technology Decisions

*Status: To be completed*

Research artifacts will document:
1. Better Auth configuration for Next.js 14 App Router
2. Better Auth JWT token generation setup
3. FastAPI JWT verification with PyJWT library
4. SQLModel User model with password hashing
5. Best practices for JWT secret management
6. Testing strategies for authenticated endpoints

**Output**: `research.md` with technology decisions and implementation patterns

---

## Phase 1: Design Artifacts

*Status: To be completed*

### 1. Data Model (`data-model.md`)

**Entities to define**:
- User: id (UUID), email (unique), hashed_password, created_at, updated_at
- Task: id (UUID), user_id (FK to User), title, description (optional), is_completed (boolean), created_at, updated_at

**Relationships**: Task belongs_to User (enforced via foreign key + query filters)

### 2. API Contracts (`contracts/`)

**auth-api.yaml** (Frontend Better Auth):
- POST /api/auth/register - User registration
- POST /api/auth/login - User login (returns JWT)
- POST /api/auth/logout - User logout
- GET /api/auth/session - Get current session

**tasks-api.yaml** (Backend FastAPI):
- GET /api/tasks - List all tasks for authenticated user
- POST /api/tasks - Create new task
- GET /api/tasks/{task_id} - Get task details (ownership check)
- PATCH /api/tasks/{task_id} - Update task (ownership check)
- DELETE /api/tasks/{task_id} - Delete task (ownership check)
- POST /api/tasks/{task_id}/toggle - Toggle completion status (ownership check)

All backend endpoints require `Authorization: Bearer <jwt_token>` header.

### 3. Quickstart Guide (`quickstart.md`)

Developer setup instructions:
- Backend: Install dependencies, configure DATABASE_URL and JWT_SECRET, run migrations, start server
- Frontend: Install dependencies, configure NEXT_PUBLIC_API_URL and BETTER_AUTH_SECRET, run dev server
- Testing: Instructions for running backend tests with pytest and frontend tests

**Output**: `data-model.md`, `contracts/*.yaml`, `quickstart.md`

---

## Phase 2: Tasks Generation

*Status: Not started (will be created by `/sp.tasks` command)*

**Prerequisites**: Phase 0 and Phase 1 complete

Tasks will cover:
- Backend: User model, JWT verification, auth dependencies, task authorization
- Frontend: Better Auth setup, auth pages, protected routes, task UI components
- Integration: End-to-end authentication flow, task CRUD with authorization
- Testing: Unit tests for JWT verification, integration tests for protected endpoints

**Output**: `tasks.md` with prioritized, testable implementation tasks

---

## Risk Analysis

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Better Auth and FastAPI JWT token mismatch | High - authentication breaks | Document exact JWT payload format in contracts, add integration tests |
| Shared secret management across services | High - security vulnerability if exposed | Use environment variables, document rotation procedure, add .env.example files |
| SQLModel schema migrations | Medium - data loss risk | Document migration commands, use Alembic for versioning, backup before migrations |
| Frontend token storage | Medium - XSS vulnerability | Better Auth handles secure storage (httpOnly cookies recommended) |
| Task ownership enforcement gaps | High - data leak | Add database-level foreign key constraints + application-level checks, test thoroughly |

### Implementation Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking changes to existing task routes | High - breaks existing frontend | Version API or add backwards compatibility layer, coordinate frontend/backend updates |
| Better Auth learning curve | Medium - delays delivery | Research phase includes Better Auth documentation review, start with minimal config |
| Testing authenticated endpoints complexity | Medium - inadequate test coverage | Create pytest fixtures for auth tokens, document testing patterns in quickstart |

---

## Dependencies & Assumptions

### External Dependencies
- Better Auth library compatibility with Next.js 14 App Router
- PyJWT library for HS256 token verification
- PostgreSQL/Neon database availability
- Shared network access between frontend and backend services

### Assumptions
- Existing backend has SQLModel configured with database connection
- Existing frontend has Next.js 14 App Router and Tailwind CSS set up
- PyJWT (2.9.0) is already in requirements.txt
- No existing authentication system to migrate from
- Development and production environments have separate JWT secrets
- Frontend and backend are deployed with CORS properly configured

### Blocking Dependencies
- Database must be accessible before user/task models can be tested
- JWT_SECRET environment variable must be configured before authentication works
- Better Auth must be installed before frontend auth pages function

---

## Next Steps

1. ✅ **Complete this plan** - Document technical decisions and architecture
2. **Phase 0: Research** - Create research.md with Better Auth + PyJWT patterns
3. **Phase 1: Design** - Generate data-model.md, API contracts, quickstart guide
4. **Phase 2: Tasks** - Run `/sp.tasks` to generate implementation tasks
5. **Implementation** - Execute tasks following TDD (red-green-refactor)
6. **Testing** - Verify all acceptance scenarios from spec.md
7. **Documentation** - Update README with authentication setup instructions

---

## ADR Candidates

The following decisions may warrant Architecture Decision Records:

1. **JWT Token Signing Algorithm Choice (HS256 vs RS256)**
   - Decision: HS256 symmetric signing
   - Context: Single backend service, simpler key management
   - Tradeoff: Less flexible for microservices, but adequate for current architecture
   - *Suggested ADR Title*: "Use HS256 for JWT Signing in MVP"

2. **Better Auth Frontend vs Backend-Only Authentication**
   - Decision: Better Auth on frontend (Next.js) generating JWT
   - Context: User experience requires frontend session management
   - Tradeoff: More complex than backend-only, but better UX and aligns with spec
   - *Suggested ADR Title*: "Frontend Authentication with Better Auth"

3. **Direct Database Queries vs Repository Pattern**
   - Decision: Direct SQLModel queries for MVP
   - Context: Small codebase, clear ownership model
   - Tradeoff: Less abstraction, but simpler and faster to implement
   - *Suggested ADR Title*: "Direct Database Access for Task Ownership"

**Note**: Run `/sp.adr <title>` to create ADRs for any of these decisions after user approval.
