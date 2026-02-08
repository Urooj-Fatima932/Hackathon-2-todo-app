# Tasks: Better Auth JWT Integration for Task Management

**Input**: Design documents from `/specs/003-better-auth-integration/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5, US6)
- All file paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, environment configuration, and dependency installation

- [ ] T001 Install Better Auth in frontend: `cd frontend && npm install better-auth`
- [x] T002 [P] Install passlib for password hashing in backend: `cd backend && pip install 'passlib[bcrypt]'`
- [x] T003 [P] Create backend environment variables template in `backend/.env.example` with JWT_SECRET, DATABASE_URL
- [x] T004 [P] Create frontend environment variables template in `frontend/.env.local.example` with BETTER_AUTH_SECRET, DATABASE_URL, NEXT_PUBLIC_API_URL
- [ ] T005 Generate secure JWT secret and configure in backend/.env and frontend/.env.local (must be identical)

**Checkpoint**: Dependencies installed, environment configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core authentication infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [x] T006 Create User model in `backend/app/models.py` with id (UUID), email (unique), hashed_password, created_at, updated_at
- [x] T007 Create Task model in `backend/app/models.py` with id (UUID), user_id (FK to users.id), title, description, is_completed, created_at, updated_at
- [x] T008 [P] Create password hashing utilities in `backend/app/auth/password.py` with hash_password() and verify_password() using passlib/bcrypt
- [x] T009 [P] Create JWT verification utilities in `backend/app/auth/jwt.py` with verify_jwt_token() and extract_user_from_token()
- [x] T010 Create get_current_user dependency in `backend/app/auth/dependencies.py` using FastAPI HTTPBearer and JWT verification
- [x] T011 Update config in `backend/app/config.py` to load JWT_SECRET from environment with pydantic-settings
- [ ] T012 Run database migrations to create users and tasks tables with SQLModel

### Frontend Foundation

- [x] T013 [P] Create Better Auth configuration in `frontend/lib/auth/context.tsx` with auth state management and token storage
- [x] T014 [P] Create AuthProvider component in `frontend/lib/auth/context.tsx` with login/register/logout functions
- [x] T015 [P] Update API client in `frontend/lib/api.ts` to add Authorization Bearer header from stored token
- [x] T016 Wrap root layout in `frontend/app/layout.tsx` with AuthProvider component

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Authentication (Priority: P1) 🎯 MVP

**Goal**: Users can register accounts, log in with email/password, and receive JWT tokens for API access

**Independent Test**: Register new account → Login with credentials → Receive JWT token → Make authenticated API request → Backend identifies user

### Backend Implementation for US1

- [x] T017 [P] [US1] Create user registration schema in `backend/app/schemas.py` with UserCreate (email, password validation)
- [x] T018 [P] [US1] Create user response schema in `backend/app/schemas.py` with UserResponse (id, email, created_at)
- [x] T019 [US1] Create user registration endpoint POST /api/auth/register in `backend/app/routes/auth.py` with email uniqueness check and password hashing
- [x] T020 [US1] Add authentication error handling in `backend/app/utils/exceptions.py` for invalid credentials, duplicate email
- [x] T021 [US1] Add logging for authentication events (registration, login attempts) in auth routes

### Frontend Implementation for US1

- [x] T022 [P] [US1] Create registration page in `frontend/app/(auth)/register/page.tsx` with email/password form
- [x] T023 [P] [US1] Create login page in `frontend/app/(auth)/login/page.tsx` with email/password form
- [x] T024 [P] [US1] Create auth form components in `frontend/components/auth/` for reusable input fields and validation
- [x] T025 [US1] Integrate Better Auth registration flow in register page with API call to backend
- [x] T026 [US1] Integrate Better Auth login flow in login page with JWT token storage
- [x] T027 [US1] Add error handling and user feedback for registration/login failures with react-hot-toast

### Integration for US1

- [ ] T028 [US1] Test complete authentication flow: register → login → verify JWT token in API request
- [ ] T029 [US1] Verify token expiration handling and error responses for invalid tokens

**Checkpoint**: User Story 1 complete - users can register, login, and authenticate API requests

---

## Phase 4: User Story 2 - Create and List Personal Tasks (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can create new tasks and view their personal task list with proper ownership isolation

**Independent Test**: Login → Create task with title → View task list → Verify task appears → Verify other users cannot see this task

### Backend Implementation for US2

- [x] T030 [P] [US2] Create task schemas in `backend/app/schemas.py` with TaskCreate (title, description), TaskResponse (all fields)
- [x] T031 [US2] Create POST /api/tasks endpoint in `backend/app/routes/tasks.py` with get_current_user dependency, associate task with user_id
- [x] T032 [US2] Create GET /api/tasks endpoint in `backend/app/routes/tasks.py` filtered by current user's ID
- [x] T033 [US2] Add task validation in routes (title required, description optional, max lengths)
- [x] T034 [US2] Add authorization checks to ensure task isolation by user_id
- [x] T035 [US2] Add logging for task operations (created, listed) with user_id context

### Frontend Implementation for US2

- [x] T036 [P] [US2] Create protected tasks page in `frontend/app/tasks/page.tsx` with authentication check
- [x] T037 [P] [US2] Create TaskList component (using existing TaskCard) to display all user tasks
- [x] T038 [P] [US2] Create TaskItem component in `frontend/components/TaskCard.tsx` for individual task display
- [x] T039 [P] [US2] Create TaskForm component in `frontend/components/TaskForm.tsx` with title and description inputs
- [x] T040 [US2] Integrate task creation API call in TaskForm component with Authorization header
- [x] T041 [US2] Integrate task list API call in tasks page to fetch and display user tasks
- [x] T042 [US2] Add loading states and error handling for task operations
- [x] T043 [US2] Add empty state UI when user has no tasks

### Integration for US2

- [ ] T044 [US2] Test unauthenticated requests are rejected with 401 error
- [ ] T045 [US2] Test authenticated user can create task and see it in their list
- [ ] T046 [US2] Test task ownership isolation - user A cannot see user B's tasks

**Checkpoint**: User Story 2 complete - users can create and list their personal tasks

---

## Phase 5: User Story 3 - View Task Details (Priority: P2)

**Goal**: Authenticated users can view detailed information for a specific task they own

**Independent Test**: Login → Create task → Request task details by ID → Verify complete information returned → Test authorization for non-owned tasks

### Backend Implementation for US3

- [x] T047 [US3] Create GET /api/tasks/{task_id} endpoint in `backend/app/routes/tasks.py` with ownership verification
- [x] T048 [US3] Add 403 Forbidden response when user attempts to access task they don't own
- [x] T049 [US3] Add 404 Not Found response when task_id doesn't exist
- [x] T050 [US3] Add logging for task detail access attempts with authorization results

### Frontend Implementation for US3

- [ ] T051 [P] [US3] Create TaskDialog component in `frontend/components/tasks/task-dialog.tsx` to display task details in modal
- [ ] T052 [US3] Add click handler to TaskItem to open TaskDialog with task details
- [ ] T053 [US3] Integrate GET /api/tasks/{task_id} API call in TaskDialog component
- [ ] T054 [US3] Add error handling for 403/404 responses with user-friendly messages

### Integration for US3

- [ ] T055 [US3] Test task details displayed correctly for owned tasks
- [ ] T056 [US3] Test 403 error when attempting to view non-owned task
- [ ] T057 [US3] Test 404 error when requesting non-existent task ID

**Checkpoint**: User Story 3 complete - users can view detailed task information

---

## Phase 6: User Story 4 - Update Task Information (Priority: P2)

**Goal**: Authenticated users can modify title and description of their own tasks

**Independent Test**: Login → Create task → Update task properties → Verify changes persist → Test authorization for non-owned tasks

### Backend Implementation for US4

- [x] T058 [P] [US4] Create TaskUpdate schema in `backend/app/schemas.py` with optional title and description fields
- [x] T059 [US4] Create PATCH /api/tasks/{task_id} endpoint in `backend/app/routes/tasks.py` with ownership verification
- [x] T060 [US4] Add validation for update payload (at least one field must be provided)
- [x] T061 [US4] Update updated_at timestamp when task is modified
- [x] T062 [US4] Add logging for task update operations with before/after values

### Frontend Implementation for US4

- [x] T063 [P] [US4] Add edit mode to TaskCard component with editable title and description inputs
- [x] T064 [P] [US4] Add edit button to TaskCard component to trigger edit mode
- [x] T065 [US4] Integrate PATCH /api/tasks/{task_id} API call in TaskForm save handler
- [ ] T066 [US4] Add optimistic UI updates with rollback on API failure
- [x] T067 [US4] Refresh task list after successful update to reflect changes

### Integration for US4

- [ ] T068 [US4] Test task update persists changes to title and description
- [ ] T069 [US4] Test 403 error when attempting to update non-owned task
- [ ] T070 [US4] Test validation errors for invalid update payloads

**Checkpoint**: User Story 4 complete - users can update their task information

---

## Phase 7: User Story 5 - Toggle Task Completion Status (Priority: P2)

**Goal**: Authenticated users can mark tasks as complete or incomplete with single action

**Independent Test**: Login → Create task → Toggle completion → Verify status changes → Toggle again → Verify status reverts

### Backend Implementation for US5

- [x] T071 [US5] Create POST /api/tasks/{task_id}/toggle endpoint in `backend/app/routes/tasks.py` with ownership verification
- [x] T072 [US5] Implement toggle logic to flip is_completed boolean value
- [x] T073 [US5] Update updated_at timestamp when completion status changes
- [x] T074 [US5] Add logging for completion toggle operations with new status

### Frontend Implementation for US5

- [x] T075 [P] [US5] Add checkbox to TaskCard component for completion status display
- [x] T076 [US5] Add click handler to checkbox to call toggle API endpoint
- [x] T077 [US5] Add visual differentiation for completed tasks (strikethrough, different styling)
- [ ] T078 [US5] Add optimistic UI update for immediate feedback before API response
- [x] T079 [US5] Add error handling with rollback if toggle API call fails

### Integration for US5

- [ ] T080 [US5] Test toggle completion from incomplete to complete
- [ ] T081 [US5] Test toggle completion from complete to incomplete
- [ ] T082 [US5] Test 403 error when attempting to toggle non-owned task
- [ ] T083 [US5] Test completion status reflected in task list after toggle

**Checkpoint**: User Story 5 complete - users can toggle task completion status

---

## Phase 8: User Story 6 - Delete Personal Tasks (Priority: P3)

**Goal**: Authenticated users can permanently remove tasks they no longer need

**Independent Test**: Login → Create task → Delete task → Verify task removed from list → Verify task cannot be accessed by ID

### Backend Implementation for US6

- [x] T084 [US6] Create DELETE /api/tasks/{task_id} endpoint in `backend/app/routes/tasks.py` with ownership verification
- [x] T085 [US6] Implement hard delete to permanently remove task from database
- [x] T086 [US6] Add 404 response for subsequent requests to deleted task ID
- [x] T087 [US6] Add logging for task deletion operations with user_id and task_id

### Frontend Implementation for US6

- [x] T088 [P] [US6] Add delete button to TaskCard component
- [x] T089 [US6] Add confirmation dialog before delete to prevent accidental deletion
- [x] T090 [US6] Integrate DELETE /api/tasks/{task_id} API call on delete confirmation
- [x] T091 [US6] Remove task from UI immediately after successful deletion
- [x] T092 [US6] Add error handling if deletion fails with rollback

### Integration for US6

- [ ] T093 [US6] Test task deletion removes task from database
- [ ] T094 [US6] Test 404 error when accessing deleted task by ID
- [ ] T095 [US6] Test 403 error when attempting to delete non-owned task
- [ ] T096 [US6] Test task removed from task list after deletion

**Checkpoint**: User Story 6 complete - users can delete their personal tasks

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Production readiness, error handling, and user experience improvements

### Security & Error Handling

- [ ] T097 [P] Add rate limiting to authentication endpoints to prevent brute force attacks
- [x] T098 [P] Implement CORS configuration in `backend/app/main.py` for frontend origin
- [x] T099 [P] Add comprehensive error messages without exposing security details
- [x] T100 [P] Implement token expiration handling on frontend with automatic re-login prompt
- [ ] T101 Add global error boundary in `frontend/app/layout.tsx` for unhandled exceptions

### User Experience

- [x] T102 [P] Add loading skeletons for task list while data is fetching
- [x] T103 [P] Add success toast notifications for all task operations
- [ ] T104 [P] Add responsive design tweaks for mobile devices
- [ ] T105 [P] Add keyboard shortcuts for common actions (Ctrl+N for new task, etc.)
- [ ] T106 Add landing page content in `frontend/app/page.tsx` with feature overview and login/register CTAs

### Documentation & Deployment

- [ ] T107 [P] Create quickstart guide in `specs/003-better-auth-integration/quickstart.md` with setup instructions
- [ ] T108 [P] Document environment variables and JWT secret generation in README
- [ ] T109 [P] Add API documentation with endpoint descriptions and example requests
- [ ] T110 Verify HTTPS enforcement configuration for production deployment

**Checkpoint**: All features complete and production-ready

---

## Dependencies & Execution Strategy

### User Story Dependencies

```
Setup (T001-T005)
    ↓
Foundation (T006-T016) ← BLOCKING - Must complete before any user stories
    ↓
    ├─→ US1: Auth (T017-T029) ← BLOCKING for all other user stories
    │       ↓
    │       ├─→ US2: Create/List (T030-T046) 🎯 MVP Core
    │       ├─→ US3: View Details (T047-T057)
    │       ├─→ US4: Update (T058-T070)
    │       ├─→ US5: Toggle (T071-T083)
    │       └─→ US6: Delete (T084-T096)
    │
    └─→ Polish (T097-T110) - Can happen anytime after US2 complete
```

### MVP Delivery Strategy

**Minimum Viable Product (MVP)**: User Story 1 + User Story 2
- **T001-T046** delivers core value: users can register, login, create tasks, and view their personal task list
- **User stories 3-6** are enhancements that can be delivered incrementally after MVP

### Parallel Execution Opportunities

**Phase 1 (Setup)**: All tasks parallelizable
- T001 + T002 + T003 + T004

**Phase 2 (Foundation)**: Two parallel tracks
- Backend track: T006 → T007 → T012, then T008 + T009 + T010 + T011 in parallel
- Frontend track: T013 + T014 + T015 in parallel, then T016

**Phase 3 (US1)**: Three parallel tracks
- Backend schemas: T017 + T018
- Backend routes: T019 → T020 → T021
- Frontend UI: T022 + T023 + T024, then T025 + T026 → T027
- Integration: T028 → T029

**Phase 4 (US2)**: Three parallel tracks
- Backend: T030, then T031 + T032 in parallel, then T033 → T034 → T035
- Frontend: T036 + T037 + T038 + T039 in parallel, then T040 + T041 → T042 → T043
- Integration: T044 → T045 → T046

**Phases 5-8**: Each user story can be implemented by different developers in parallel after US1 complete
- US3 team: T047-T057
- US4 team: T058-T070
- US5 team: T071-T083
- US6 team: T084-T096

**Phase 9 (Polish)**: Most tasks parallelizable
- Security: T097 + T098 + T099 in parallel
- UX: T102 + T103 + T104 + T105 in parallel
- Docs: T107 + T108 + T109 in parallel

### Independent Testing per User Story

**US1 Acceptance**: User can register → login → receive JWT → make authenticated API request
**US2 Acceptance**: Authenticated user can create task → task appears in their list → other users cannot see it
**US3 Acceptance**: User can click task → view full details → cannot view other users' tasks
**US4 Acceptance**: User can edit task title/description → changes persist → cannot edit other users' tasks
**US5 Acceptance**: User can toggle task completion → status updates → cannot toggle other users' tasks
**US6 Acceptance**: User can delete task → task removed from list → cannot delete other users' tasks

---

## Task Summary

**Total Tasks**: 110 tasks
**MVP Tasks**: 46 tasks (T001-T046: Setup + Foundation + US1 + US2)

**Tasks by User Story**:
- Setup: 5 tasks (T001-T005)
- Foundation: 11 tasks (T006-T016) - BLOCKING
- US1 (Auth): 13 tasks (T017-T029) - BLOCKING for other stories
- US2 (Create/List): 17 tasks (T030-T046) - MVP Core
- US3 (View Details): 11 tasks (T047-T057)
- US4 (Update): 13 tasks (T058-T070)
- US5 (Toggle): 13 tasks (T071-T083)
- US6 (Delete): 13 tasks (T084-T096)
- Polish: 14 tasks (T097-T110)

**Parallel Opportunities**: ~60% of tasks can run in parallel within their phase

**Recommended Delivery Increments**:
1. **MVP (Sprint 1)**: T001-T046 - Core authentication and task management
2. **Enhancement 1 (Sprint 2)**: T047-T057 + T058-T070 - View details and updates
3. **Enhancement 2 (Sprint 3)**: T071-T083 + T084-T096 - Toggle and delete
4. **Production Ready (Sprint 4)**: T097-T110 - Polish and deployment

---

## Implementation Notes

### Critical Path
Setup → Foundation → US1 (Auth) → US2 (Create/List) = MVP

### Risk Mitigation
- **JWT Token Mismatch**: Test token payload format early (after T009, T013)
- **Authorization Bypass**: Test ownership checks thoroughly for each user story
- **Secret Management**: Verify JWT_SECRET matches between frontend and backend (T005)

### Testing Strategy
Each user story includes integration tasks to verify:
1. Happy path works end-to-end
2. Authorization prevents access to non-owned resources
3. Error cases return appropriate status codes and messages

### Code Quality Gates
- All auth logic includes logging for security audit trail
- All endpoints include authorization dependency (get_current_user)
- All frontend forms include validation and error handling
- All API calls include Authorization header from Better Auth session
