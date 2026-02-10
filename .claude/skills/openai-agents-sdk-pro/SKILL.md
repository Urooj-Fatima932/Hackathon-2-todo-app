---
name: openai-agents-sdk-pro
description: |
  Generates agentic AI applications using OpenAI Agents SDK with function tools and MCP integration.
  This skill should be used when users want to create AI agents that perform actions (CRUD operations),
  build multi-agent systems with handoffs, integrate MCP servers, or connect agents to FastAPI backends.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

# OpenAI Agents SDK Pro

Generate production-grade agentic AI applications with OpenAI Agents SDK.

## What This Skill Does

- Creates AI agents with function tools for CRUD operations
- Generates MCP servers exposing tools to agents
- Builds multi-agent systems with handoffs
- Integrates agents with FastAPI backends
- Sets up guardrails for input/output validation
- Configures sessions for conversation persistence
- Implements tracing for debugging and monitoring

## What This Skill Does NOT Do

- Create frontend chat UIs (use nextjs-ui-pro or chatkit)
- Deploy agents to production infrastructure
- Handle voice/realtime agent features
- Manage OpenAI API billing or quotas

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing FastAPI routes, database models, service layer |
| **Conversation** | User's specific CRUD operations, entity relationships |
| **Skill References** | Agent patterns from `references/` (tools, MCP, handoffs) |
| **User Guidelines** | Project conventions, error handling patterns |

---

## Clarifications (Ask User)

Ask before generating:

1. **What operations?** - What CRUD actions should the agent perform?
2. **Entities?** - What data models/tables does the agent interact with?
3. **MCP or native tools?** - Expose tools via MCP server or native function tools?
4. **Multi-agent?** - Single agent or multiple specialized agents with handoffs?
5. **Persistence?** - Need conversation history? (SQLite, PostgreSQL)

---

## Architecture Patterns

### Pattern 1: Single Agent with Native Tools

```
User → Agent → Function Tools → Database/API
```

Best for: Simple CRUD chatbots, single-domain operations.

### Pattern 2: Agent with MCP Server

```
User → Agent → MCP Client → MCP Server → Database/API
```

Best for: Decoupled architecture, tool reuse across agents.

### Pattern 3: Multi-Agent with Handoffs

```
User → Triage Agent → [Specialized Agent A]
                    → [Specialized Agent B]
```

Best for: Complex domains, different expertise areas.

---

## Generation Process

```
Gather context → Choose pattern → Generate agent → Create tools → Wire up → Test
```

### Step 1: Analyze Existing Project

```
# Find FastAPI routes
Glob: **/routers/*.py, **/api/**/*.py

# Find database models
Grep: "class.*Base\)|SQLModel" in *.py

# Find existing services
Glob: **/services/*.py

# Check for existing agents
Grep: "from agents import|openai-agents" in *.py
```

### Step 2: Generate Based on Pattern

| Pattern | Files to Generate |
|---------|-------------------|
| Native tools | `agents/{name}.py`, `tools/{entity}_tools.py` |
| MCP server | `mcp_server.py`, `agents/{name}.py` |
| Multi-agent | `agents/triage.py`, `agents/{specialist}.py` |

### Step 3: Create Files

Generate in this order:

1. **Tools** (`tools/{entity}_tools.py`)
   - Function tools with @function_tool decorator
   - Pydantic models for tool inputs
   - Error handling

2. **Agent** (`agents/{name}.py`)
   - Agent configuration with instructions
   - Tool registration
   - Handoffs (if multi-agent)

3. **MCP Server** (`mcp_server.py`) - If MCP pattern
   - Tool definitions
   - FastAPI integration

4. **Runner** (`agent_runner.py`)
   - Session configuration
   - Streaming support
   - Tracing setup

5. **FastAPI Integration** (`routers/chat.py`)
   - Chat endpoint
   - Session management
   - Error handling

---

## Output Structure

```
project/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── {name}_agent.py      # Agent definition
│   │   └── runner.py            # Agent runner utilities
│   ├── tools/
│   │   ├── __init__.py
│   │   └── {entity}_tools.py    # Function tools
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── server.py            # MCP server (if needed)
│   ├── routers/
│   │   └── chat.py              # Chat endpoint
│   └── services/                # Business logic (existing)
└── tests/
    └── test_agent.py
```

---

## Standards

| Standard | Reference |
|----------|-----------|
| Function tools | `references/function-tools.md` |
| MCP integration | `references/mcp-integration.md` |
| Agent configuration | `references/agent-config.md` |
| Handoffs | `references/handoffs.md` |
| Sessions | `references/sessions.md` |
| Guardrails | `references/guardrails.md` |
| FastAPI integration | `references/fastapi-integration.md` |

---

## Quick Reference

### Basic Agent

```python
from agents import Agent, Runner

agent = Agent(
    name="NotesAgent",
    instructions="You help users manage their notes. You can create, list, and delete notes.",
    tools=[create_note, list_notes, delete_note],
)

result = await Runner.run(agent, user_message)
```

### Function Tool

```python
from agents import function_tool
from pydantic import BaseModel

class CreateNoteInput(BaseModel):
    title: str
    content: str

@function_tool
async def create_note(title: str, content: str) -> str:
    """Create a new note with the given title and content."""
    # Implementation
    return f"Created note: {title}"
```

### MCP Server with FastAPI

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Notes MCP Server")

@mcp.tool()
async def create_note(title: str, content: str) -> str:
    """Create a new note."""
    return f"Created note: {title}"

# Mount in FastAPI
app.mount("/mcp", mcp.get_app())
```

### Agent with MCP

```python
from agents import Agent
from agents.mcp import MCPServerStreamableHttp

async with MCPServerStreamableHttp(
    name="Notes MCP",
    params={"url": "http://localhost:8000/mcp"}
) as server:
    agent = Agent(
        name="NotesAgent",
        instructions="Manage notes using available tools.",
        mcp_servers=[server],
    )
```

---

## Checklist

Before completing implementation, verify:

- [ ] Tools have clear docstrings (used for LLM understanding)
- [ ] Tool inputs use Pydantic models for complex types
- [ ] Agent instructions clearly describe available capabilities
- [ ] Error handling returns user-friendly messages
- [ ] Session configured for conversation persistence
- [ ] Tracing enabled for debugging
- [ ] FastAPI endpoint handles streaming responses
