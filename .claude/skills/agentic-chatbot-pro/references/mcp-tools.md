# MCP Tools Specification

## Tool Pattern for Any Entity

Replace `{entity}` with your domain entity (task, note, order, etc.).

### Tool: add_{entity}

| Field | Value |
|-------|-------|
| Purpose | Create new {entity} |
| Parameters | `user_id` (string, required), `title` (string, required), `description` (string, optional) |
| Returns | `{entity}_id`, `status`, `title` |

**Example:**
```json
// Input
{"user_id": "user123", "title": "Buy groceries", "description": "Milk, eggs, bread"}

// Output
{"task_id": 5, "status": "created", "title": "Buy groceries"}
```

### Tool: list_{entities}

| Field | Value |
|-------|-------|
| Purpose | Retrieve {entities} list |
| Parameters | `user_id` (string, required), `status` (string, optional: "all", "pending", "completed") |
| Returns | Array of {entity} objects |

**Example:**
```json
// Input
{"user_id": "user123", "status": "pending"}

// Output
[{"id": 1, "title": "Buy groceries", "completed": false}, ...]
```

### Tool: get_{entity}

| Field | Value |
|-------|-------|
| Purpose | Get single {entity} details |
| Parameters | `user_id` (string, required), `{entity}_id` (integer, required) |
| Returns | Full {entity} object |

### Tool: update_{entity}

| Field | Value |
|-------|-------|
| Purpose | Modify {entity} |
| Parameters | `user_id` (string, required), `{entity}_id` (integer, required), `title` (string, optional), `description` (string, optional) |
| Returns | `{entity}_id`, `status`, `title` |

**Example:**
```json
// Input
{"user_id": "user123", "task_id": 1, "title": "Buy groceries and fruits"}

// Output
{"task_id": 1, "status": "updated", "title": "Buy groceries and fruits"}
```

### Tool: complete_{entity}

| Field | Value |
|-------|-------|
| Purpose | Mark {entity} as complete |
| Parameters | `user_id` (string, required), `{entity}_id` (integer, required) |
| Returns | `{entity}_id`, `status`, `title` |

**Example:**
```json
// Input
{"user_id": "user123", "task_id": 3}

// Output
{"task_id": 3, "status": "completed", "title": "Call mom"}
```

### Tool: delete_{entity}

| Field | Value |
|-------|-------|
| Purpose | Remove {entity} |
| Parameters | `user_id` (string, required), `{entity}_id` (integer, required) |
| Returns | `{entity}_id`, `status`, `title` |

**Example:**
```json
// Input
{"user_id": "user123", "task_id": 2}

// Output
{"task_id": 2, "status": "deleted", "title": "Old task"}
```

---

## MCP Server Implementation

```python
# app/mcp/server.py
from mcp.server.fastmcp import FastMCP
from app.database import async_session_factory
from app.repositories.task_repo import TaskRepository

mcp = FastMCP("{Entity} MCP Server")

@mcp.tool()
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Create a new task.

    Args:
        user_id: The user's ID.
        title: The task title.
        description: Optional task description.
    """
    async with async_session_factory() as db:
        repo = TaskRepository(db)
        task = await repo.create(user_id, title, description)
        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title,
        }

@mcp.tool()
async def list_tasks(user_id: str, status: str = "all") -> list[dict]:
    """List tasks for a user.

    Args:
        user_id: The user's ID.
        status: Filter by status ("all", "pending", "completed").
    """
    async with async_session_factory() as db:
        repo = TaskRepository(db)
        tasks = await repo.list(user_id, status)
        return [
            {"id": t.id, "title": t.title, "completed": t.completed}
            for t in tasks
        ]

@mcp.tool()
async def complete_task(user_id: str, task_id: int) -> dict:
    """Mark a task as complete.

    Args:
        user_id: The user's ID.
        task_id: The task ID to complete.
    """
    async with async_session_factory() as db:
        repo = TaskRepository(db)
        task = await repo.get(user_id, task_id)
        if not task:
            return {"error": f"Task {task_id} not found"}
        await repo.complete(task_id)
        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title,
        }

@mcp.tool()
async def delete_task(user_id: str, task_id: int) -> dict:
    """Delete a task.

    Args:
        user_id: The user's ID.
        task_id: The task ID to delete.
    """
    async with async_session_factory() as db:
        repo = TaskRepository(db)
        task = await repo.get(user_id, task_id)
        if not task:
            return {"error": f"Task {task_id} not found"}
        title = task.title
        await repo.delete(task_id)
        return {
            "task_id": task_id,
            "status": "deleted",
            "title": title,
        }

@mcp.tool()
async def update_task(
    user_id: str,
    task_id: int,
    title: str = None,
    description: str = None,
) -> dict:
    """Update a task.

    Args:
        user_id: The user's ID.
        task_id: The task ID to update.
        title: New title (optional).
        description: New description (optional).
    """
    async with async_session_factory() as db:
        repo = TaskRepository(db)
        task = await repo.get(user_id, task_id)
        if not task:
            return {"error": f"Task {task_id} not found"}
        task = await repo.update(task_id, title=title, description=description)
        return {
            "task_id": task.id,
            "status": "updated",
            "title": task.title,
        }
```

---

## Mounting in FastAPI

```python
# app/main.py
from fastapi import FastAPI
from app.mcp.server import mcp

app = FastAPI()

# Mount MCP server at /mcp
app.mount("/mcp", mcp.get_app())
```

---

## Key Points

1. **User ID in every tool** - Multi-tenancy, isolate user data
2. **Consistent return format** - `{entity}_id`, `status`, `title`
3. **Clear docstrings** - Agent uses these to understand tools
4. **Error handling** - Return error dict, don't raise exceptions
5. **DB session per tool** - Create fresh session, don't share
