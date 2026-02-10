# Complete Development Flow

Step-by-step guide to building an agentic chatbot using all related skills.

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AGENTIC CHATBOT DEVELOPMENT FLOW                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   STEP 1     │    │   STEP 2     │    │   STEP 3     │    │   STEP 4     │    │   STEP 5     │
│   Database   │───▶│   Backend    │───▶│   MCP Tools  │───▶│   Agent +    │───▶│   Frontend   │
│              │    │   Structure  │    │              │    │   Flow       │    │   Chat UI    │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
       │                   │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼                   ▼
  neon-db-pro        fastapi-pro         mcp-builder       openai-agents       chatkit-pro
                                                            -sdk-pro
                                                          agentic-chatbot
                                                              -pro
```

---

## Step 1: Database Setup

**Skill:** `neon-db-pro`

### What to Ask Claude
```
"Set up Neon PostgreSQL with SQLAlchemy async for my chatbot"
```

### What Gets Created
- Neon database connection
- SQLAlchemy async engine
- Connection pooling
- Alembic migrations setup

### Tables Needed
```sql
-- messages: Conversation history
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,        -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- {entity}: Your domain data (e.g., tasks)
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Output Files
```
backend/
├── app/
│   ├── database.py          # Async SQLAlchemy setup
│   └── models/
│       ├── message.py       # Message model
│       └── task.py          # Entity model
└── alembic/
    └── versions/
        └── 001_initial.py   # Migration
```

---

## Step 2: Backend Structure

**Skill:** `fastapi-pro`

### What to Ask Claude
```
"Create FastAPI backend structure for a task chatbot with repositories"
```

### What Gets Created
- Project structure
- Pydantic schemas
- Repository pattern
- Router setup

### Output Files
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── schemas/
│   │   ├── chat.py          # ChatRequest, ChatResponse
│   │   └── task.py          # TaskCreate, TaskResponse
│   ├── repositories/
│   │   ├── message_repo.py  # Message CRUD
│   │   └── task_repo.py     # Task CRUD
│   └── routers/
│       └── chat.py          # /api/chat endpoint
└── requirements.txt
```

---

## Step 3: MCP Tools

**Skill:** `mcp-builder`

### What to Ask Claude
```
"Create MCP server with tools for task CRUD operations"
```

### What Gets Created
- FastMCP server
- CRUD tools (add, list, complete, delete, update)
- Tool documentation for agent

### Output Files
```
backend/app/mcp/
├── __init__.py
└── server.py                # MCP tools
```

### Tools Generated
```python
@mcp.tool()
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Create a new task."""

@mcp.tool()
async def list_tasks(user_id: str, status: str = "all") -> list[dict]:
    """List tasks for a user."""

@mcp.tool()
async def complete_task(user_id: str, task_id: int) -> dict:
    """Mark a task as complete."""

@mcp.tool()
async def delete_task(user_id: str, task_id: int) -> dict:
    """Delete a task."""

@mcp.tool()
async def update_task(user_id: str, task_id: int, ...) -> dict:
    """Update a task."""
```

---

## Step 4: Agent + 9-Step Flow

**Skills:** `openai-agents-sdk-pro` + `agentic-chatbot-pro`

### What to Ask Claude
```
"Create the chat service with 9-step stateless flow and agent configuration"
```

### What Gets Created
- Agent configuration
- Chat service (9-step flow)
- MCP integration

### The 9-Step Flow
```
1. Receive user message
2. Fetch conversation history from database
3. Build message array (history + new message)
4. Store user message in database
5. Run agent with MCP tools
6. Agent invokes appropriate MCP tool(s)
7. Store assistant response in database
8. Return response to client
9. Server holds NO state (ready for next request)
```

### Output Files
```
backend/app/
├── services/
│   └── chat_service.py      # 9-step flow
└── agents/
    └── task_agent.py        # Agent config (optional)
```

### Agent Configuration
```python
agent = Agent(
    name="TaskAssistant",
    instructions="""You are a helpful task management assistant.

When user wants to:
- Add/create/remember → use add_task
- Show/list/view → use list_tasks
- Done/complete/finish → use complete_task
- Delete/remove/cancel → use delete_task
- Change/update/rename → use update_task

Always confirm actions with a friendly response.""",
    mcp_servers=[mcp_server],
)
```

---

## Step 5: Frontend Chat UI

**Skill:** `chatkit-pro`

### What to Ask Claude
```
"Create chat UI for my task chatbot using chatscope"
```

OR

```
"Create custom chat components with Tailwind for my chatbot"
```

### What Gets Created
- Chat components
- Message state management
- API integration
- Streaming support (optional)

### Output Files
```
frontend/
├── src/
│   ├── app/
│   │   └── page.tsx         # Chat page
│   ├── components/
│   │   └── chat/
│   │       ├── ChatContainer.tsx
│   │       ├── MessageList.tsx
│   │       ├── Message.tsx
│   │       ├── MessageInput.tsx
│   │       └── TypingIndicator.tsx
│   └── hooks/
│       └── useChat.ts       # State management
├── package.json
└── .env.local
```

---

## Step 6 (Optional): Authentication

**Skill:** `fullstack-auth`

### What to Ask Claude
```
"Add authentication to my chatbot with Better Auth"
```

### What Gets Created
- User authentication
- Protected routes
- Session management

---

## Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FULL STACK ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────────┘

  FRONTEND (chatkit-pro)              BACKEND (fastapi-pro + agentic-chatbot-pro)
  ─────────────────────               ─────────────────────────────────────────────

  ┌─────────────────┐                 ┌─────────────────────────────────────────┐
  │   Next.js App   │                 │              FastAPI                     │
  │                 │                 │                                          │
  │  ┌───────────┐  │   POST /chat    │  ┌────────────────────────────────────┐ │
  │  │MessageList│  │ ───────────────▶│  │         Chat Service               │ │
  │  │           │  │                 │  │  (9-step stateless flow)           │ │
  │  │ • User msg│  │                 │  │                                    │ │
  │  │ • Bot msg │  │                 │  │  1. Fetch history ─────────────────│─┼─▶ DB
  │  │ • Typing..│  │                 │  │  2. Build messages                 │ │
  │  └───────────┘  │                 │  │  3. Store user msg ────────────────│─┼─▶ DB
  │                 │                 │  │  4. Run Agent ─────────┐           │ │
  │  ┌───────────┐  │                 │  │                        ▼           │ │
  │  │   Input   │  │                 │  │  ┌─────────────────────────────┐  │ │
  │  │  [Send]   │  │                 │  │  │    OpenAI Agent             │  │ │
  │  └───────────┘  │                 │  │  │    (openai-agents-sdk-pro)  │  │ │
  │                 │                 │  │  │                             │  │ │
  └─────────────────┘                 │  │  │  "Add task to buy milk"     │  │ │
          │                           │  │  │         │                   │  │ │
          │                           │  │  │         ▼                   │  │ │
          │◀──────────────────────────│  │  │  Decides: call add_task    │  │ │
          │   {response: "Added..."}  │  │  └──────────────┬──────────────┘  │ │
          │                           │  │                 │                 │ │
          │                           │  │                 ▼                 │ │
          │                           │  │  ┌─────────────────────────────┐  │ │
          │                           │  │  │      MCP Server             │  │ │
          │                           │  │  │      (mcp-builder)          │  │ │
          │                           │  │  │                             │  │ │
          │                           │  │  │  @mcp.tool()                │  │ │
          │                           │  │  │  add_task(title) ───────────│──┼─▶ DB
          │                           │  │  │                             │  │ │
          │                           │  │  │  Returns: {task_id: 1}      │  │ │
          │                           │  │  └─────────────────────────────┘  │ │
          │                           │  │                                   │ │
          │                           │  │  5. Store response ───────────────│─┼─▶ DB
          │                           │  │  6. Return                        │ │
          │                           │  └────────────────────────────────────┘ │
          │                           └─────────────────────────────────────────┘

                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │    Database     │
                                               │  (neon-db-pro)  │
                                               │                 │
                                               │  • messages     │
                                               │  • tasks        │
                                               └─────────────────┘
```

---

## Quick Start Commands

### Step 1: Database
```
"Set up Neon PostgreSQL for my task chatbot"
```

### Step 2: Backend
```
"Create FastAPI backend with task and message models"
```

### Step 3: MCP
```
"Create MCP tools for task CRUD"
```

### Step 4: Agent
```
"Create chat service with 9-step flow and agent"
```

### Step 5: Frontend
```
"Create chat UI with chatscope for my task chatbot"
```

---

## Why This Architecture?

| Benefit | Explanation |
|---------|-------------|
| **Stateless** | Server restart won't lose conversations |
| **Scalable** | Multiple backend instances, any can handle any request |
| **Testable** | Each request is independent |
| **Maintainable** | Clear separation: UI → API → Agent → Tools → DB |
| **Extensible** | Add new tools without changing frontend |
