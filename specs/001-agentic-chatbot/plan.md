# Implementation Plan: Agentic Task Management Chatbot

**Branch**: `001-agentic-chatbot` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-agentic-chatbot/spec.md`

## Summary

Build a stateless agentic chatbot that enables natural language task management through a floating chat widget. The system uses OpenAI Agents SDK with MCP-style function tools to interpret user commands (create/read/update/delete tasks) and responds conversationally. Conversations and messages are persisted to PostgreSQL, enabling multi-session continuity while keeping the API server stateless.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5 (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.115+, SQLModel 0.0.22, OpenAI Agents SDK (`openai-agents`), PyJWT 2.9
- Frontend: Next.js 14 (App Router), React 18, Tailwind CSS, @chatscope/chat-ui-kit-react
**Storage**: PostgreSQL via Neon (existing), SQLModel ORM
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Web application (desktop/mobile browsers)
**Project Type**: Web (frontend + backend)
**Performance Goals**: <5s for task creation, <3s for task listing (per spec SC-001, SC-002)
**Constraints**: 30s AI timeout, load last 20 messages per conversation (FR-022, FR-027)
**Scale/Scope**: Single-tenant multi-user, existing user base from todo app

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Test-First | ⚠️ PENDING | Will define tests before implementation in tasks.md |
| Smallest Viable Change | ✅ PASS | Reuses existing Task model, auth, API patterns |
| No Hardcoded Secrets | ✅ PASS | OpenAI API key via .env, existing pattern |
| User Isolation | ✅ PASS | JWT auth + user_id filtering on all operations |

## Project Structure

### Documentation (this feature)

```text
specs/001-agentic-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI schemas)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py                 # Add chat router
│   ├── models.py               # Add Conversation, Message models
│   ├── schemas.py              # Add chat request/response schemas
│   ├── routes/
│   │   ├── tasks.py            # Existing (expose as MCP tools)
│   │   └── chat.py             # NEW: Chat endpoints
│   ├── agent/                  # NEW: AI agent module
│   │   ├── __init__.py
│   │   ├── agent.py            # OpenAI Agent configuration
│   │   └── tools.py            # MCP-style function tools
│   └── auth/
│       └── dependencies.py     # Existing (reuse CurrentUser)
├── tests/
│   ├── test_chat.py            # NEW: Chat endpoint tests
│   └── test_agent_tools.py     # NEW: Tool unit tests

frontend/
├── app/
│   ├── tasks/page.tsx          # Existing (add chat widget)
│   └── layout.tsx              # Add ChatWidget provider
├── components/
│   ├── chat/                   # NEW: Chat components
│   │   ├── ChatWidget.tsx      # Floating widget container
│   │   ├── ChatMessages.tsx    # Message display
│   │   ├── ChatInput.tsx       # Message input
│   │   └── ConversationList.tsx # Sidebar conversation list
│   └── ui/                     # Existing shadcn components
└── lib/
    ├── api.ts                  # Add chat API methods
    └── types.ts                # Add chat types
```

**Structure Decision**: Extend existing web application structure. Backend adds new `agent/` module and `routes/chat.py`. Frontend adds new `components/chat/` directory with floating widget pattern.

## Complexity Tracking

> No constitution violations requiring justification.

---

## Phase 0: Research

### Research Tasks

1. **OpenAI Agents SDK Integration Pattern**
   - How to configure stateless agent with function tools
   - Conversation history injection pattern (last 20 messages)
   - Streaming vs non-streaming response handling

2. **MCP-Style Function Tools Design**
   - Tool schema definition for task CRUD operations
   - Return format for tool results (structured JSON)
   - Error handling in tool execution

3. **Floating Chat Widget Implementation**
   - React pattern for persistent widget across pages
   - State management for expand/collapse
   - Conversation switching UX

### Research Findings

#### 1. OpenAI Agents SDK Pattern

**Decision**: Use `openai-agents` SDK with synchronous function tools

**Rationale**:
- SDK provides clean abstraction for tool calling
- Handles conversation context automatically when messages provided
- Supports structured tool definitions with Pydantic

**Alternatives Considered**:
- Raw OpenAI API: More control but requires manual tool dispatch
- LangChain: Heavier dependency, unnecessary abstractions for this use case

**Implementation Pattern**:
```python
from agents import Agent, Runner

agent = Agent(
    name="TaskBot",
    instructions="You are a helpful task management assistant...",
    tools=[add_task, list_tasks, complete_task, update_task, delete_task]
)

# Stateless: inject history on each request
result = Runner.run_sync(
    agent,
    messages=[{"role": m.role, "content": m.content} for m in history],
    input=user_message
)
```

#### 2. MCP-Style Function Tools

**Decision**: Define tools as decorated Python functions with Pydantic schemas

**Rationale**:
- Agents SDK supports `@function_tool` decorator
- Pydantic provides validation and schema generation
- Matches existing FastAPI patterns in codebase

**Alternatives Considered**:
- JSON schema definitions: Verbose, no runtime validation
- Dataclasses: Less validation support than Pydantic

**Tool Schema Pattern**:
```python
from agents import function_tool
from pydantic import BaseModel

class AddTaskInput(BaseModel):
    title: str
    description: str | None = None

@function_tool
def add_task(input: AddTaskInput, context: RunContext) -> dict:
    """Add a new task for the user."""
    user_id = context.context["user_id"]
    # Create task in database
    return {"task_id": task.id, "title": task.title, "status": "created"}
```

#### 3. Floating Chat Widget

**Decision**: Use React Context + Portal for persistent widget

**Rationale**:
- Context preserves state across page navigation
- Portal renders widget outside normal DOM hierarchy
- @chatscope/chat-ui-kit provides accessible, tested components

**Alternatives Considered**:
- Global state (Zustand/Redux): Overkill for single widget
- iframe: Poor integration, styling issues
- Custom from scratch: More effort, accessibility risks

**Implementation Pattern**:
```tsx
// ChatProvider wraps layout
<ChatProvider>
  {children}
  <ChatWidget />  {/* Rendered via portal */}
</ChatProvider>
```

---

## Phase 1: Data Model & Contracts

### Data Model

**New Entities**:

#### Conversation
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID (string) | PK | Auto-generated via uuid4 |
| user_id | UUID (string) | FK → users.id, NOT NULL, indexed | Owner |
| title | string | max 100 chars, nullable | Auto-generated from first message |
| created_at | datetime | NOT NULL | UTC timestamp |
| updated_at | datetime | NOT NULL | Updated on new message |

**Relationships**: User 1:N Conversation, Conversation 1:N Message

#### Message
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID (string) | PK | Auto-generated via uuid4 |
| conversation_id | UUID (string) | FK → conversations.id, NOT NULL, indexed | Parent conversation |
| role | string | enum: 'user', 'assistant' | Message sender type |
| content | text | 1-10000 chars, NOT NULL | Message text content |
| created_at | datetime | NOT NULL | UTC timestamp |

**Cascade Delete**: When Conversation deleted, all Messages cascade delete.

**Existing Entities (unchanged)**:
- **User**: id, email, hashed_password, name, created_at, updated_at
- **Task**: id, user_id, title, description, is_completed, created_at, updated_at

### API Contracts

#### Chat Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `POST /api/chat` | POST | JWT | Send message, get AI response |
| `GET /api/conversations` | GET | JWT | List user's conversations |
| `GET /api/conversations/{id}` | GET | JWT | Get conversation with messages |
| `DELETE /api/conversations/{id}` | DELETE | JWT | Delete conversation (cascade) |

#### POST /api/chat

**Request Schema** (`ChatRequest`):
```json
{
  "message": "string (1-1000 chars, required)",
  "conversation_id": "string (UUID, optional)"
}
```

**Response Schema** (`ChatResponse`):
```json
{
  "response": "string (AI response text)",
  "conversation_id": "string (UUID)",
  "tool_calls": [
    {
      "tool": "string (tool name)",
      "args": "object (tool arguments)",
      "result": "object (tool result)"
    }
  ]
}
```

**Error Responses**:
| Status | Condition | Response |
|--------|-----------|----------|
| 400 | Message empty or >1000 chars | `{"detail": "Message must be 1-1000 characters"}` |
| 401 | Invalid/missing JWT | `{"detail": "Could not validate credentials"}` |
| 404 | conversation_id not found/not owned | `{"detail": "Conversation not found"}` |
| 504 | AI service timeout (30s) | `{"detail": "AI service timeout. Please try again."}` |

#### GET /api/conversations

**Response Schema** (`ConversationListResponse`):
```json
{
  "conversations": [
    {
      "id": "string (UUID)",
      "title": "string | null",
      "created_at": "string (ISO datetime)",
      "updated_at": "string (ISO datetime)"
    }
  ],
  "total": "integer"
}
```

#### GET /api/conversations/{id}

**Response Schema** (`ConversationDetailResponse`):
```json
{
  "id": "string (UUID)",
  "title": "string | null",
  "created_at": "string (ISO datetime)",
  "updated_at": "string (ISO datetime)",
  "messages": [
    {
      "id": "string (UUID)",
      "role": "string (user|assistant)",
      "content": "string",
      "created_at": "string (ISO datetime)"
    }
  ]
}
```

**Note**: Returns last 20 messages ordered by created_at ascending (oldest first).

#### DELETE /api/conversations/{id}

**Response**: 204 No Content on success
**Error**: 404 if not found or not owned by user

---

## Architecture Decisions

### AD-001: Stateless API Design

**Context**: System must support horizontal scaling per FR-026.

**Decision**: No server-side session state; reload history from DB on each request.

**Consequences**:
- (+) Enables horizontal scaling without sticky sessions
- (+) Simplifies deployment and failover
- (-) Slight latency increase for loading 20 messages (~50ms)
- (-) Higher DB read load per request

**Alternatives Rejected**:
- Redis session cache: Adds operational complexity, single point of failure
- In-memory cache with TTL: Doesn't work with multiple instances

### AD-002: Tool Results Not Persisted

**Context**: Tool calls show what actions the AI performed per FR-023.

**Decision**: Tool call results returned in API response only, not stored in database.

**Consequences**:
- (+) Reduces storage requirements
- (+) Avoids stale data (task state may change after tool call)
- (-) Cannot replay or audit tool execution history
- (-) Tool calls not shown when loading conversation history

**Alternatives Rejected**:
- Store tool calls as special messages: Complicates message model
- Separate tool_calls table: Storage overhead for transient data

### AD-003: Floating Widget vs Dedicated Page

**Context**: Chat should be accessible from any page per FR-020.

**Decision**: Floating widget in bottom-right corner, accessible from all pages.

**Consequences**:
- (+) Immediate access to AI assistant without navigation
- (+) Matches modern SaaS patterns (Intercom, Drift)
- (-) Adds complexity to frontend layout
- (-) Widget state must persist across navigation

**Alternatives Rejected**:
- Dedicated /chat page: Requires navigation, loses task context
- Sidebar drawer: Takes more screen space, blocks content

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OpenAI API latency/failures | Medium | High | 30s timeout, retry button, graceful error messages, preserve user message on failure |
| Token context overflow (>20 msgs) | Low | Medium | Limit to 20 messages, implement summarization in future if needed |
| Tool execution errors | Low | Medium | Validate user_id in every tool, atomic DB operations, return friendly errors |
| Ambiguous user intent | Medium | Low | Agent asks clarifying questions (FR-017), contextual pronoun resolution |

---

## Dependencies

### New Python Packages
```
openai-agents>=0.1.0
```

### New NPM Packages
```
@chatscope/chat-ui-kit-react@^2.0.0
```

### Environment Variables
```
OPENAI_API_KEY=sk-...  # Required for AI agent
```

---

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks with test cases
2. Review and approve task breakdown
3. Begin Red-Green-Refactor cycle for each task

---

**Generated Artifacts**:
- `specs/001-agentic-chatbot/plan.md` (this file)

**Artifacts to Generate** (via `/sp.tasks`):
- `specs/001-agentic-chatbot/data-model.md`
- `specs/001-agentic-chatbot/contracts/chat-api.yaml`
- `specs/001-agentic-chatbot/quickstart.md`
- `specs/001-agentic-chatbot/tasks.md`
