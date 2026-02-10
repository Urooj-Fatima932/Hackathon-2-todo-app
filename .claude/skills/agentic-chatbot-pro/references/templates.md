# Complete Code Templates

## Backend Structure

### main.py

```python
# backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import chat
from app.mcp.server import mcp
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="{Entity} Chatbot", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount MCP server
app.mount("/mcp", mcp.get_app())

# Include routers
app.include_router(chat.router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### config.py

```python
# backend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/chatbot"

    # MCP
    mcp_url: str = "http://localhost:8000/mcp"

    # OpenAI
    openai_api_key: str

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
```

### database.py

```python
# backend/app/database.py
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

### chat_service.py

```python
# backend/app/services/chat_service.py
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message
from app.repositories.message_repo import MessageRepository

class ChatService:
    def __init__(self, db: AsyncSession, mcp_url: str):
        self.db = db
        self.mcp_url = mcp_url
        self.message_repo = MessageRepository(db)

    async def process_message(self, user_id: str, message: str) -> str:
        """9-step stateless conversation flow."""

        # 1-2. Fetch history
        history = await self.message_repo.get_history(user_id)

        # 3. Build messages
        messages = self._build_messages(history, message)

        # 4. Store user message
        await self.message_repo.create(user_id, "user", message)

        # 5-6. Run agent with MCP
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
            result = await Runner.run(agent, messages)

        response = result.final_output

        # 7. Store assistant response
        await self.message_repo.create(user_id, "assistant", response)

        # 8-9. Return (stateless)
        return response

    def _build_messages(self, history: list[Message], new_msg: str) -> list[dict]:
        messages = [{"role": m.role, "content": m.content} for m in history]
        messages.append({"role": "user", "content": new_msg})
        return messages

    def _get_instructions(self) -> str:
        return """You are a helpful {entity} management assistant.

When user wants to:
- Add/create/remember → use add_{entity}
- Show/list/view → use list_{entities}
- Done/complete/finish → use complete_{entity}
- Delete/remove/cancel → use delete_{entity}
- Change/update/rename → use update_{entity}

Always confirm actions with a friendly response.
Handle errors gracefully."""
```

### chat.py (router)

```python
# backend/app/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.chat_service import ChatService
from app.config import settings

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    user_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    service = ChatService(db, mcp_url=settings.mcp_url)
    try:
        response = await service.process_message(
            user_id=request.user_id,
            message=request.message,
        )
        return ChatResponse(response=response, user_id=request.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### MCP server.py

```python
# backend/app/mcp/server.py
from mcp.server.fastmcp import FastMCP
from app.database import async_session_factory
from app.repositories.{entity}_repo import {Entity}Repository

mcp = FastMCP("{Entity} MCP Server")

@mcp.tool()
async def add_{entity}(user_id: str, title: str, description: str = "") -> dict:
    """Create a new {entity}.

    Args:
        user_id: The user's ID.
        title: The {entity} title.
        description: Optional description.
    """
    async with async_session_factory() as db:
        repo = {Entity}Repository(db)
        item = await repo.create(user_id, title, description)
        return {"{entity}_id": item.id, "status": "created", "title": item.title}

@mcp.tool()
async def list_{entities}(user_id: str, status: str = "all") -> list[dict]:
    """List {entities} for a user.

    Args:
        user_id: The user's ID.
        status: Filter ("all", "pending", "completed").
    """
    async with async_session_factory() as db:
        repo = {Entity}Repository(db)
        items = await repo.list(user_id, status)
        return [{"id": i.id, "title": i.title, "completed": i.completed} for i in items]

@mcp.tool()
async def complete_{entity}(user_id: str, {entity}_id: int) -> dict:
    """Mark {entity} as complete.

    Args:
        user_id: The user's ID.
        {entity}_id: The {entity} ID.
    """
    async with async_session_factory() as db:
        repo = {Entity}Repository(db)
        item = await repo.get(user_id, {entity}_id)
        if not item:
            return {"error": f"{Entity} {{{entity}_id}} not found"}
        await repo.complete({entity}_id)
        return {"{entity}_id": item.id, "status": "completed", "title": item.title}

@mcp.tool()
async def delete_{entity}(user_id: str, {entity}_id: int) -> dict:
    """Delete a {entity}.

    Args:
        user_id: The user's ID.
        {entity}_id: The {entity} ID.
    """
    async with async_session_factory() as db:
        repo = {Entity}Repository(db)
        item = await repo.get(user_id, {entity}_id)
        if not item:
            return {"error": f"{Entity} {{{entity}_id}} not found"}
        title = item.title
        await repo.delete({entity}_id)
        return {"{entity}_id": {entity}_id, "status": "deleted", "title": title}

@mcp.tool()
async def update_{entity}(
    user_id: str,
    {entity}_id: int,
    title: str = None,
    description: str = None,
) -> dict:
    """Update a {entity}.

    Args:
        user_id: The user's ID.
        {entity}_id: The {entity} ID.
        title: New title (optional).
        description: New description (optional).
    """
    async with async_session_factory() as db:
        repo = {Entity}Repository(db)
        item = await repo.get(user_id, {entity}_id)
        if not item:
            return {"error": f"{Entity} {{{entity}_id}} not found"}
        item = await repo.update({entity}_id, title=title, description=description)
        return {"{entity}_id": item.id, "status": "updated", "title": item.title}
```

---

## requirements.txt

```
fastapi>=0.109.0
uvicorn>=0.27.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
openai-agents>=0.1.0
mcp>=0.1.0
alembic>=1.13.0
python-dotenv>=1.0.0
```

---

## .env Template

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/chatbot

# OpenAI
OPENAI_API_KEY=sk-...

# MCP (internal)
MCP_URL=http://localhost:8000/mcp

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

---

## README Template

```markdown
# {Entity} Chatbot

An agentic chatbot that manages {entities} through natural language.

## Architecture

- **Frontend**: Next.js + ChatKit
- **Backend**: FastAPI + OpenAI Agents SDK
- **Tools**: MCP Server for {entity} CRUD
- **Database**: PostgreSQL

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your values
npm run dev
```

## Usage

Chat naturally:
- "Add a {entity} to buy groceries"
- "Show me all my {entities}"
- "Mark {entity} 3 as complete"
- "Delete the meeting {entity}"

## API

- `POST /api/chat` - Send message, get response
- `GET /health` - Health check
- `/mcp` - MCP server (internal)
```
