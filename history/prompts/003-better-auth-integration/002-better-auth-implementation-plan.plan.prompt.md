---
id: 002
title: Better Auth Implementation Plan
stage: plan
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: 003-better-auth-integration
branch: 003-better-auth-integration
user: Saqlain
command: /sp.plan
labels: ["planning", "architecture", "better-auth", "jwt", "research"]
links:
  spec: specs/003-better-auth-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-better-auth-integration/plan.md
  - specs/003-better-auth-integration/research.md
tests:
  - Validation: Technical context complete with no NEEDS CLARIFICATION markers
  - Constitution check: PASS - no violations detected
---

## Prompt

create a plan.md for spec.md

## Response snapshot

Created comprehensive implementation plan and research artifacts for Better Auth JWT integration:

**plan.md (302 lines)**:
- **Summary**: Better Auth on Next.js frontend issues HS256 JWT tokens, FastAPI backend verifies tokens for user-specific task CRUD operations
- **Technical Context**: Fully defined - Next.js 14/TypeScript frontend, Python 3.11+/FastAPI backend, PostgreSQL/Neon storage, PyJWT already in requirements.txt
- **Constitution Check**: ✅ PASSED - follows test-first development, security best practices, simplicity principles
- **Project Structure**: Detailed file tree for both frontend and backend with NEW/MODIFY markers
  - Backend: `app/auth/jwt.py`, `app/auth/dependencies.py`, modify `routes/tasks.py`
  - Frontend: `app/(auth)/`, `components/auth/`, `lib/auth.ts`, task components
- **Risk Analysis**: 5 technical risks + 3 implementation risks with mitigations documented
- **ADR Candidates**: 3 significant architectural decisions identified (HS256 algorithm, frontend auth, direct DB access)

**research.md (complete)**:
Six research areas fully documented with Decision/Rationale/Alternatives/Implementation Notes:

1. **Better Auth Configuration**: Next.js 14 App Router setup, JWT generation with HS256, session management patterns, code examples for `lib/auth.ts` and auth provider
2. **FastAPI JWT Verification**: PyJWT usage, dependency injection pattern for `get_current_user`, error handling, code examples for `app/auth/jwt.py` and `app/auth/dependencies.py`
3. **SQLModel User Model**: User and Task models with UUID primary keys, password hashing with passlib[bcrypt], code examples for models and password utilities
4. **JWT Secret Management**: Environment variable patterns, secret generation commands, rotation procedure, CRITICAL note that JWT_SECRET must match between frontend and backend
5. **Testing Authenticated Endpoints**: pytest fixtures for test JWT tokens, `authenticated_client` fixture, code examples for testing authorization enforcement
6. **JWT Payload Structure**: Standardized format with `sub` (user ID), `email`, `iat`, `exp` claims for interoperability

**Key Technical Decisions**:
- HS256 symmetric signing (simpler for single-service architecture)
- Better Auth handles frontend session, FastAPI verifies tokens
- passlib[bcrypt] for password hashing (industry standard)
- Environment variables for secrets (12-factor app pattern)
- pytest fixtures with real JWTs (test actual verification code paths)

**Project Status**:
- ✅ Phase 0 (Research): COMPLETE
- 🔄 Phase 1 (Design): Ready to start - need data-model.md, contracts/, quickstart.md
- ⏳ Phase 2 (Tasks): Blocked until Phase 1 complete

## Outcome

- ✅ Impact: Complete architectural plan with 302-line plan.md + comprehensive research.md covering all integration patterns
- 🧪 Tests: Constitution check PASSED, no violations, test-first development enforced
- 📁 Files: plan.md (complete), research.md (complete, 6 topics documented)
- 🔁 Next prompts: Continue with Phase 1 design artifacts (data-model.md, contracts/, quickstart.md), then `/sp.tasks`
- 🧠 Reflection: Successfully identified PyJWT already in requirements.txt, eliminating one dependency. Research phase provided concrete code examples to accelerate implementation. Identified 3 ADR candidates for user approval.

## Evaluation notes (flywheel)

- Failure modes observed: Initial constitution was template placeholders; resolved by applying standard web app best practices for gates
- Graders run and results (PASS/FAIL): Constitution check PASS, Technical context completeness PASS (zero NEEDS CLARIFICATION), Research depth PASS (6 topics with code examples)
- Prompt variant (if applicable): Standard /sp.plan workflow with embedded Phase 0 research completion
- Next experiment (smallest change to try): Monitor if separate frontend/backend JWT secrets cause issues; consider documenting in ADR the requirement for shared secret in HS256 symmetric architecture
