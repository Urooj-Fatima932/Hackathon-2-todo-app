from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(min_length=1, max_length=200, description="Task title (required)")
    description: Optional[str] = Field(default=None, max_length=1000, description="Optional task description")


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200, description="New task title (optional)")
    description: Optional[str] = Field(default=None, max_length=1000, description="New task description (optional)")


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for task list response."""
    tasks: list[TaskResponse]
    total: int
