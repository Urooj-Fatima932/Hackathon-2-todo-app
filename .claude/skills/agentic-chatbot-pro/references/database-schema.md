# Database Schema

## Two Required Tables

Every agentic chatbot needs:
1. **Messages** - Conversation history
2. **{Entity}** - Domain data (tasks, notes, etc.)

---

## Messages Table

Stores conversation history for stateless retrieval.

```python
# app/models/message.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from app.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_messages_user_created", "user_id", "created_at"),
    )
```

### Message Repository

```python
# app/repositories/message_repo.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message

class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_history(
        self,
        user_id: str,
        limit: int = 50,
    ) -> list[Message]:
        """Fetch conversation history ordered by time."""
        query = (
            select(Message)
            .where(Message.user_id == user_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(
        self,
        user_id: str,
        role: str,
        content: str,
    ) -> Message:
        """Store a message."""
        message = Message(
            user_id=user_id,
            role=role,
            content=content,
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def clear(self, user_id: str) -> None:
        """Delete all messages for a user."""
        from sqlalchemy import delete
        await self.db.execute(
            delete(Message).where(Message.user_id == user_id)
        )
        await self.db.commit()
```

---

## Entity Table (Example: Task)

Replace with your domain entity.

```python
# app/models/task.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Index
from app.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_tasks_user_completed", "user_id", "completed"),
    )
```

### Entity Repository (Example: Task)

```python
# app/repositories/task_repo.py
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task

class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: str,
        title: str,
        description: str = "",
    ) -> Task:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
        )
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get(self, user_id: str, task_id: int) -> Task | None:
        query = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list(
        self,
        user_id: str,
        status: str = "all",
    ) -> list[Task]:
        query = select(Task).where(Task.user_id == user_id)

        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)

        query = query.order_by(Task.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        task_id: int,
        title: str = None,
        description: str = None,
    ) -> Task:
        task = await self.db.get(Task, task_id)
        if title:
            task.title = title
        if description is not None:
            task.description = description
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def complete(self, task_id: int) -> Task:
        task = await self.db.get(Task, task_id)
        task.completed = True
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete(self, task_id: int) -> None:
        await self.db.execute(
            delete(Task).where(Task.id == task_id)
        )
        await self.db.commit()
```

---

## Database Setup

```python
# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with async_session_factory() as session:
        yield session
```

---

## Alembic Migration

```python
# alembic/versions/001_initial.py
"""Initial migration

Revision ID: 001
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_messages_user_id', 'messages', ['user_id'])
    op.create_index('ix_messages_user_created', 'messages', ['user_id', 'created_at'])

    # Tasks table (replace with your entity)
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), default=''),
        sa.Column('completed', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('ix_tasks_user_completed', 'tasks', ['user_id', 'completed'])

def downgrade():
    op.drop_table('tasks')
    op.drop_table('messages')
```

---

## Key Points

1. **user_id in both tables** - Multi-tenancy support
2. **Indexes on user_id** - Fast lookups per user
3. **Composite indexes** - user_id + created_at for history queries
4. **Soft vs hard delete** - Consider adding `deleted_at` for soft deletes
5. **Timestamps** - Always track created_at and updated_at
