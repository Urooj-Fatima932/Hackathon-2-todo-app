"""
MCP Server for Task Management.

Exposes task CRUD operations as MCP tools that the AI agent can invoke.
Following the stateless pattern - each tool receives user_id and operates on DB.
"""

import json
from typing import Optional
from datetime import datetime
from enum import Enum

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict
from sqlmodel import Session, select

from app.models import Task
from app.database import engine

# Initialize MCP Server
mcp = FastMCP("tasks_mcp")


# Response Format Enum
class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    JSON = "json"
    TEXT = "text"


# ============== Input Models ==============

class AddTaskInput(BaseModel):
    """Input for creating a new task."""
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(..., description="The authenticated user's ID")
    title: str = Field(..., description="Task title (1-200 characters)", min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, description="Optional task description (max 1000 chars)")


class ListTasksInput(BaseModel):
    """Input for listing tasks."""
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(..., description="The authenticated user's ID")
    status: Optional[str] = Field(
        default="all",
        description="Filter: 'all', 'pending', or 'completed'"
    )


class TaskIdInput(BaseModel):
    """Input for operations requiring task ID."""
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(..., description="The authenticated user's ID")
    task_id: str = Field(..., description="The task ID to operate on")


class UpdateTaskInput(BaseModel):
    """Input for updating a task."""
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(..., description="The authenticated user's ID")
    task_id: str = Field(..., description="The task ID to update")
    title: Optional[str] = Field(default=None, description="New title (optional)", max_length=200)
    description: Optional[str] = Field(default=None, description="New description (optional)", max_length=1000)


# ============== Helper Functions ==============

def get_db_session() -> Session:
    """Create a new database session."""
    return Session(engine)


def format_task(task: Task) -> dict:
    """Format a task for response."""
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.is_completed,
        "created_at": task.created_at.isoformat() if task.created_at else None
    }


# ============== MCP Tools ==============

@mcp.tool(
    name="add_task",
    annotations={
        "title": "Add Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def add_task(params: AddTaskInput) -> str:
    """
    Create a new task for the user.

    Use this when the user says: add, create, remember, make a task, new task.

    Args:
        params: Contains user_id, title, and optional description.

    Returns:
        JSON with task_id, status='created', and title.
    """
    with get_db_session() as db:
        task = Task(
            user_id=params.user_id,
            title=params.title[:200],
            description=params.description[:1000] if params.description else None,
            is_completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        return json.dumps({
            "task_id": task.id,
            "status": "created",
            "title": task.title
        })


@mcp.tool(
    name="list_tasks",
    annotations={
        "title": "List Tasks",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def list_tasks(params: ListTasksInput) -> str:
    """
    List all tasks for the user.

    Use this when the user says: show, list, view, what are my tasks, show me tasks.

    Args:
        params: Contains user_id and optional status filter.

    Returns:
        JSON array of tasks with id, title, description, completed status.
    """
    with get_db_session() as db:
        query = select(Task).where(Task.user_id == params.user_id)

        if params.status == "pending":
            query = query.where(Task.is_completed == False)
        elif params.status == "completed":
            query = query.where(Task.is_completed == True)

        query = query.order_by(Task.created_at.desc())
        tasks = db.exec(query).all()

        if not tasks:
            return json.dumps({
                "tasks": [],
                "count": 0,
                "message": "No tasks found"
            })

        return json.dumps({
            "tasks": [format_task(t) for t in tasks],
            "count": len(tasks)
        })


@mcp.tool(
    name="get_task",
    annotations={
        "title": "Get Task Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_task(params: TaskIdInput) -> str:
    """
    Get details of a specific task.

    Use this when the user asks about a specific task by ID.

    Args:
        params: Contains user_id and task_id.

    Returns:
        JSON with task details or error if not found.
    """
    with get_db_session() as db:
        task = db.exec(
            select(Task).where(
                Task.id == params.task_id,
                Task.user_id == params.user_id
            )
        ).first()

        if not task:
            return json.dumps({
                "error": "Task not found",
                "task_id": params.task_id
            })

        return json.dumps(format_task(task))


@mcp.tool(
    name="complete_task",
    annotations={
        "title": "Complete Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def complete_task(params: TaskIdInput) -> str:
    """
    Mark a task as completed.

    Use this when the user says: done, complete, finished, mark as done.

    Args:
        params: Contains user_id and task_id.

    Returns:
        JSON with task_id, status='completed', and title.
    """
    with get_db_session() as db:
        task = db.exec(
            select(Task).where(
                Task.id == params.task_id,
                Task.user_id == params.user_id
            )
        ).first()

        if not task:
            return json.dumps({
                "error": "Task not found",
                "task_id": params.task_id
            })

        task.is_completed = True
        task.updated_at = datetime.utcnow()
        db.add(task)
        db.commit()
        db.refresh(task)

        return json.dumps({
            "task_id": task.id,
            "status": "completed",
            "title": task.title
        })


@mcp.tool(
    name="update_task",
    annotations={
        "title": "Update Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def update_task(params: UpdateTaskInput) -> str:
    """
    Update a task's title or description.

    Use this when the user says: change, update, rename, modify, edit task.

    Args:
        params: Contains user_id, task_id, and optional new title/description.

    Returns:
        JSON with task_id, status='updated', and new title.
    """
    with get_db_session() as db:
        task = db.exec(
            select(Task).where(
                Task.id == params.task_id,
                Task.user_id == params.user_id
            )
        ).first()

        if not task:
            return json.dumps({
                "error": "Task not found",
                "task_id": params.task_id
            })

        if params.title is not None:
            task.title = params.title[:200]
        if params.description is not None:
            task.description = params.description[:1000] if params.description else None

        task.updated_at = datetime.utcnow()
        db.add(task)
        db.commit()
        db.refresh(task)

        return json.dumps({
            "task_id": task.id,
            "status": "updated",
            "title": task.title
        })


@mcp.tool(
    name="delete_task",
    annotations={
        "title": "Delete Task",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def delete_task(params: TaskIdInput) -> str:
    """
    Delete a task permanently.

    Use this when the user says: delete, remove, cancel, get rid of task.

    Args:
        params: Contains user_id and task_id.

    Returns:
        JSON with task_id, status='deleted', and title.
    """
    with get_db_session() as db:
        task = db.exec(
            select(Task).where(
                Task.id == params.task_id,
                Task.user_id == params.user_id
            )
        ).first()

        if not task:
            return json.dumps({
                "error": "Task not found",
                "task_id": params.task_id
            })

        title = task.title
        task_id = task.id
        db.delete(task)
        db.commit()

        return json.dumps({
            "task_id": task_id,
            "status": "deleted",
            "title": title
        })


# ============== Server Entry Point ==============

def get_mcp_app():
    """Return the MCP FastAPI app for mounting."""
    return mcp.sse_app()


if __name__ == "__main__":
    # Run as standalone MCP server (stdio transport)
    mcp.run()
