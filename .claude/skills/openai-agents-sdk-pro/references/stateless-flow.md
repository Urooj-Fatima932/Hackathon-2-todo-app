# Stateless Conversation Flow

## Overview

Server holds NO state between requests. Each request:
1. Fetches history from DB
2. Processes with agent
3. Stores results to DB
4. Returns response

```
Request → Fetch History → Run Agent → Store → Response → (Server stateless)
```

## Complete Flow Implementation

```python
# app/services/chat_service.py
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message
from app.repositories.message_repository import MessageRepository

class ChatService:
    def __init__(self, db: AsyncSession, mcp_url: str):
        self.db = db
        self.mcp_url = mcp_url
        self.message_repo = MessageRepository(db)

    async def process_message(
        self,
        conversation_id: str,
        user_message: str,
    ) -> str:
        """
        Stateless request cycle:
        1. Fetch history
        2. Build messages
        3. Store user message
        4. Run agent
        5. Store assistant response
        6. Return (server holds no state)
        """

        # 1. Fetch conversation history from database
        history = await self.message_repo.get_history(conversation_id)

        # 2. Build message array for agent
        messages = self._build_message_array(history, user_message)

        # 3. Store user message in database
        await self.message_repo.create(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
        )

        # 4-5. Run agent with MCP tools
        async with MCPServerStreamableHttp(
            name="App MCP",
            params={"url": self.mcp_url},
            cache_tools_list=True,
        ) as mcp_server:
            agent = Agent(
                name="Assistant",
                instructions=self._get_instructions(),
                mcp_servers=[mcp_server],
            )

            # 6. Agent invokes appropriate MCP tool(s)
            result = await Runner.run(agent, messages)

        assistant_response = result.final_output

        # 7. Store assistant response in database
        await self.message_repo.create(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_response,
        )

        # 8. Return response to client
        # 9. Server holds NO state (ready for next request)
        return assistant_response

    def _build_message_array(
        self,
        history: list[Message],
        new_message: str,
    ) -> list[dict]:
        """Build OpenAI-format message array."""
        messages = []

        # Add history
        for msg in history:
            messages.append({
                "role": msg.role,
                "content": msg.content,
            })

        # Add new user message
        messages.append({
            "role": "user",
            "content": new_message,
        })

        return messages

    def _get_instructions(self) -> str:
        return """You are a helpful assistant that can manage notes.

Available actions:
- Create notes
- List notes
- Delete notes

Always confirm destructive actions before proceeding."""
```

## Database Models

```python
# app/models/message.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from app.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(String(255), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )
```

```python
# app/models/note.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## Repository Layer

```python
# app/repositories/message_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message

class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_history(
        self,
        conversation_id: str,
        limit: int = 50,
    ) -> list[Message]:
        """Fetch conversation history ordered by time."""
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> Message:
        """Store a message."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def clear_conversation(self, conversation_id: str) -> None:
        """Delete all messages in a conversation."""
        await self.db.execute(
            Message.__table__.delete().where(
                Message.conversation_id == conversation_id
            )
        )
        await self.db.commit()
```

## MCP Server (Note Tools)

```python
# app/mcp/server.py
from mcp.server.fastmcp import FastMCP
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_factory
from app.repositories.note_repository import NoteRepository

mcp = FastMCP("Notes MCP Server")

async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        yield session

@mcp.tool()
async def create_note(title: str, content: str) -> str:
    """Create a new note.

    Args:
        title: The note title.
        content: The note content.
    """
    async with async_session_factory() as db:
        repo = NoteRepository(db)
        note = await repo.create(title=title, content=content)
        return f"Created note '{note.title}' with ID {note.id}"

@mcp.tool()
async def list_notes() -> str:
    """List all notes."""
    async with async_session_factory() as db:
        repo = NoteRepository(db)
        notes = await repo.list()
        if not notes:
            return "No notes found."
        return "\n".join(f"- [{n.id}] {n.title}" for n in notes)

@mcp.tool()
async def get_note(note_id: int) -> str:
    """Get a note by ID.

    Args:
        note_id: The ID of the note to retrieve.
    """
    async with async_session_factory() as db:
        repo = NoteRepository(db)
        note = await repo.get(note_id)
        if not note:
            return f"Note {note_id} not found."
        return f"**{note.title}**\n\n{note.content}"

@mcp.tool()
async def delete_note(note_id: int) -> str:
    """Delete a note by ID.

    Args:
        note_id: The ID of the note to delete.
    """
    async with async_session_factory() as db:
        repo = NoteRepository(db)
        note = await repo.get(note_id)
        if not note:
            return f"Note {note_id} not found."
        await repo.delete(note_id)
        return f"Deleted note '{note.title}' (ID: {note_id})"
```

## FastAPI Router

```python
# app/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.chat_service import ChatService
from app.config import settings

router = APIRouter()

class ChatRequest(BaseModel):
    conversation_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Stateless chat endpoint.
    Each request fetches history, processes, stores, returns.
    Server holds no state between requests.
    """
    service = ChatService(db, mcp_url=settings.mcp_url)

    try:
        response = await service.process_message(
            conversation_id=request.conversation_id,
            user_message=request.message,
        )
        return ChatResponse(
            response=response,
            conversation_id=request.conversation_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Main Application

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import engine, Base
from app.routers import chat
from app.mcp.server import mcp

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup
    await engine.dispose()

app = FastAPI(title="Notes Chatbot", lifespan=lifespan)

# Mount MCP server
app.mount("/mcp", mcp.get_app())

# Include chat router
app.include_router(chat.router, prefix="/api")
```

## Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://user:pass@localhost/notes"
    mcp_url: str = "http://localhost:8000/mcp"
    openai_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()
```

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

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    STATELESS REQUEST CYCLE                   │
└─────────────────────────────────────────────────────────────┘

  Client                    Server                    Database
    │                         │                          │
    │  1. POST /chat          │                          │
    │  {conversation_id,      │                          │
    │   message}              │                          │
    │ ───────────────────────>│                          │
    │                         │                          │
    │                         │  2. Fetch history        │
    │                         │ ─────────────────────────>
    │                         │                          │
    │                         │  3. Build messages       │
    │                         │  (history + new)         │
    │                         │                          │
    │                         │  4. Store user message   │
    │                         │ ─────────────────────────>
    │                         │                          │
    │                         │  5. Run agent            │
    │                         │  ┌─────────────────┐     │
    │                         │  │ Agent + MCP     │     │
    │                         │  │                 │     │
    │                         │  │ 6. Tool calls   │─────│───> DB
    │                         │  │    (CRUD ops)   │<────│────
    │                         │  └─────────────────┘     │
    │                         │                          │
    │                         │  7. Store assistant msg  │
    │                         │ ─────────────────────────>
    │                         │                          │
    │  8. Return response     │                          │
    │ <───────────────────────│                          │
    │                         │                          │
    │                         │  9. Server stateless     │
    │                         │  (no memory of request)  │
    │                         │                          │
```

## Key Points

1. **No in-memory state**: Server doesn't store conversations
2. **DB is source of truth**: All history lives in database
3. **Each request is independent**: Fetch → Process → Store → Return
4. **Scalable**: Any server instance can handle any request
5. **MCP tools handle business logic**: Agent delegates to MCP for CRUD
