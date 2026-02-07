# Data Model: Backend Todo API

**Feature**: Backend Todo API
**Date**: 2026-02-06
**Purpose**: Define database schema, entities, relationships, and validation rules

## Overview

The data model consists of two primary entities: **User** and **Task**. Users are managed by the Better Auth system (external to this API), while Tasks are owned and managed within this API. The relationship is one-to-many: one User owns many Tasks.

## Entity Relationship Diagram

```
┌─────────────────────┐
│ users               │
│ (Better Auth)       │
├─────────────────────┤
│ PK id (VARCHAR)     │◄──┐
│    email (VARCHAR)  │   │
│    name (VARCHAR)   │   │
│    created_at (TS)  │   │
└─────────────────────┘   │
                          │ FK user_id
                          │
┌─────────────────────┐   │
│ tasks               │   │
├─────────────────────┤   │
│ PK id (SERIAL)      │   │
│ FK user_id (VARCHAR)├───┘
│    title (VARCHAR)  │
│    description (TEXT│
│    completed (BOOL) │
│    created_at (TS)  │
│    updated_at (TS)  │
└─────────────────────┘

Indexes:
- tasks.user_id (for user isolation queries)
- tasks.completed (for status filtering)
- tasks (user_id, completed) composite (for filtered lists)
```

## Entities

### User Entity

**Purpose**: Represents an authenticated user in the system. Managed externally by Better Auth.

**Source**: Better Auth authentication system (external)

**Table Name**: `users`

**Columns**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR | PRIMARY KEY | Unique user identifier from Better Auth |
| email | VARCHAR | UNIQUE, NOT NULL | User's email address |
| name | VARCHAR | NULLABLE | User's display name |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    """User model - matches Better Auth schema"""
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="user")
```

**Notes**:
- This table is created and managed by Better Auth
- Backend API has READ-ONLY access to this table
- User ID is extracted from JWT token `sub` claim
- Email is used for display purposes only (not for authentication in this API)

---

### Task Entity

**Purpose**: Represents a todo task owned by a user.

**Table Name**: `tasks`

**Columns**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing task identifier |
| user_id | VARCHAR | FOREIGN KEY (users.id), NOT NULL, INDEX | Owner of the task |
| title | VARCHAR(200) | NOT NULL, LENGTH 1-200 | Task title (required) |
| description | TEXT | NULLABLE, MAX 1000 chars | Optional task details |
| completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | TIMESTAMP | NOT NULL | Task creation timestamp (UTC) |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp (UTC) |

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """Task model - user's todo items"""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="tasks")
```

**Indexes**:
- `PRIMARY KEY (id)` - Automatic unique index for task ID
- `INDEX idx_tasks_user_id (user_id)` - Fast lookup of user's tasks
- `INDEX idx_tasks_completed (completed)` - Fast filtering by completion status
- `INDEX idx_tasks_user_completed (user_id, completed)` - Composite index for filtered user queries

**Constraints**:
- `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE` - Delete tasks when user deleted
- `CHECK (LENGTH(title) >= 1 AND LENGTH(title) <= 200)` - Title length validation
- `CHECK (description IS NULL OR LENGTH(description) <= 1000)` - Description length validation

**SQL DDL**:
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT check_title_length
        CHECK (LENGTH(title) >= 1 AND LENGTH(title) <= 200),

    CONSTRAINT check_description_length
        CHECK (description IS NULL OR LENGTH(description) <= 1000)
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
```

---

## Relationships

### User → Tasks (One-to-Many)

**Relationship Type**: One user owns many tasks

**Cardinality**: 1:N (one user to many tasks)

**Foreign Key**: `tasks.user_id → users.id`

**Cascade Behavior**: `ON DELETE CASCADE` - When a user is deleted, all their tasks are automatically deleted

**Access Pattern**:
- Retrieve all tasks for a user: `SELECT * FROM tasks WHERE user_id = ?`
- Retrieve filtered tasks: `SELECT * FROM tasks WHERE user_id = ? AND completed = ?`

**SQLModel Relationship**:
```python
# User side
class User(SQLModel, table=True):
    tasks: list["Task"] = Relationship(back_populates="user")

# Task side
class Task(SQLModel, table=True):
    user: User = Relationship(back_populates="tasks")
```

**Usage Example**:
```python
# Get all tasks for a user (ORM)
user = session.get(User, user_id)
tasks = user.tasks  # Lazy-loaded relationship

# Get all tasks for a user (explicit query - preferred)
tasks = session.exec(
    select(Task).where(Task.user_id == user_id)
).all()
```

---

## Validation Rules

### Task Title Validation

| Rule | Constraint | Error Message |
|------|------------|---------------|
| Required | NOT NULL | "Title is required" |
| Minimum Length | >= 1 character | "Title must be at least 1 character" |
| Maximum Length | <= 200 characters | "Title must be 200 characters or less" |
| Whitespace | Trimmed before validation | "Title cannot be empty after trimming whitespace" |

**Pydantic Schema**:
```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
```

### Task Description Validation

| Rule | Constraint | Error Message |
|------|------------|---------------|
| Optional | NULLABLE | (No error if omitted) |
| Maximum Length | <= 1000 characters | "Description must be 1000 characters or less" |

**Pydantic Schema**:
```python
from pydantic import BaseModel, Field
from typing import Optional

class TaskCreate(BaseModel):
    description: Optional[str] = Field(default=None, max_length=1000)
```

### Task Completed Validation

| Rule | Constraint | Error Message |
|------|------------|---------------|
| Type | Boolean only | "Completed must be true or false" |
| Default | FALSE | (Automatically set on creation) |

### User ID Validation

| Rule | Constraint | Error Message |
|------|------------|---------------|
| Required | NOT NULL | "User ID is required" |
| Foreign Key | Must exist in users table | "Invalid user ID" |
| Match Token | Must match JWT sub claim | "Access denied: Cannot access other users' data" |

---

## State Transitions

### Task Lifecycle

```
┌─────────────┐
│  [Created]  │
│ completed = │
│   FALSE     │
└──────┬──────┘
       │
       │ User action: Toggle completion
       │
       ▼
┌─────────────┐
│ [Completed] │
│ completed = │
│    TRUE     │
└──────┬──────┘
       │
       │ User action: Toggle completion (again)
       │
       ▼
┌─────────────┐
│  [Created]  │  ◄── Can toggle back
│ completed = │
│   FALSE     │
└──────┬──────┘
       │
       │ User action: Delete
       │
       ▼
┌─────────────┐
│  [Deleted]  │  (Permanent)
└─────────────┘
```

**State Transitions**:
1. **Creation**: Task starts with `completed = FALSE`
2. **Toggle Completion**: User can flip `completed` between TRUE and FALSE any number of times
3. **Deletion**: Task is permanently removed from database (no soft delete)

**No Invalid States**:
- Task cannot exist without a user_id (foreign key constraint)
- Task cannot have empty title (validation constraint)
- Task completed status is always boolean (type constraint)

---

## Query Patterns

### Common Queries

**1. Get all tasks for a user**:
```sql
SELECT * FROM tasks
WHERE user_id = $1
ORDER BY created_at DESC;
```
Performance: O(log n) with `idx_tasks_user_id` index

**2. Get pending tasks for a user**:
```sql
SELECT * FROM tasks
WHERE user_id = $1 AND completed = FALSE
ORDER BY created_at DESC;
```
Performance: O(log n) with `idx_tasks_user_completed` composite index

**3. Get completed tasks for a user**:
```sql
SELECT * FROM tasks
WHERE user_id = $1 AND completed = TRUE
ORDER BY created_at DESC;
```
Performance: O(log n) with `idx_tasks_user_completed` composite index

**4. Get specific task for a user**:
```sql
SELECT * FROM tasks
WHERE id = $1 AND user_id = $2;
```
Performance: O(1) with primary key index, then O(1) verification of user_id

**5. Count user's tasks**:
```sql
SELECT COUNT(*) FROM tasks
WHERE user_id = $1;
```
Performance: O(n) but fast with index (database can count using index only)

### SQLModel Query Examples

```python
from sqlmodel import Session, select

# Get all tasks for user
statement = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
tasks = session.exec(statement).all()

# Get pending tasks
statement = (
    select(Task)
    .where(Task.user_id == user_id)
    .where(Task.completed == False)
    .order_by(Task.created_at.desc())
)
pending_tasks = session.exec(statement).all()

# Get specific task
task = session.get(Task, task_id)
if task and task.user_id == user_id:
    # Task belongs to user
    pass
else:
    # Task not found or doesn't belong to user
    raise HTTPException(status_code=404, detail="Task not found")
```

---

## Data Constraints Summary

| Constraint Type | Entity | Field | Rule |
|----------------|--------|-------|------|
| Primary Key | Task | id | Auto-increment, unique |
| Foreign Key | Task | user_id | References users.id, CASCADE on delete |
| Not Null | Task | user_id, title, completed, created_at, updated_at | Must have value |
| Unique | User | email | No duplicate emails |
| Length | Task | title | 1-200 characters |
| Length | Task | description | 0-1000 characters (if provided) |
| Default | Task | completed | FALSE |
| Index | Task | user_id | B-tree index |
| Index | Task | completed | B-tree index |
| Composite Index | Task | (user_id, completed) | B-tree index |

---

## Scalability Considerations

### Current Design (Phase 1)

**Supports**:
- 100+ concurrent users
- 1000+ tasks per user
- <1s query time for task lists

**Limitations**:
- No pagination (returns all tasks)
- No soft delete (permanent deletion only)
- No task history/audit trail

### Future Enhancements (Out of Scope for Initial Version)

**If scale increases** (1000+ concurrent users, 10,000+ tasks per user):
1. **Add Pagination**: Limit/offset or cursor-based pagination
   ```sql
   SELECT * FROM tasks
   WHERE user_id = $1
   ORDER BY created_at DESC
   LIMIT 50 OFFSET 0;
   ```

2. **Add Soft Delete**: Keep deleted tasks for recovery/audit
   ```sql
   ALTER TABLE tasks ADD COLUMN deleted_at TIMESTAMP NULL;
   CREATE INDEX idx_tasks_deleted ON tasks(deleted_at);
   ```

3. **Add Full-Text Search**: Search tasks by title/description
   ```sql
   ALTER TABLE tasks ADD COLUMN search_vector tsvector;
   CREATE INDEX idx_tasks_search ON tasks USING gin(search_vector);
   ```

4. **Add Partitioning**: Partition tasks table by user_id for very large datasets

---

## Summary

The data model is simple and focused:
- **2 entities**: User (external) and Task (managed by this API)
- **1 relationship**: User owns many Tasks (1:N)
- **Strict validation**: All constraints enforced at database and application level
- **User isolation**: Every query filtered by user_id for security
- **Performance**: Indexes on all frequently queried columns
- **Scalability**: Design supports 100+ concurrent users with room to grow

This model satisfies all functional requirements from the specification while maintaining simplicity and performance.
