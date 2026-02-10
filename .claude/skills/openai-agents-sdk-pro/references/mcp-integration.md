# MCP Integration

## Overview

Model Context Protocol (MCP) standardizes how AI agents connect to tools. The SDK supports both creating MCP servers and connecting agents to them.

## Creating an MCP Server with FastMCP

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Notes Server")

@mcp.tool()
async def create_note(title: str, content: str) -> str:
    """Create a new note.

    Args:
        title: The note title.
        content: The note content.
    """
    note = await note_service.create(title, content)
    return f"Created note: {note.title} (ID: {note.id})"

@mcp.tool()
async def delete_note(note_id: int) -> str:
    """Delete a note by ID.

    Args:
        note_id: The ID of the note to delete.
    """
    await note_service.delete(note_id)
    return f"Deleted note {note_id}"

@mcp.tool()
async def list_notes() -> str:
    """List all notes."""
    notes = await note_service.list()
    return "\n".join(f"- [{n.id}] {n.title}" for n in notes)
```

## Mounting MCP Server in FastAPI

```python
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP("Notes Server")

# Define tools...

# Mount MCP server
app.mount("/mcp", mcp.get_app())

# Or mount at specific path
app.mount("/api/mcp", mcp.get_app())
```

## Connecting Agent to MCP Server

### Streamable HTTP (Recommended)

```python
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

async def run_agent(user_message: str):
    async with MCPServerStreamableHttp(
        name="Notes MCP",
        params={
            "url": "http://localhost:8000/mcp",
            "timeout": 30,
        },
        cache_tools_list=True,
    ) as server:
        agent = Agent(
            name="NotesAgent",
            instructions="Help users manage notes using available tools.",
            mcp_servers=[server],
        )
        result = await Runner.run(agent, user_message)
        return result.final_output
```

### With Authentication

```python
async with MCPServerStreamableHttp(
    name="Notes MCP",
    params={
        "url": "http://localhost:8000/mcp",
        "headers": {"Authorization": f"Bearer {token}"},
        "timeout": 30,
    },
) as server:
    # ...
```

### stdio MCP Servers (Local Processes)

```python
from agents.mcp import MCPServerStdio

async with MCPServerStdio(
    name="Local MCP",
    params={
        "command": "python",
        "args": ["mcp_server.py"],
    },
) as server:
    agent = Agent(
        name="Agent",
        mcp_servers=[server],
    )
```

## MCP Server with Dependencies

```python
from mcp.server.fastmcp import FastMCP
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    # Setup
    async with get_db_session() as session:
        app.state.db = session
        yield
    # Teardown

mcp = FastMCP("Notes Server", lifespan=lifespan)

@mcp.tool()
async def create_note(title: str, content: str) -> str:
    """Create a note."""
    db = mcp.app.state.db
    # Use db session
```

## Tool Filtering

### Static Filtering

```python
from agents.mcp import create_static_tool_filter

async with MCPServerStreamableHttp(
    name="Notes MCP",
    params={"url": "http://localhost:8000/mcp"},
    tool_filter=create_static_tool_filter(
        allowed_tool_names=["create_note", "list_notes"],
        # Or block specific tools:
        # blocked_tool_names=["delete_note"],
    ),
) as server:
    # Agent only sees create_note and list_notes
```

### Dynamic Filtering

```python
def filter_tools(tool, agent, context):
    # Only allow delete for admin users
    if tool.name == "delete_note":
        return context.user_role == "admin"
    return True

async with MCPServerStreamableHttp(
    name="Notes MCP",
    params={"url": "http://localhost:8000/mcp"},
    tool_filter=filter_tools,
) as server:
    # ...
```

## Approval Workflows

For destructive operations:

```python
async with MCPServerStreamableHttp(
    name="Notes MCP",
    params={"url": "http://localhost:8000/mcp"},
    # Require approval for specific tools
    require_approval={
        "delete_note": "always",
        "create_note": "never",
    },
    # Or globally
    # require_approval="always",
) as server:
    # ...
```

## Agent-Level MCP Config

```python
agent = Agent(
    name="NotesAgent",
    mcp_servers=[server],
    mcp_config={
        "convert_schemas_to_strict": True,
        "failure_error_function": None,  # Propagate errors
    },
)
```

## Multiple MCP Servers

```python
async with MCPServerStreamableHttp(
    name="Notes MCP",
    params={"url": "http://localhost:8000/notes/mcp"},
) as notes_server, MCPServerStreamableHttp(
    name="Users MCP",
    params={"url": "http://localhost:8000/users/mcp"},
) as users_server:
    agent = Agent(
        name="Assistant",
        instructions="Help with notes and user management.",
        mcp_servers=[notes_server, users_server],
    )
```

## Complete FastAPI + MCP Example

```python
# mcp_server.py
from fastapi import FastAPI, Depends
from mcp.server.fastmcp import FastMCP
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.note_service import NoteService

app = FastAPI()
mcp = FastMCP("Notes MCP Server")

# Dependency injection workaround for MCP
_db_session = None

@app.middleware("http")
async def inject_db(request, call_next):
    global _db_session
    async for session in get_db():
        _db_session = session
        break
    response = await call_next(request)
    return response

@mcp.tool()
async def create_note(title: str, content: str) -> str:
    """Create a new note."""
    service = NoteService(_db_session)
    note = await service.create(title=title, content=content)
    return f"Created note: {note.title} (ID: {note.id})"

@mcp.tool()
async def list_notes() -> str:
    """List all notes."""
    service = NoteService(_db_session)
    notes = await service.list()
    if not notes:
        return "No notes found."
    return "\n".join(f"- [{n.id}] {n.title}" for n in notes)

@mcp.tool()
async def delete_note(note_id: int) -> str:
    """Delete a note by ID."""
    service = NoteService(_db_session)
    await service.delete(note_id)
    return f"Deleted note {note_id}"

# Mount MCP
app.mount("/mcp", mcp.get_app())
```

## Best Practices

1. **Use Streamable HTTP** for production (better than SSE)
2. **Cache tool lists** when tools don't change frequently
3. **Set timeouts** to avoid hanging requests
4. **Filter tools** to limit agent capabilities per context
5. **Require approval** for destructive operations
6. **Use authentication** for production MCP servers
7. **Handle errors** gracefully in tool implementations
