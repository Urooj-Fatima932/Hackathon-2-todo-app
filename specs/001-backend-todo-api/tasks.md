# Tasks: Backend Todo API

**Input**: Design documents from `/specs/001-backend-todo-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are EXCLUDED per template guidelines.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

Per plan.md, this is a **web backend API** in a monorepo:
- Backend code: `backend/app/` for source
- Tests: `backend/tests/` for test files
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend directory structure per plan.md: `backend/app/`, `backend/app/auth/`, `backend/app/routes/`, `backend/app/utils/`, `backend/tests/`
- [X] T002 Create requirements.txt in backend/ with dependencies: FastAPI==0.115.0, uvicorn[standard]==0.31.0, sqlmodel==0.0.22, psycopg2-binary==2.9.9, pydantic==2.9.0, pydantic-settings==2.5.0, PyJWT==2.9.0, python-multipart==0.0.12
- [X] T003 [P] Create .env.example in backend/ with template environment variables: DATABASE_URL, BETTER_AUTH_SECRET, API_HOST, API_PORT, DEBUG, CORS_ORIGINS
- [X] T004 [P] Create backend/README.md with quickstart instructions per quickstart.md
- [X] T005 [P] Create Dockerfile in backend/ for containerization
- [X] T006 [P] Create __init__.py files in backend/app/, backend/app/auth/, backend/app/routes/, backend/app/utils/, backend/tests/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Implement configuration management in backend/app/config.py using pydantic-settings to load environment variables
- [X] T008 [P] Implement database connection in backend/app/database.py with SQLModel engine, connection pooling (pool_size=5, max_overflow=10), and get_session dependency
- [X] T009 [P] Create SQLModel User model in backend/app/models.py matching Better Auth schema (id, email, name, created_at)
- [X] T010 Create SQLModel Task model in backend/app/models.py with fields per data-model.md (id, user_id FK, title, description, completed, created_at, updated_at) and relationships to User
- [ ] T011 [P] Implement JWT verification in backend/app/auth/middleware.py using PyJWT with HS256 algorithm and BETTER_AUTH_SECRET (SKIPPED - auth not implemented)
- [ ] T012 Implement authentication dependency in backend/app/auth/dependencies.py with get_current_user() and verify_user_access() functions per plan.md security requirements (SKIPPED - auth not implemented)
- [X] T013 [P] Create Pydantic schemas in backend/app/schemas.py: TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, JWTPayload per data-model.md
- [X] T014 [P] Create custom exception handlers in backend/app/utils/exceptions.py for consistent error response format
- [X] T015 Create FastAPI application in backend/app/main.py with CORS middleware, lifespan events for database table creation, root endpoint, health check endpoint, and global exception handler

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Creation and Viewing (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks and view their task list

**Independent Test**: Authenticate a user, create multiple tasks via POST /api/{user_id}/tasks, then retrieve the task list via GET /api/{user_id}/tasks. Verify tasks appear with IDs and timestamps, ordered newest first, and user isolation works.

### Implementation for User Story 1

- [X] T016 [US1] Create tasks router in backend/app/routes/tasks.py with APIRouter configured with prefix="/api" and tags=["tasks"]
- [X] T017 [P] [US1] Implement POST /api/{user_id}/tasks endpoint in backend/app/routes/tasks.py to create tasks with Pydantic validation, and return 201 Created with TaskResponse (JWT auth skipped)
- [X] T018 [P] [US1] Implement GET /api/{user_id}/tasks endpoint in backend/app/routes/tasks.py to list user's tasks with optional status filtering (all/pending/completed), ordered by created_at DESC, and return TaskListResponse (JWT auth skipped)
- [X] T019 [US1] Include tasks router in main FastAPI application in backend/app/main.py using app.include_router(tasks.router)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create and view their tasks

---

## Phase 4: User Story 2 - Task Status Management (Priority: P2)

**Goal**: Users can toggle task completion status and filter by status

**Independent Test**: Create a task, toggle its completion status multiple times via PATCH /api/{user_id}/tasks/{task_id}/complete, verify status changes persist. Filter tasks by completion status and verify correct tasks returned.

### Implementation for User Story 2

- [X] T020 [US2] Implement PATCH /api/{user_id}/tasks/{task_id}/complete endpoint in backend/app/routes/tasks.py to toggle task completion with 404 for non-existent/other user's tasks, update updated_at timestamp, and return TaskResponse (JWT auth skipped)

**Note**: Status filtering already implemented in T018 (GET /api/{user_id}/tasks with status query parameter)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can create, view, and mark tasks complete

---

## Phase 5: User Story 3 - Task Modification (Priority: P3)

**Goal**: Users can update task title and/or description

**Independent Test**: Create a task, update its title via PUT /api/{user_id}/tasks/{task_id}, verify title changed and updated_at timestamp reflects change. Update only description, verify title unchanged. Attempt to update another user's task, verify 403 Forbidden.

### Implementation for User Story 3

- [X] T021 [US3] Implement PUT /api/{user_id}/tasks/{task_id} endpoint in backend/app/routes/tasks.py to update tasks with Pydantic TaskUpdate validation, conditional field updates (title and/or description), update updated_at timestamp, 404 for non-existent/other user's tasks, and return TaskResponse (JWT auth skipped)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - full task management with create, view, complete, and edit

---

## Phase 6: User Story 4 - Task Deletion (Priority: P4)

**Goal**: Users can permanently delete tasks

**Independent Test**: Create a task, delete it via DELETE /api/{user_id}/tasks/{task_id}, verify it no longer appears in task list. Attempt to delete non-existent task, verify 404. Attempt to delete another user's task, verify 403 Forbidden.

### Implementation for User Story 4

- [X] T022 [US4] Implement DELETE /api/{user_id}/tasks/{task_id} endpoint in backend/app/routes/tasks.py to delete tasks with permanent deletion from database, 404 for non-existent/other user's tasks, and return 204 No Content (JWT auth skipped)

**Checkpoint**: At this point, User Stories 1-4 should all work - complete CRUD operations available

---

## Phase 7: User Story 5 - Individual Task Retrieval (Priority: P5)

**Goal**: Users can retrieve detailed information about a specific task by ID

**Independent Test**: Create a task, retrieve it by ID via GET /api/{user_id}/tasks/{task_id}, verify all details returned (title, description, completion status, timestamps). Attempt to access non-existent task, verify 404. Attempt to access another user's task, verify 404 (not 403 for security).

### Implementation for User Story 5

- [X] T023 [US5] Implement GET /api/{user_id}/tasks/{task_id} endpoint in backend/app/routes/tasks.py to retrieve individual task with 404 for non-existent/other user's tasks (not 403 to prevent enumeration), and return TaskResponse (JWT auth skipped)

**Checkpoint**: All user stories (1-5) are now complete - full API functionality available

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T024 [P] Add comprehensive docstrings to all functions in backend/app/routes/tasks.py following FastAPI documentation standards
- [ ] T025 [P] Verify all endpoints return correct HTTP status codes per spec.md requirements (200, 201, 204, 400, 401, 403, 404, 500)
- [ ] T026 [P] Verify all error responses use consistent {"detail": "message"} format per plan.md
- [ ] T027 [P] Add input validation edge case handling: empty title after trim, title > 200 chars, description > 1000 chars, malformed JSON
- [ ] T028 [P] Verify CORS configuration in backend/app/main.py uses explicit origins from environment variable (no wildcards)
- [ ] T029 [P] Verify database indexes created on tasks.user_id and tasks.completed per data-model.md
- [ ] T030 [P] Test API manually using quickstart.md steps to verify setup instructions are correct
- [ ] T031 [P] Verify FastAPI automatic documentation at /docs displays all endpoints correctly
- [ ] T032 Code review for security: no hardcoded secrets, all queries filter by user_id, JWT validation on all protected endpoints
- [ ] T033 Performance verification: test with 100 concurrent users, verify <500ms task creation, <1s task list retrieval

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational (Phase 2) completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Adds to US1's GET endpoint but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent from US1 and US2
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Independent from previous stories
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Independent from previous stories

### Within Each Phase

**Phase 1 (Setup)**: T001 must complete first, then T002-T006 can run in parallel

**Phase 2 (Foundational)**:
- T007 (config) must complete first
- T008 (database) can run in parallel with T007
- T009 (User model) can run in parallel with T007-T008
- T010 (Task model) depends on T009 (User model)
- T011 (JWT middleware) can run in parallel with T007-T010
- T012 (auth dependencies) depends on T011
- T013 (schemas) can run in parallel with T007-T012
- T014 (exceptions) can run in parallel with T007-T013
- T015 (main app) depends on T007-T014 all being complete

**Phase 3 (US1)**: T016 first, then T017-T018 in parallel, then T019

**Phase 4 (US2)**: T020 is single task

**Phase 5 (US3)**: T021 is single task

**Phase 6 (US4)**: T022 is single task

**Phase 7 (US5)**: T023 is single task

**Phase 8 (Polish)**: T024-T031 can run in parallel, T032-T033 must run last

### Parallel Opportunities

- **Setup**: T003-T006 can all run in parallel after T001-T002
- **Foundational**: T007-T009, T011, T013-T014 can run in parallel; T010 needs T009; T012 needs T011; T015 needs all
- **User Story 1**: T017-T018 can run in parallel after T016
- **User Stories 2-5**: Can all be worked on in parallel by different team members after Foundational completes
- **Polish**: T024-T031 can all run in parallel

---

## Parallel Example: Phase 2 (Foundational)

```bash
# First wave (parallel):
Task T007: "Implement configuration management in backend/app/config.py"
Task T008: "Implement database connection in backend/app/database.py"
Task T009: "Create SQLModel User model in backend/app/models.py"
Task T011: "Implement JWT verification in backend/app/auth/middleware.py"
Task T013: "Create Pydantic schemas in backend/app/schemas.py"
Task T014: "Create custom exception handlers in backend/app/utils/exceptions.py"

# Second wave (depends on T009 and T011):
Task T010: "Create SQLModel Task model in backend/app/models.py" (needs T009)
Task T012: "Implement authentication dependency in backend/app/auth/dependencies.py" (needs T011)

# Final task (depends on all above):
Task T015: "Create FastAPI application in backend/app/main.py"
```

---

## Parallel Example: User Story 1

```bash
# After T016 creates the router:
Task T017: "Implement POST /api/{user_id}/tasks endpoint in backend/app/routes/tasks.py"
Task T018: "Implement GET /api/{user_id}/tasks endpoint in backend/app/routes/tasks.py"

# Both can be implemented in parallel, then:
Task T019: "Include tasks router in main FastAPI application"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T015) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T016-T019)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Create tasks via POST /api/{user_id}/tasks
   - Retrieve tasks via GET /api/{user_id}/tasks
   - Verify user isolation works
   - Verify authentication required
5. Deploy/demo if ready - **This is the MVP!**

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (can now complete tasks)
4. Add User Story 3 → Test independently → Deploy/Demo (can now edit tasks)
5. Add User Story 4 → Test independently → Deploy/Demo (can now delete tasks)
6. Add User Story 5 → Test independently → Deploy/Demo (full CRUD complete)
7. Add Polish → Final production-ready API
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T015)
2. Once Foundational is done (checkpoint after T015):
   - Developer A: User Story 1 (T016-T019)
   - Developer B: User Story 2 (T020) - can start immediately
   - Developer C: User Story 3 (T021) - can start immediately
   - Developer D: User Story 4 (T022) - can start immediately
   - Developer E: User Story 5 (T023) - can start immediately
3. Stories complete and integrate independently
4. Team collaborates on Polish phase (T024-T033)

### Recommended Order for Solo Developer

Priority order matching spec.md:
1. Phase 1: Setup → Phase 2: Foundational
2. Phase 3: User Story 1 (P1) - MVP ← **Deploy after this**
3. Phase 4: User Story 2 (P2) - Task completion
4. Phase 5: User Story 3 (P3) - Task editing
5. Phase 6: User Story 4 (P4) - Task deletion
6. Phase 7: User Story 5 (P5) - Individual retrieval
7. Phase 8: Polish - Production hardening

---

## Task Count Summary

- **Phase 1 (Setup)**: 6 tasks (T001-T006)
- **Phase 2 (Foundational)**: 9 tasks (T007-T015) - **CRITICAL PATH**
- **Phase 3 (User Story 1 - P1)**: 4 tasks (T016-T019) - **MVP**
- **Phase 4 (User Story 2 - P2)**: 1 task (T020)
- **Phase 5 (User Story 3 - P3)**: 1 task (T021)
- **Phase 6 (User Story 4 - P4)**: 1 task (T022)
- **Phase 7 (User Story 5 - P5)**: 1 task (T023)
- **Phase 8 (Polish)**: 10 tasks (T024-T033)

**Total**: 33 tasks

**MVP Scope** (Phases 1-3): 19 tasks
**Full Feature Scope** (Phases 1-7): 23 tasks
**Production Ready** (All phases): 33 tasks

**Parallel Opportunities**:
- Setup: 4 tasks can run in parallel (T003-T006)
- Foundational: Up to 6 tasks in first wave (T007-T009, T011, T013-T014)
- User Story 1: 2 tasks can run in parallel (T017-T018)
- User Stories 2-5: All 4 stories can be developed in parallel after Foundational
- Polish: 10 tasks can run in parallel (T024-T031)

**Estimated Parallel Execution** (with 5 developers):
- Phase 1: ~2 rounds
- Phase 2: ~3 rounds
- Phase 3-7: ~2 rounds (all stories in parallel)
- Phase 8: ~2 rounds
- **Total**: ~9 rounds vs 33 sequential

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story (US1-US5) for traceability
- Each user story is independently completable and testable per spec.md
- No test tasks included because tests not explicitly requested in specification
- Commit after each task or logical group per development workflow
- Stop at any checkpoint to validate story independently
- All file paths follow plan.md backend monorepo structure
- Constitution check passed - all tasks align with security, API, and database standards
