"""Task management routes with JWT authentication."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from datetime import datetime
from typing import Annotated
import logging

from app.database import get_session
from app.models import Task, User
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
logger = logging.getLogger(__name__)

# Type alias for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_session)]


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: CurrentUser,
    session: DbSession
):
    """Create a new task for the authenticated user."""
    new_task = Task(
        user_id=current_user.id,
        title=task_data.title.strip(),
        description=task_data.description.strip() if task_data.description else None,
        is_completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    logger.info(f"Task created: {new_task.id} by user: {current_user.email}")
    return new_task


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    current_user: CurrentUser,
    session: DbSession,
    status_filter: str = Query("all", alias="status", description="Filter: all, pending, completed")
):
    """List all tasks for the authenticated user with optional status filtering."""
    query = select(Task).where(Task.user_id == current_user.id)

    if status_filter == "pending":
        query = query.where(Task.is_completed == False)
    elif status_filter == "completed":
        query = query.where(Task.is_completed == True)

    query = query.order_by(Task.created_at.desc())
    tasks = session.exec(query).all()

    logger.info(f"Listed {len(tasks)} tasks for user: {current_user.email}")
    return TaskListResponse(tasks=tasks, total=len(tasks))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: CurrentUser,
    session: DbSession
):
    """Get a specific task by ID (must belong to authenticated user)."""
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task.user_id != current_user.id:
        logger.warning(f"User {current_user.email} attempted to access task {task_id} owned by another user")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this task"
        )

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: CurrentUser,
    session: DbSession
):
    """Update an existing task (must belong to authenticated user)."""
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task.user_id != current_user.id:
        logger.warning(f"User {current_user.email} attempted to update task {task_id} owned by another user")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this task"
        )

    # Validate at least one field is provided
    if task_data.title is None and task_data.description is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field (title or description) must be provided"
        )

    if task_data.title is not None:
        task.title = task_data.title.strip()
    if task_data.description is not None:
        task.description = task_data.description.strip() if task_data.description else None

    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    logger.info(f"Task updated: {task_id} by user: {current_user.email}")
    return task


@router.post("/{task_id}/toggle", response_model=TaskResponse)
async def toggle_task_completion(
    task_id: str,
    current_user: CurrentUser,
    session: DbSession
):
    """Toggle task completion status (must belong to authenticated user)."""
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task.user_id != current_user.id:
        logger.warning(f"User {current_user.email} attempted to toggle task {task_id} owned by another user")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this task"
        )

    task.is_completed = not task.is_completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    logger.info(f"Task {task_id} toggled to {task.is_completed} by user: {current_user.email}")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: CurrentUser,
    session: DbSession
):
    """Delete a task permanently (must belong to authenticated user)."""
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task.user_id != current_user.id:
        logger.warning(f"User {current_user.email} attempted to delete task {task_id} owned by another user")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this task"
        )

    session.delete(task)
    session.commit()

    logger.info(f"Task deleted: {task_id} by user: {current_user.email}")
    return None
