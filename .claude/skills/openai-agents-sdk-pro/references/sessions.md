# Sessions

## Overview

Sessions manage conversation history automatically, eliminating manual message tracking.

## Session Types

| Type | Storage | Use Case |
|------|---------|----------|
| `SQLiteSession` | SQLite file/memory | Development, simple apps |
| `SQLAlchemySession` | PostgreSQL, MySQL, etc. | Production |
| `AdvancedSQLiteSession` | SQLite with extras | Analytics, branching |
| `EncryptedSession` | Wrapper + encryption | Sensitive data |

## Basic SQLite Session

```python
from agents import Agent, Runner
from agents.sessions import SQLiteSession

agent = Agent(name="NotesAgent", instructions="Help with notes.")

# In-memory (lost on restart)
session = SQLiteSession("user_123")

# File-based (persistent)
session = SQLiteSession("user_123", "conversations.db")

# Run with session
result = await Runner.run(agent, "Create a note", session=session)

# Continue conversation (history preserved)
result = await Runner.run(agent, "Now list my notes", session=session)
```

## SQLAlchemy Session (Production)

```python
from agents.sessions import SQLAlchemySession

# From URL
session = SQLAlchemySession(
    session_id="user_123",
    db_url="postgresql+asyncpg://user:pass@host/db",
    create_tables=True,
)

# From existing engine
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("postgresql+asyncpg://...")
session = SQLAlchemySession(
    session_id="user_123",
    engine=engine,
)
```

## Session Per User

```python
from agents import Agent, Runner
from agents.sessions import SQLiteSession

agent = Agent(name="NotesAgent", instructions="...")

async def chat(user_id: str, message: str) -> str:
    # Each user gets own session
    session = SQLiteSession(user_id, "conversations.db")
    result = await Runner.run(agent, message, session=session)
    return result.final_output
```

## Session Operations

```python
# Get conversation history
items = await session.get_items()

# Add items manually
await session.add_items([{"role": "user", "content": "Hello"}])

# Remove last item (for corrections)
removed = await session.pop_item()

# Clear entire session
await session.clear_session()
```

## Advanced SQLite Session

Features: branching, usage analytics, structured queries.

```python
from agents.sessions import AdvancedSQLiteSession

session = AdvancedSQLiteSession(
    session_id="user_123",
    db_path="conversations.db",
)

# Tracks token usage automatically
result = await Runner.run(agent, "Hello", session=session)

# Query usage stats
stats = await session.get_usage_stats()
```

## Encrypted Session

Wrap any session with encryption:

```python
from agents.sessions import EncryptedSession, SQLiteSession

base_session = SQLiteSession("user_123", "conversations.db")
session = EncryptedSession(
    session=base_session,
    encryption_key="your-32-byte-key-here-for-aes256",
    ttl=3600,  # Expire after 1 hour
)
```

## Without Sessions (Manual History)

```python
from agents import Agent, Runner

agent = Agent(name="NotesAgent", instructions="...")

# First turn
result1 = await Runner.run(agent, "Create a note titled Test")

# Get history for next turn
history = result1.to_input_list()

# Continue with history
result2 = await Runner.run(agent, "Now list notes", input=history)
```

## FastAPI Integration

```python
from fastapi import FastAPI, Depends
from agents import Agent, Runner
from agents.sessions import SQLAlchemySession

app = FastAPI()

# Shared engine
engine = create_async_engine("postgresql+asyncpg://...")

agent = Agent(name="NotesAgent", instructions="...")

@app.post("/chat")
async def chat(user_id: str, message: str):
    session = SQLAlchemySession(
        session_id=user_id,
        engine=engine,
    )
    result = await Runner.run(agent, message, session=session)
    return {"response": result.final_output}
```

## Session with Context

```python
from dataclasses import dataclass
from agents import Agent, Runner
from agents.sessions import SQLiteSession

@dataclass
class UserContext:
    user_id: str
    user_name: str

agent = Agent(
    name="NotesAgent",
    instructions=lambda ctx, _: f"Help {ctx.context.user_name} with notes.",
)

async def chat(user_id: str, user_name: str, message: str):
    context = UserContext(user_id=user_id, user_name=user_name)
    session = SQLiteSession(user_id, "conversations.db")

    result = await Runner.run(
        agent,
        message,
        context=context,
        session=session,
    )
    return result.final_output
```

## Best Practices

1. **Use file-based SQLite** for development persistence
2. **Use SQLAlchemy** for production with PostgreSQL
3. **Unique session IDs** per user or conversation
4. **Handle session cleanup** for old conversations
5. **Consider encryption** for sensitive data
6. **Set TTL** if conversations should expire
