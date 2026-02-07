from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlmodel import Session, select
from datetime import datetime
from typing import Optional

from app.database import get_session
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse

router = APIRouter(prefix="/api", tags=["tasks"])


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    user_id: str = Path(..., description="User ID"),
    task_data: TaskCreate = None,
    session: Session = Depends(get_session)
):
    """Create a new task for the user."""
    # Create new task
    new_task = Task(
        user_id=user_id,
        title=task_data.title.strip(),
        description=task_data.description.strip() if task_data.description else None,
        completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    
    return new_task


@router.get("/{user_id}/tasks", response_model=TaskListResponse)
def list_tasks(
    user_id: str = Path(..., description="User ID"),
    status_filter: str = Query("all", alias="status", description="Filter by status: all, pending, completed"),
    session: Session = Depends(get_session)
):
    """List all tasks for the user with optional status filtering."""
    # Build query
    query = select(Task).where(Task.user_id == user_id)
    
    # Apply status filter
    if status_filter == "pending":
        query = query.where(Task.completed == False)
    elif status_filter == "completed":
        query = query.where(Task.completed == True)
    
    # Order by newest first
    query = query.order_by(Task.created_at.desc())
    
    # Execute query
    tasks = session.exec(query).all()
    
    return TaskListResponse(tasks=tasks, total=len(tasks))


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    user_id: str = Path(..., description="User ID"),
    task_id: int = Path(..., ge=1, description="Task ID"),
    session: Session = Depends(get_session)
):
    """Get a specific task by ID."""
    task = session.get(Task, task_id)
    
    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    user_id: str = Path(..., description="User ID"),
    task_id: int = Path(..., ge=1, description="Task ID"),
    task_data: TaskUpdate = None,
    session: Session = Depends(get_session)
):
    """Update an existing task."""
    task = session.get(Task, task_id)
    
    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update fields if provided
    if task_data.title is not None:
        task.title = task_data.title.strip()
    if task_data.description is not None:
        task.description = task_data.description.strip() if task_data.description else None
    
    task.updated_at = datetime.utcnow()
    
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return task


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
def toggle_task_completion(
    user_id: str = Path(..., description="User ID"),
    task_id: int = Path(..., ge=1, description="Task ID"),
    session: Session = Depends(get_session)
):
    """Toggle task completion status."""
    task = session.get(Task, task_id)
    
    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Toggle completion
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()
    
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return task


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    user_id: str = Path(..., description="User ID"),
    task_id: int = Path(..., ge=1, description="Task ID"),
    session: Session = Depends(get_session)
):
    """Delete a task permanently."""
    task = session.get(Task, task_id)
    
    if not task or task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    session.delete(task)
    session.commit()
    
    return None
