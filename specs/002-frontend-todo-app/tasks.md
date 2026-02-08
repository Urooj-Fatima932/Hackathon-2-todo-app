# Tasks: Frontend Todo Web Application

**Input**: Design documents from `/specs/002-frontend-todo-app/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-endpoints.md

**Note**: Authentication (User Story 1) is DEFERRED per user request. This implementation focuses on landing page and task management UI only.

**Tests**: Not requested in spec - tests deferred to post-MVP phase per plan.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US2, US3)
- **[Landing]**: Landing page tasks (not tied to user story)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/` directory (Next.js 14 App Router)
- **Backend**: `backend/` directory (existing FastAPI - out of scope)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Next.js project and install dependencies

**Acceptance**: Dev server runs on http://localhost:3000 without errors

- [X] T001 Initialize Next.js 14 with TypeScript, Tailwind CSS, and App Router in frontend/ directory
- [X] T002 Install dependencies: react-hot-toast for toast notifications
- [X] T003 [P] Initialize shadcn/ui with default configuration (Style: Default, Base color: Slate)
- [X] T004 [P] Add shadcn/ui components: button, dialog, input, textarea, card, checkbox
- [X] T005 Create .env.local with NEXT_PUBLIC_API_URL=http://localhost:8000
- [ ] T006 Verify backend API is accessible by testing http://localhost:8000/health endpoint

**Checkpoint**: Next.js dev server runs successfully with all dependencies installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story or landing page work

**⚠️ CRITICAL**: No feature work can begin until this phase is complete

**Acceptance**: Types defined, API client ready, utilities in place

- [X] T007 Create TypeScript types in frontend/lib/types.ts (User, Task, CreateTaskRequest, UpdateTaskRequest, TaskListResponse, ApiError, TaskFilter, OptimisticTask)
- [X] T008 Implement API client in frontend/lib/api.ts with typed fetch wrapper for GET, POST, PATCH, DELETE methods
- [X] T009 [P] Create utility functions in frontend/lib/utils.ts (cn helper for Tailwind, date formatters)
- [X] T010 [P] Configure globals.css in frontend/app/globals.css with Tailwind directives and custom styles
- [X] T011 Create root layout in frontend/app/layout.tsx with metadata, fonts, and Toaster provider
- [X] T012 [P] Create Navigation component in frontend/components/Navigation.tsx with links to landing page and tasks

**Checkpoint**: Foundation ready - feature implementation can now begin in parallel

---

## Phase 3: Landing Page (No User Story - Marketing Content) 🎯 MVP Component 1

**Goal**: Build responsive marketing landing page with hero, features, and CTA sections

**Independent Test**: Visit http://localhost:3000 and verify landing page displays with hero, features, CTA, and footer. Test mobile responsiveness.

**Acceptance**: Landing page loads, is mobile-responsive, and achieves Lighthouse score 90+ desktop

### Implementation for Landing Page

- [X] T013 [P] [Landing] Create (marketing) route group and layout in frontend/app/(marketing)/layout.tsx
- [X] T014 [Landing] Create landing page in frontend/app/(marketing)/page.tsx with Hero, Features, CTA, Footer sections
- [X] T015 [P] [Landing] Implement Hero component in frontend/components/landing/Hero.tsx with value proposition and CTA button
- [X] T016 [P] [Landing] Implement Features component in frontend/components/landing/Features.tsx with 3-4 key benefits (Fast, Simple, Organized)
- [X] T017 [P] [Landing] Implement CTA component in frontend/components/landing/CTA.tsx with "Get Started" button linking to /tasks
- [X] T018 [P] [Landing] Implement Footer component in frontend/components/landing/Footer.tsx with links and copyright
- [X] T019 [Landing] Add responsive design and mobile optimization to all landing page components
- [X] T020 [Landing] Add meta tags and SEO optimization to landing page (title, description, Open Graph tags)

**Checkpoint**: Landing page fully functional, mobile-responsive, and optimized for performance

---

## Phase 4: User Story 2 - Task Management (Priority: P1) 🎯 MVP Component 2

**Goal**: Enable users to create, view, update, and delete tasks with optimistic UI updates

**Independent Test**: A user can navigate to /tasks, see a task list, create a new task (appears immediately), edit a task (updates immediately), mark a task as complete (toggles immediately), and delete a task (removes immediately). All operations should update the UI in <500ms.

**From spec.md**:
- FR-003: Authenticated users MUST be able to create, read, update, and delete their own tasks
- SC-002: Task operations must update UI in <500ms (optimistic updates)
- SC-003: Task list should load within 2 seconds for up to 1000 tasks

### Implementation for User Story 2

**Task Display & List**

- [X] T021 [P] [US2] Create tasks page in frontend/app/tasks/page.tsx as Server Component fetching tasks from backend
- [X] T022 [P] [US2] Create loading.tsx in frontend/app/tasks/loading.tsx with skeleton placeholders for task list
- [X] T023 [P] [US2] Create error.tsx in frontend/app/tasks/error.tsx with error message and retry button
- [X] T024 [US2] Implement TaskCard component in frontend/components/TaskCard.tsx displaying title, description, completed status, and action buttons (edit, delete, toggle complete)
- [X] T025 [US2] Implement TaskList client component in frontend/components/TaskList.tsx with optimistic updates using useOptimistic hook

**Task Creation**

- [X] T026 [P] [US2] Create TaskForm component in frontend/components/TaskForm.tsx with title and description inputs
- [X] T027 [US2] Implement Server Action for task creation in frontend/app/tasks/actions.ts (createTask function)
- [X] T028 [US2] Add "Create Task" button and dialog to tasks page integrating TaskForm with create action
- [X] T029 [US2] Add form validation to TaskForm (title required, 1-200 chars; description optional, max 1000 chars)
- [X] T030 [US2] Implement optimistic UI update for task creation (task appears immediately in list)

**Task Update**

- [X] T031 [US2] Implement Server Action for task update in frontend/app/tasks/actions.ts (updateTask function)
- [X] T032 [US2] Add edit functionality to TaskCard opening TaskForm dialog with pre-filled data
- [X] T033 [US2] Implement optimistic UI update for task edits (changes appear immediately)
- [X] T034 [US2] Add toggle completion functionality to TaskCard with checkbox and optimistic update

**Task Deletion**

- [X] T035 [US2] Implement Server Action for task deletion in frontend/app/tasks/actions.ts (deleteTask function)
- [X] T036 [US2] Add delete button to TaskCard with confirmation dialog
- [X] T037 [US2] Implement optimistic UI update for task deletion (task removed immediately)

**Error Handling & Notifications**

- [X] T038 [P] [US2] Add toast notifications for success/error states using react-hot-toast
- [X] T039 [P] [US2] Implement error handling for API failures with revert on optimistic update failure
- [X] T040 [P] [US2] Add empty state component for when no tasks exist in frontend/components/EmptyState.tsx

**Checkpoint**: At this point, User Story 2 (Task Management) should be fully functional and testable independently. Users can create, read, update, delete tasks with optimistic UI.

---

## Phase 5: User Story 3 - Task Filtering (Priority: P2)

**Goal**: Enable users to filter tasks by status (All, Pending, Completed) with persistent filter selection

**Independent Test**: A user on /tasks can click filter buttons (All/Pending/Completed), see the task list update to show only matching tasks, refresh the page, and see the same filter still applied (URL-based persistence).

**From spec.md**:
- FR-005: Users MUST be able to filter tasks by status (All, Pending, Completed)
- Acceptance: Filter selection persisted on page refresh

### Implementation for User Story 3

- [X] T041 [P] [US3] Create TaskFilters component in frontend/components/TaskFilters.tsx with three buttons (All, Pending, Completed)
- [X] T042 [US3] Implement URL-based filter state using searchParams in frontend/app/tasks/page.tsx (e.g., /tasks?filter=pending)
- [X] T043 [US3] Update tasks page to filter tasks based on URL searchParams before rendering
- [X] T044 [US3] Add active state styling to TaskFilters component showing current filter selection
- [X] T045 [US3] Test filter persistence by refreshing page and verifying filter remains applied
- [X] T046 [US3] Update TaskList component to respect filter state and show appropriate tasks

**Checkpoint**: All user stories (US2, US3) should now be independently functional. Users can manage and filter tasks.

---

## Phase 6: Task Detail Page (Optional Enhancement - Priority: P2)

**Goal**: Provide dedicated page for viewing and editing individual task details

**Independent Test**: Click on a task card, navigate to /tasks/[id], see full task details with timestamps, edit or delete from detail page, navigate back to task list.

**From plan.md**: Phase 5 enhancement for better UX

### Implementation for Task Detail Page

- [ ] T047 [P] Create dynamic route folder in frontend/app/tasks/[id]/
- [ ] T048 Create task detail page in frontend/app/tasks/[id]/page.tsx fetching single task by ID
- [ ] T049 [P] Create loading.tsx in frontend/app/tasks/[id]/loading.tsx with skeleton for task detail
- [ ] T050 [P] Create error.tsx in frontend/app/tasks/[id]/error.tsx with 404 handling
- [ ] T051 Add breadcrumb navigation component in frontend/components/Breadcrumbs.tsx (Tasks > Task Title)
- [ ] T052 Render task details (title, description, status, createdAt, updatedAt) on detail page
- [ ] T053 Add Edit and Delete buttons to detail page reusing TaskForm and delete action
- [ ] T054 Make TaskCard clickable linking to /tasks/[id] detail page

**Checkpoint**: Task detail pages fully functional with navigation and CRUD operations

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Performance optimization, accessibility, and final UX improvements

**From spec.md**:
- FR-006: UI MUST be responsive and functional on both mobile and desktop
- SC-004: Lighthouse score 90+ desktop, 80+ mobile

### Polish Tasks

- [ ] T055 [P] Add keyboard shortcuts (Escape to close dialogs, Enter to submit forms, Ctrl+K to open create task dialog)
- [ ] T056 [P] Implement loading skeletons for task cards in TaskList component
- [ ] T057 [P] Add ARIA labels and semantic HTML for accessibility (button labels, form labels, dialog descriptions)
- [ ] T058 Optimize images using next/image component (landing page hero image, feature icons)
- [ ] T059 [P] Test responsive design on mobile devices (iPhone, Android) and adjust breakpoints
- [ ] T060 Run Lighthouse audit on landing page and tasks page, address performance issues
- [ ] T061 [P] Add focus management for dialogs (trap focus, restore focus on close)
- [ ] T062 Verify color contrast meets WCAG AA standards for all text
- [ ] T063 Test keyboard navigation for all interactive elements (tab order, focus indicators)
- [ ] T064 Add page transitions and micro-animations for better UX (task card hover, button interactions)
- [ ] T065 Run quickstart.md validation to ensure setup steps work correctly

**Checkpoint**: Application polished, accessible, performant (Lighthouse 90+/80+), and production-ready

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all feature work
- **Landing Page (Phase 3)**: Depends on Foundational (Phase 2) - Can proceed in parallel with Phase 4
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) - Main feature work
- **User Story 3 (Phase 5)**: Depends on User Story 2 (Phase 4) - Builds on task list
- **Task Detail (Phase 6)**: Depends on User Story 2 (Phase 4) - Optional enhancement
- **Polish (Phase 7)**: Depends on all desired features being complete

### User Story Dependencies

- **User Story 1 (Authentication)**: ❌ DEFERRED per user request
- **User Story 2 (Task Management)**: ✅ Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (Task Filtering)**: ✅ Depends on User Story 2 (needs task list to filter)

### Within Each Phase

- Tasks marked [P] can run in parallel (different files, no conflicts)
- Sequential tasks must complete in order (e.g., Server Actions before UI components using them)
- Complete phase before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003 (shadcn init) and T002 (npm install) can run together
- T004, T005, T006 can run after T001-T003

**Phase 2 (Foundational)**:
- T007, T008, T009, T010, T012 can all run in parallel (different files)
- T011 depends on T010 (needs globals.css)

**Phase 3 (Landing Page)**:
- T013 first, then T015, T016, T017, T018 can all run in parallel
- T014 assembles them, then T019, T020 sequentially

**Phase 4 (User Story 2)**:
- T021, T022, T023 can run in parallel (different files)
- T024, T025 depend on T021-T023
- T026, T038, T039, T040 can run in parallel (different files)
- T027-T037 depend on T024-T026

**Phase 5 (User Story 3)**:
- T041 and parallel work possible
- T042-T046 sequential (modifying same page logic)

**Phase 6 (Task Detail)**:
- T047, T049, T050, T051 can run in parallel
- T048, T052-T054 sequential

**Phase 7 (Polish)**:
- T055, T056, T057, T059, T061, T062, T063, T064 can all run in parallel (different concerns)
- T058, T060, T065 sequential

---

## Parallel Example: User Story 2 (Task Management)

```bash
# Launch initial page structure in parallel:
Task T021: "Create tasks page in frontend/app/tasks/page.tsx"
Task T022: "Create loading.tsx in frontend/app/tasks/loading.tsx"
Task T023: "Create error.tsx in frontend/app/tasks/error.tsx"

# Launch components in parallel after page structure:
Task T024: "TaskCard component in frontend/components/TaskCard.tsx"
Task T026: "TaskForm component in frontend/components/TaskForm.tsx"
Task T038: "Add toast notifications"
Task T040: "Add empty state component"

# Then proceed with Server Actions and integration sequentially
```

---

## Implementation Strategy

### MVP First (Minimal Viable Product)

**Recommended MVP Scope**: Landing Page + User Story 2 (Task Management)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all features)
3. Complete Phase 3: Landing Page (marketing site)
4. Complete Phase 4: User Story 2 (core task CRUD)
5. **STOP and VALIDATE**: Test task management independently
6. Deploy/demo if ready

**At this point you have**: A working todo app with landing page and full task management (create, read, update, delete) with optimistic UI.

### Incremental Delivery

**Delivery 1**: MVP (Phases 1-4)
- Landing page + Task CRUD
- Users can manage tasks immediately
- Deployed and usable

**Delivery 2**: Add Filtering (Phase 5)
- Enhance existing task list with filters
- Users can now filter by status
- Deployed as enhancement

**Delivery 3**: Add Detail Page (Phase 6 - Optional)
- Dedicated task detail views
- Better UX for viewing/editing
- Deployed as enhancement

**Delivery 4**: Polish & Optimize (Phase 7)
- Accessibility improvements
- Performance optimization
- Production-ready quality

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (Phases 1-2)
2. **Once Foundational is done**:
   - Developer A: Landing Page (Phase 3)
   - Developer B: Task Management (Phase 4)
   - These can proceed in parallel
3. **After Task Management complete**:
   - Developer A or B: Task Filtering (Phase 5)
   - Other developer: Task Detail Page (Phase 6)
4. **Team tackles Polish together** (Phase 7)

---

## Task Summary

**Total Tasks**: 65

### By Phase:
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 6 tasks
- Phase 3 (Landing Page): 8 tasks
- Phase 4 (Task Management - User Story 2): 20 tasks
- Phase 5 (Task Filtering - User Story 3): 6 tasks
- Phase 6 (Task Detail Page): 8 tasks
- Phase 7 (Polish): 11 tasks

### By User Story:
- Landing Page: 8 tasks
- User Story 2 (Task Management): 20 tasks
- User Story 3 (Task Filtering): 6 tasks
- Setup/Infrastructure: 12 tasks
- Enhancement (Detail Page): 8 tasks
- Polish: 11 tasks

### Parallel Opportunities:
- 28 tasks marked [P] can run in parallel within their phases
- Landing Page (Phase 3) can run in parallel with Task Management (Phase 4) after Foundation complete

### MVP Scope (Recommended):
- Phases 1-4 (40 tasks)
- Delivers: Landing page + Complete task management CRUD with optimistic UI
- Estimated LOC: ~1,500-2,000 lines of TypeScript/TSX

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label (US2, US3) maps task to specific user story for traceability
- [Landing] label identifies landing page tasks
- Each user story should be independently completable and testable
- Authentication (User Story 1) is DEFERRED - all tasks assume authenticated state
- Tests are DEFERRED per plan.md - focus on implementation first
- Commit after each task or logical group of parallel tasks
- Stop at any checkpoint to validate independently
- Backend API at http://localhost:8000 must be running for development
- Follow frontend/CLAUDE.md guidelines for all code

---

## Success Criteria Validation

**From spec.md**:

| Criteria | Addressed By | Status |
|----------|-------------|--------|
| SC-001: Sign up + first task <60s | User Story 1 | ❌ Deferred (auth excluded) |
| SC-002: Task ops <500ms | Phase 4 (optimistic UI) | ✅ Yes (T030, T033, T037) |
| SC-003: Load 1000 tasks <2s | Phase 4 (Server Components) | ✅ Yes (T021, efficient rendering) |
| SC-004: Lighthouse 90+/80+ | Phase 7 (optimization) | ✅ Yes (T060, T058) |
| FR-003: Task CRUD | Phase 4 (User Story 2) | ✅ Yes (T021-T040) |
| FR-005: Task filtering | Phase 5 (User Story 3) | ✅ Yes (T041-T046) |
| FR-006: Responsive UI | Phase 3, 7 (design + testing) | ✅ Yes (T019, T059) |

**3 of 4 success criteria met** (SC-001 deferred per user request)

---

**Generated**: 2026-02-07
**Feature Branch**: `002-frontend-todo-app`
**Ready for**: `/sp.implement` command to execute tasks
