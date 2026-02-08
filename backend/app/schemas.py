from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


# User Schemas
class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, max_length=100, description="User password (min 8 characters)")
    name: Optional[str] = Field(default=None, max_length=100, description="Optional user display name")


class UserResponse(BaseModel):
    """Schema for user response."""
    id: str
    email: str
    name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(description="User email address")
    password: str = Field(description="User password")


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Task Schemas
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
    id: str
    user_id: str
    title: str
    description: Optional[str]
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for task list response."""
    tasks: list[TaskResponse]
    total: int
