---
name: agentic-chatbot-pro
description: |
  Generates production-grade agentic chatbots with stateless architecture using OpenAI Agents SDK,
  MCP tools, and FastAPI. This skill should be used when users want to create chatbots that perform
  CRUD operations through natural language, with database-persisted conversations and horizontal scalability.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

# Agentic Chatbot Pro

Generate complete agentic chatbot applications with stateless server architecture.

## What This Skill Does

- Orchestrates full-stack chatbot development using related skills
- Implements 9-step stateless conversation flow
- Generates MCP tool specifications for any entity CRUD
- Sets up database schema (messages + domain entities)
- Configures agent behavior for natural language understanding

## What This Skill Does NOT Do

- Handle authentication (use fullstack-auth)
- Create complex multi-agent handoffs (use openai-agents-sdk-pro)
- Deploy to cloud infrastructure
- Handle voice/realtime features

---

## Full Development Flow

This skill orchestrates multiple skills to build a complete chatbot:

```
┌─────────────────────────────────────────────────────────────────────┐
│                 AGENTIC CHATBOT DEVELOPMENT FLOW                    │
└─────────────────────────────────────────────────────────────────────┘

  STEP 1          STEP 2          STEP 3          STEP 4          STEP 5
  Database   ──▶  Backend    ──▶  MCP Tools  ──▶  Agent      ──▶  Frontend
                  Structure
     │               │               │               │               │
     ▼               ▼               ▼               ▼               ▼
 neon-db-pro    fastapi-pro    mcp-builder   openai-agents    chatkit-pro
                                              -sdk-pro
```

### Skills Used (In Order)

| Step | Skill | What It Does |
|------|-------|--------------|
| 1 | `neon-db-pro` | PostgreSQL setup, SQLAlchemy async, migrations |
| 2 | `fastapi-pro` | Backend structure (routers, schemas, repos) |
| 3 | `mcp-builder` | MCP server with CRUD tools |
| 4 | `openai-agents-sdk-pro` | Agent config, tool integration |
| 5 | `chatkit-pro` | Frontend chat UI components |
| 6 | `fullstack-auth` | (Optional) Authentication |

### How Skills Connect

```
Frontend (chatkit-pro)
    │
    │ POST /api/chat {user_id, message}
    ▼
FastAPI Backend (fastapi-pro)
    │
    ├──▶ Database (neon-db-pro)
    │    • Fetch conversation history
    │    • Store messages
    │
    └──▶ Chat Service (this skill - 9-step flow)
              │
              ▼
         OpenAI Agent (openai-agents-sdk-pro)
              │
              │ Tool calls
              ▼
         MCP Server (mcp-builder)
              │
              │ CRUD operations
              ▼
         Database (neon-db-pro)
```

---

## Before Implementation

| Source | Gather |
|--------|--------|
| **Conversation** | Entity name, fields, CRUD operations needed |
| **Codebase** | Existing database setup, FastAPI structure |
| **Skill References** | Stateless flow, MCP patterns, templates |
| **Related Skills** | Check if neon-db-pro, fastapi-pro already used |

---

## Clarifications (Ask User)

1. **Entity name?** - What will the chatbot manage? (task, note, order, etc.)
2. **Entity fields?** - What properties? (title, description, status, etc.)
3. **Operations?** - Which actions? (create, list, update, delete, complete)
4. **Database?** - PostgreSQL (neon-db-pro) or SQLite?
5. **Frontend library?** - chatscope, custom, or Vercel AI SDK? (chatkit-pro)

---

## Core Architecture

```
┌──────────────────────────────────────────────────────────┐
│              STATELESS AGENTIC CHATBOT                   │
└──────────────────────────────────────────────────────────┘

 ChatKit UI          FastAPI + Agent           Database
     │                     │                      │
     │ POST /chat          │                      │
     │ {user_id, message}  │                      │
     │ ───────────────────>│                      │
     │                     │ 1. Fetch history     │
     │                     │ ──────────────────── │
     │                     │ 2. Build messages    │
     │                     │ 3. Store user msg    │
     │                     │ ──────────────────── │
     │                     │ 4. Run Agent+MCP     │
     │                     │ ┌────────────────┐   │
     │                     │ │ Agent decides  │   │
     │                     │ │ 5. MCP Tool    │───│──> CRUD
     │                     │ └────────────────┘   │
     │                     │ 6. Store response    │
     │                     │ ──────────────────── │
     │ 7. Return response  │                      │
     │ <───────────────────│                      │
     │                     │ SERVER STATELESS     │
```

---

## 9-Step Stateless Flow

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

**Benefits**: Resilience, horizontal scaling, testability.

---

## MCP Tool Pattern

For entity `{entity}`, generate these tools:

| Tool | Purpose | Parameters |
|------|---------|------------|
| `add_{entity}` | Create | user_id, title, description? |
| `list_{entities}` | List all/filtered | user_id, status? |
| `get_{entity}` | Get one | user_id, {entity}_id |
| `update_{entity}` | Modify | user_id, {entity}_id, fields... |
| `delete_{entity}` | Remove | user_id, {entity}_id |
| `complete_{entity}` | Mark done | user_id, {entity}_id |

**Return format**: `{"{entity}_id": int, "status": str, "title": str}`

---

## Agent Behavior Pattern

| User Says | Agent Should |
|-----------|--------------|
| "Add/Create/Remember X" | Call `add_{entity}` |
| "Show/List/What are my X" | Call `list_{entities}` |
| "Done/Complete/Finished X" | Call `complete_{entity}` |
| "Delete/Remove/Cancel X" | Call `delete_{entity}` |
| "Change/Update/Rename X" | Call `update_{entity}` |

**Always**: Confirm actions, handle errors gracefully.

---

## Project Structure

```
project/
├── frontend/
│   ├── src/app/page.tsx          # ChatKit integration
│   └── .env.local                # OPENAI_DOMAIN_KEY
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI + MCP mount
│   │   ├── config.py             # Settings
│   │   ├── database.py           # Async SQLAlchemy
│   │   ├── models/
│   │   │   ├── message.py        # Conversation history
│   │   │   └── {entity}.py       # Domain entity
│   │   ├── repositories/
│   │   │   ├── message_repo.py
│   │   │   └── {entity}_repo.py
│   │   ├── mcp/
│   │   │   └── server.py         # MCP tools
│   │   ├── services/
│   │   │   └── chat_service.py   # Stateless flow
│   │   └── routers/
│   │       └── chat.py           # /chat endpoint
│   └── alembic/                  # Migrations
├── specs/
│   ├── mcp-tools.md
│   └── agent-behavior.md
└── README.md
```

---

## Generation Process

1. **Ask clarifications** (entity, fields, operations)
2. **Generate database models** (Message + Entity)
3. **Generate repositories** (CRUD operations)
4. **Generate MCP server** (tools for each operation)
5. **Generate chat service** (9-step stateless flow)
6. **Generate FastAPI router** (/chat endpoint)
7. **Generate frontend** (ChatKit page)
8. **Generate specs** (documentation)

---

## Standards

| Component | Reference |
|-----------|-----------|
| Stateless flow implementation | `references/stateless-flow.md` |
| MCP tools template | `references/mcp-tools.md` |
| Agent behavior spec | `references/agent-behavior.md` |
| Database models | `references/database-schema.md` |
| ChatKit setup | `references/chatkit-setup.md` |
| Complete templates | `references/templates.md` |
| Full development guide | `references/development-flow.md` |

---

## Checklist

- [ ] Entity name and fields defined
- [ ] Database setup (neon-db-pro or SQLite)
- [ ] FastAPI structure created (fastapi-pro)
- [ ] Database models created (Message + Entity)
- [ ] Repositories implement CRUD
- [ ] MCP tools match operations (mcp-builder)
- [ ] Agent configured (openai-agents-sdk-pro)
- [ ] Chat service implements 9-step flow
- [ ] FastAPI endpoint with error handling
- [ ] Frontend chat UI (chatkit-pro)
- [ ] Migrations created
- [ ] README with setup instructions
