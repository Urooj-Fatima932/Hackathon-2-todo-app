# Tasks: Agentic Task Management Chatbot

**Input**: Design documents from `/specs/001-agentic-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chat-api.yaml

**Tests**: Not explicitly requested in spec - tests are OPTIONAL.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Skills Referenced**:
- `agentic-chatbot-pro` - Stateless flow, MCP tools pattern
- `openai-agents-sdk-pro` - Function tools, agent configuration
- `chatkit-pro` - Chat UI components, floating widget pattern
- `fastapi-pro` - API endpoints, schemas, error handling

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/` (FastAPI, Python 3.11+)
- **Frontend**: `frontend/` (Next.js 14, App Router)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [x] T001 Install backend dependency `openai-agents` in backend/requirements.txt
- [x] T002 [P] Install frontend dependency `@chatscope/chat-ui-kit-react@^2.0.0` and `@chatscope/chat-ui-kit-styles@^1.4.0` in frontend/package.json
- [x] T003 [P] Add `OPENAI_API_KEY` to backend/.env.example with placeholder
- [x] T004 [P] Create backend/app/agent/ directory structure with __init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Database Models (Required for all user stories)

- [x] T005 Create Conversation model in backend/app/models.py with fields: id (UUID PK), user_id (FK), title (nullable), created_at, updated_at per data-model.md
- [x] T006 Create Message model in backend/app/models.py with fields: id (UUID PK), conversation_id (FK), role (enum), content (text), created_at per data-model.md
- [x] T007 Add relationship from User to Conversation (1:N) and Conversation to Message (1:N) with cascade delete in backend/app/models.py
- [x] T008 Update backend/app/main.py to create conversations and messages tables on startup via SQLModel.metadata.create_all

### Request/Response Schemas

- [x] T009 Create ChatRequest schema in backend/app/schemas.py with message (str, 1-1000 chars) and conversation_id (UUID, optional) per contracts/chat-api.yaml
- [x] T010 [P] Create ChatResponse schema in backend/app/schemas.py with response (str), conversation_id (UUID), tool_calls (list) per contracts/chat-api.yaml
- [x] T011 [P] Create ToolCall schema in backend/app/schemas.py with tool (str), args (dict), result (dict)
- [x] T012 [P] Create ConversationListResponse schema in backend/app/schemas.py with conversations (list), total (int)
- [x] T013 [P] Create ConversationDetailResponse schema in backend/app/schemas.py with id, title, created_at, updated_at, messages (list)
- [x] T014 [P] Create MessageResponse schema in backend/app/schemas.py with id, role, content, created_at

### MCP-Style Function Tools (Per openai-agents-sdk-pro skill)

- [x] T015 Create backend/app/agent/tools.py with @function_tool decorator imports from agents SDK
- [x] T016 Implement add_task tool in backend/app/agent/tools.py: takes title, description (optional), returns task_id, status, title (per mcp-tools.md)
- [x] T017 [P] Implement list_tasks tool in backend/app/agent/tools.py: takes status_filter (optional), returns array of tasks (per mcp-tools.md)
- [x] T018 [P] Implement get_task tool in backend/app/agent/tools.py: takes task_id, returns full task details (per mcp-tools.md)
- [x] T019 [P] Implement update_task tool in backend/app/agent/tools.py: takes task_id, title (optional), description (optional), returns updated task (per mcp-tools.md)
- [x] T020 [P] Implement complete_task tool in backend/app/agent/tools.py: takes task_id, returns task_id, status, title (per mcp-tools.md)
- [x] T021 [P] Implement delete_task tool in backend/app/agent/tools.py: takes task_id, returns task_id, status, title (per mcp-tools.md)
- [x] T022 Add user_id context injection pattern to all tools using RunContextWrapper (per openai-agents-sdk-pro skill: function-tools.md)

### Agent Configuration (Per openai-agents-sdk-pro skill)

- [x] T023 Create backend/app/agent/agent.py with Agent configuration: name="TaskBot", instructions (friendly, conversational), tools list
- [x] T024 Add agent instructions for natural language task management, pronoun resolution ("it", "that"), and clarifying questions per spec FR-016, FR-017
- [x] T025 Create agent runner utility function in backend/app/agent/agent.py that accepts user message and history, returns response per stateless-flow.md

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Chat-Based Task Creation (Priority: P1)

**Goal**: User sends natural language message to create tasks via AI assistant

**Independent Test**: Send "Add a task to buy groceries" via POST /api/chat, verify task created in database and assistant confirms

### Implementation for User Story 1

- [x] T026 [US1] Create backend/app/routes/chat.py with POST /api/chat endpoint skeleton with JWT auth dependency
- [x] T027 [US1] Implement conversation lookup/creation logic in POST /api/chat: if conversation_id provided, fetch and verify ownership; else create new conversation
- [x] T028 [US1] Implement 9-step stateless flow in POST /api/chat per agentic-chatbot-pro skill (stateless-flow.md):
  1. Receive message
  2. Fetch conversation history (last 20 messages per FR-027)
  3. Build message array
  4. Store user message
  5. Run agent with tools
  6. Collect tool calls
  7. Store assistant response
  8. Return response
  9. No server state
- [x] T029 [US1] Add message validation (1-1000 chars per FR-005) in POST /api/chat with 400 error response
- [x] T030 [US1] Add conversation not found/not owned 404 error handling in POST /api/chat (return 404, not 403 per FR-029)
- [x] T031 [US1] Add 30-second timeout for AI service with 504 response in POST /api/chat per contracts/chat-api.yaml
- [x] T032 [US1] Wire POST /api/chat router to backend/app/main.py
- [x] T033 [US1] Add chat API methods to frontend/lib/api.ts: sendMessage(message, conversationId?) returning ChatResponse

**Checkpoint**: User Story 1 complete - users can create tasks via natural language chat

---

## Phase 4: User Story 2 - View and Query Tasks (Priority: P1)

**Goal**: User asks AI to show their tasks, AI retrieves and displays them conversationally

**Independent Test**: Create tasks via API, ask "What tasks do I have?" via chat, verify response lists all tasks

### Implementation for User Story 2

- [x] T034 [US2] Verify list_tasks tool returns formatted task list with id, title, completion status
- [x] T035 [US2] Update agent instructions in backend/app/agent/agent.py to handle "show", "list", "what tasks" queries and respond conversationally
- [x] T036 [US2] Add status filter support to list_tasks tool: "all", "pending", "completed" per FR-011

**Checkpoint**: User Story 2 complete - users can view tasks via natural language queries

---

## Phase 5: User Story 3 - Complete and Update Tasks (Priority: P2)

**Goal**: User can mark tasks complete or update details via chat commands

**Independent Test**: Create task, say "Mark task X as done", verify is_completed=true in database

### Implementation for User Story 3

- [x] T037 [US3] Update agent instructions to handle "mark as done", "complete", "finished" commands
- [x] T038 [US3] Update agent instructions to handle "update", "change", "rename" commands with contextual pronoun resolution per FR-016
- [x] T039 [US3] Verify complete_task tool updates is_completed field and returns confirmation
- [x] T040 [US3] Verify update_task tool modifies title/description and returns confirmation

**Checkpoint**: User Story 3 complete - users can complete and update tasks via chat

---

## Phase 6: User Story 4 - Conversation Persistence (Priority: P2)

**Goal**: Users can continue conversations across sessions with full message history preserved

**Independent Test**: Start conversation, close browser, return, verify previous messages load correctly

### Implementation for User Story 4

- [x] T041 [US4] Create GET /api/conversations endpoint in backend/app/routes/chat.py: list user's conversations ordered by updated_at DESC per contracts/chat-api.yaml
- [x] T042 [US4] Create GET /api/conversations/{id} endpoint in backend/app/routes/chat.py: return conversation with last 20 messages ordered by created_at ASC per contracts/chat-api.yaml
- [x] T043 [US4] Add 404 handling for GET /api/conversations/{id} if not found or not owned by user
- [x] T044 [US4] Implement auto-generated conversation title from first user message (truncate to 100 chars) in POST /api/chat
- [x] T045 [US4] Add conversation list API method to frontend/lib/api.ts: getConversations() returning ConversationListResponse
- [x] T046 [US4] Add conversation detail API method to frontend/lib/api.ts: getConversation(id) returning ConversationDetailResponse

**Checkpoint**: User Story 4 complete - conversation persistence works across sessions

---

## Phase 7: User Story 5 - Delete Tasks and Conversations (Priority: P3)

**Goal**: User can delete tasks via chat and delete conversations via UI

**Independent Test**: Create task, say "delete that task", verify task removed; delete conversation, verify all messages cascade deleted

### Implementation for User Story 5

- [x] T047 [US5] Verify delete_task tool removes task and returns confirmation
- [x] T048 [US5] Update agent instructions to handle "delete", "remove", "cancel" commands with contextual resolution per FR-016
- [x] T049 [US5] Create DELETE /api/conversations/{id} endpoint in backend/app/routes/chat.py: return 204 on success, cascade delete messages per contracts/chat-api.yaml
- [x] T050 [US5] Add 404 handling for DELETE /api/conversations/{id} if not found or not owned
- [x] T051 [US5] Add conversation delete API method to frontend/lib/api.ts: deleteConversation(id) returning void

**Checkpoint**: User Story 5 complete - delete functionality works for tasks and conversations

---

## Phase 8: Chat UI (Floating Widget) - Frontend Implementation

**Goal**: Floating chat widget accessible from any page per FR-020

**Independent Test**: Open any page, click chat bubble, widget expands, send message, receive response

### Chat Provider and Context (Per chatkit-pro skill)

- [x] T052 Create frontend/components/chat/ChatContext.tsx with React Context: isOpen, toggleChat, conversationId, setConversationId, messages, loading states
- [x] T053 Create ChatProvider component in frontend/components/chat/ChatContext.tsx that wraps children and renders ChatWidget via portal

### Chat Widget Components (Per chatkit-pro skill)

- [x] T054 Create frontend/components/chat/ChatWidget.tsx: floating container in bottom-right corner, expand/collapse on click per FR-020
- [x] T055 [P] Create frontend/components/chat/ChatMessages.tsx: message list with user messages right-aligned, assistant messages left-aligned per FR-021
- [x] T056 [P] Create frontend/components/chat/ChatInput.tsx: text input with send button, Enter key support
- [x] T057 [P] Create frontend/components/chat/ConversationList.tsx: sidebar panel showing user's conversations per FR-020b
- [x] T058 [P] Create frontend/components/chat/ToolCallDisplay.tsx: component to show tool calls (what actions AI performed) per FR-023
- [x] T059 [P] Create frontend/components/chat/TypingIndicator.tsx: loading indicator while waiting for AI response per FR-022
- [x] T060 [P] Create frontend/components/chat/RetryButton.tsx: retry button shown when AI request fails per FR-022a
- [x] T061 Create frontend/components/chat/index.ts: export all chat components

### Widget Integration

- [x] T062 Add 'use client' directive and ChatProvider wrapper to frontend/app/layout.tsx per chatkit-pro skill
- [x] T063 Implement sendMessage function in ChatWidget: call API, update messages state, handle loading/error states
- [x] T064 Implement conversation switching: load messages when user selects different conversation per FR-024
- [x] T065 Add conversation delete with confirmation dialog per FR-025
- [x] T066 Style chat widget using @chatscope/chat-ui-kit-styles or Tailwind CSS for consistent look

### Chat Types

- [x] T067 Add chat types to frontend/lib/types.ts: Message, Conversation, ChatResponse, ToolCall per contracts/chat-api.yaml

**Checkpoint**: Frontend chat widget complete - users can interact with AI via floating widget

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Error Handling

- [x] T068 [P] Add friendly error messages for all error responses (no raw JSON per SC-007)
- [x] T069 [P] Implement graceful handling when task doesn't exist: return "I couldn't find that task" per edge case
- [x] T070 [P] Implement clarifying questions when user intent is ambiguous per FR-017

### Performance & UX

- [x] T071 Ensure task creation completes in <5 seconds per SC-001
- [x] T072 Ensure task listing completes in <3 seconds per SC-002
- [x] T073 Preserve user's message on AI failure for retry per edge case
- [x] T074 Update conversation updated_at timestamp when new messages added per FR-010

### Validation

- [ ] T075 Run quickstart.md validation: verify full flow works end-to-end
- [ ] T076 Verify user isolation: users can only access their own tasks and conversations per SC-006

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
- **Chat UI (Phase 8)**: Can start after Phase 1 (frontend setup) but needs Phase 3+ APIs for integration
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Core chat functionality
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Shares tools with US1
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Shares tools with US1/US2
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - New conversation endpoints
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Delete functionality

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003, T004)
- All schema tasks marked [P] can run in parallel (T010-T014)
- All tool tasks marked [P] can run in parallel (T017-T021)
- Frontend components marked [P] can run in parallel (T055-T060)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: Foundational Phase

```bash
# These can run in parallel (different files, no dependencies):
T010 ChatResponse schema
T011 ToolCall schema
T012 ConversationListResponse schema
T013 ConversationDetailResponse schema
T014 MessageResponse schema

# These can run in parallel (different tools):
T017 list_tasks tool
T018 get_task tool
T019 update_task tool
T020 complete_task tool
T021 delete_task tool
```

---

## Parallel Example: Frontend Chat Components

```bash
# These can run in parallel (independent components):
T055 ChatMessages.tsx
T056 ChatInput.tsx
T057 ConversationList.tsx
T058 ToolCallDisplay.tsx
T059 TypingIndicator.tsx
T060 RetryButton.tsx
```

---

## Implementation Strategy

### MVP Scope (Recommended)

**Phase 1 + Phase 2 + Phase 3 (User Story 1) + Phase 8 (partial)**

This delivers:
- Working chat endpoint with AI integration
- Task creation via natural language
- Basic floating chat widget
- ~30 tasks to complete

### Incremental Delivery

1. **MVP**: US1 (Task Creation) + Basic UI = Core value proposition
2. **+US2**: View/Query Tasks = Full read capability
3. **+US3**: Complete/Update = Full CRUD via chat
4. **+US4**: Conversation Persistence = Multi-session support
5. **+US5**: Delete Operations = Cleanup capabilities
6. **+Polish**: Production-ready quality

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Phase 1: Setup | 4 | Dependencies and project structure |
| Phase 2: Foundational | 21 | Models, schemas, tools, agent config |
| Phase 3: US1 (P1) | 8 | Chat-based task creation |
| Phase 4: US2 (P1) | 3 | View and query tasks |
| Phase 5: US3 (P2) | 4 | Complete and update tasks |
| Phase 6: US4 (P2) | 6 | Conversation persistence |
| Phase 7: US5 (P3) | 5 | Delete tasks and conversations |
| Phase 8: Chat UI | 16 | Floating widget frontend |
| Phase 9: Polish | 9 | Error handling, performance, validation |
| **Total** | **76** | |

**Parallel Opportunities**: 35+ tasks can run in parallel within their phases
**MVP Tasks**: ~30 (Phases 1-3 + partial Phase 8)
