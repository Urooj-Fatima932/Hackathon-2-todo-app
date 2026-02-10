"""MCP-style function tools for task management.

These tools are exposed to the AI agent to perform CRUD operations on tasks.
Following the openai-agents-sdk-pro skill pattern with @function_tool decorator.
"""
from typing import Optional
from datetime import datetime
from agents import function_tool, RunContextWrapper
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.models import Task
from app.database import get_session


# Context class for user information
class UserContext(BaseModel):
    """Context containing user information for tool execution."""
    user_id: str
    db: Session = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True


# Tool Input Schemas
class AddTaskInput(BaseModel):
    """Input schema for add_task tool."""
    title: str = Field(description="The task title (1-200 chars)")
    description: Optional[str] = Field(default=None, description="Optional task description")


class TaskIdInput(BaseModel):
    """Input schema for tools that need only task_id."""
    task_id: str = Field(description="The task ID")


class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool."""
    task_id: str = Field(description="The task ID to update")
    title: Optional[str] = Field(default=None, description="New title (optional)")
    description: Optional[str] = Field(default=None, description="New description (optional)")


class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool."""
    status: Optional[str] = Field(
        default="all",
        description="Filter by status: 'all', 'pending', or 'completed'"
    )


# Function Tools

@function_tool
def add_task(ctx: RunContextWrapper[UserContext], title: str, description: Optional[str] = None) -> dict:
    """Create a new task for the user.

    Args:
        ctx: Run context containing user_id and database session.
        title: The task title (required, 1-200 characters).
        description: Optional task description.

    Returns:
        Dictionary with task_id, status, and title of created task.
    """
    user_id = ctx.context.user_id
    db = ctx.context.db

    # Create task
    task = Task(
        user_id=user_id,
        title=title[:200],  # Enforce max length
        description=description[:1000] if description else None,
        is_completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "task_id": task.id,
        "status": "created",
        "title": task.title
    }


@function_tool
def list_tasks(ctx: RunContextWrapper[UserContext], status: str = "all") -> list[dict]:
    """List tasks for the current user.

    Args:
        ctx: Run context containing user_id and database session.
        status: Filter by status - 'all', 'pending', or 'completed'.

    Returns:
        List of task dictionaries with id, title, description, and completed status.
    """
    user_id = ctx.context.user_id
    db = ctx.context.db

    # Build query
    query = select(Task).where(Task.user_id == user_id)

    if status == "pending":
        query = query.where(Task.is_completed == False)
    elif status == "completed":
        query = query.where(Task.is_completed == True)

    query = query.order_by(Task.created_at.desc())
    tasks = db.exec(query).all()

    return [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.is_completed
        }
        for task in tasks
    ]


@function_tool
def get_task(ctx: RunContextWrapper[UserContext], task_id: str) -> dict:
    """Get details of a specific task.

    Args:
        ctx: Run context containing user_id and database session.
        task_id: The ID of the task to retrieve.

    Returns:
        Task details or error if not found.
    """
    user_id = ctx.context.user_id
    db = ctx.context.db

    task = db.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        return {"error": f"Task not found", "task_id": task_id}

    return {
        "task_id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.is_completed,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat()
    }


@function_tool
def update_task(
    ctx: RunContextWrapper[UserContext],
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> dict:
    """Update an existing task's title or description.

    Args:
        ctx: Run context containing user_id and database session.
        task_id: The ID of the task to update.
        title: New title (optional).
        description: New description (optional).

    Returns:
        Updated task details or error if not found.
    """
    user_id = ctx.context.user_id
    db = ctx.context.db

    task = db.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        return {"error": f"Task not found", "task_id": task_id}

    # Update fields if provided
    if title is not None:
        task.title = title[:200]
    if description is not None:
        task.description = description[:1000] if description else None

    task.updated_at = datetime.utcnow()
    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "task_id": task.id,
        "status": "updated",
        "title": task.title
    }


@function_tool
def complete_task(ctx: RunContextWrapper[UserContext], task_id: str) -> dict:
    """Mark a task as completed.

    Args:
        ctx: Run context containing user_id and database session.
        task_id: The ID of the task to complete.

    Returns:
        Completion confirmation or error if not found.
    """
    user_id = ctx.context.user_id
    db = ctx.context.db

    task = db.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        return {"error": f"Task not found", "task_id": task_id}

    task.is_completed = True
    task.updated_at = datetime.utcnow()
    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "task_id": task.id,
        "status": "completed",
        "title": task.title
    }


@function_tool
def delete_task(ctx: RunContextWrapper[UserContext], task_id: str) -> dict:
    """Delete a task permanently.

    Args:
        ctx: Run context containing user_id and database session.
        task_id: The ID of the task to delete.

    Returns:
        Deletion confirmation or error if not found.
    """
    user_id = ctx.context.user_id
    db = ctx.context.db

    task = db.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        return {"error": f"Task not found", "task_id": task_id}

    title = task.title
    db.delete(task)
    db.commit()

    return {
        "task_id": task_id,
        "status": "deleted",
        "title": title
    }


# Export all tools
ALL_TOOLS = [
    add_task,
    list_tasks,
    get_task,
    update_task,
    complete_task,
    delete_task,
]
