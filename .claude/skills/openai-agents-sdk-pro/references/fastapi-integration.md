# FastAPI Integration

## Basic Chat Endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents import Agent, Runner
from agents.sessions import SQLiteSession

app = FastAPI()

# Define agent
notes_agent = Agent(
    name="NotesAgent",
    instructions="Help users manage notes.",
    tools=[create_note, list_notes, delete_note],
)

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session = SQLiteSession(request.user_id, "conversations.db")

    try:
        result = await Runner.run(
            notes_agent,
            request.message,
            session=session,
        )
        return ChatResponse(response=result.final_output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Streaming Response

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from agents import Agent, Runner
import json

app = FastAPI()
agent = Agent(name="NotesAgent", instructions="...")

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        session = SQLiteSession(request.user_id, "conversations.db")

        result = Runner.run_streamed(
            agent,
            request.message,
            session=session,
        )

        async for event in result.stream_events():
            if hasattr(event, 'delta') and event.delta:
                yield f"data: {json.dumps({'delta': event.delta})}\n\n"

        # Final response
        await result.wait()
        yield f"data: {json.dumps({'done': True, 'final': result.final_output})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )
```

## With User Context

```python
from fastapi import FastAPI, Depends, Header, HTTPException
from dataclasses import dataclass
from agents import Agent, Runner, RunContextWrapper, function_tool
from agents.sessions import SQLAlchemySession

app = FastAPI()

@dataclass
class UserContext:
    user_id: str
    user_name: str

# Tool with context
@function_tool
async def list_notes(ctx: RunContextWrapper[UserContext]) -> str:
    """List notes for current user."""
    user_id = ctx.context.user_id
    notes = await note_service.list_for_user(user_id)
    return "\n".join(f"- {n.title}" for n in notes)

agent = Agent(
    name="NotesAgent",
    instructions=lambda ctx, _: f"Help {ctx.context.user_name} manage notes.",
    tools=[list_notes],
)

async def get_current_user(authorization: str = Header(...)) -> UserContext:
    # Validate token, get user
    user = await auth_service.validate(authorization)
    if not user:
        raise HTTPException(401, "Invalid token")
    return UserContext(user_id=user.id, user_name=user.name)

@app.post("/chat")
async def chat(
    request: ChatRequest,
    user: UserContext = Depends(get_current_user),
):
    session = SQLAlchemySession(user.user_id, engine)

    result = await Runner.run(
        agent,
        request.message,
        context=user,
        session=session,
    )
    return {"response": result.final_output}
```

## With MCP Server

```python
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

app = FastAPI()

# Create MCP server
mcp = FastMCP("Notes MCP")

@mcp.tool()
async def create_note(title: str, content: str) -> str:
    """Create a note."""
    note = await note_service.create(title, content)
    return f"Created: {note.title}"

@mcp.tool()
async def list_notes() -> str:
    """List all notes."""
    notes = await note_service.list()
    return "\n".join(f"- {n.title}" for n in notes)

# Mount MCP
app.mount("/mcp", mcp.get_app())

# Chat endpoint using MCP
@app.post("/chat")
async def chat(request: ChatRequest):
    async with MCPServerStreamableHttp(
        name="Notes MCP",
        params={"url": "http://localhost:8000/mcp"},
    ) as server:
        agent = Agent(
            name="NotesAgent",
            instructions="Help with notes using available tools.",
            mcp_servers=[server],
        )

        result = await Runner.run(agent, request.message)
        return {"response": result.final_output}
```

## Complete Application Structure

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.routers import chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.engine = create_async_engine(settings.database_url)
    app.state.session_factory = sessionmaker(
        app.state.engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield
    # Shutdown
    await app.state.engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(chat.router, prefix="/api")
```

```python
# app/routers/chat.py
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from agents import Agent, Runner
from agents.sessions import SQLAlchemySession

from app.agents.notes_agent import notes_agent
from app.dependencies import get_db_session

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@router.post("/chat")
async def chat(
    request: ChatRequest,
    req: Request,
):
    session = SQLAlchemySession(
        session_id=request.user_id,
        engine=req.app.state.engine,
    )

    result = await Runner.run(
        notes_agent,
        request.message,
        session=session,
    )

    return {"response": result.final_output}
```

```python
# app/agents/notes_agent.py
from agents import Agent
from app.tools.note_tools import create_note, list_notes, delete_note

notes_agent = Agent(
    name="NotesAgent",
    instructions="""You are a helpful notes assistant.

You can:
- Create new notes
- List existing notes
- Delete notes (confirm first)

Be friendly and confirm destructive actions.""",
    tools=[create_note, list_notes, delete_note],
)
```

```python
# app/tools/note_tools.py
from agents import function_tool
from app.services.note_service import NoteService

# Service instance (or use dependency injection)
note_service = NoteService()

@function_tool
async def create_note(title: str, content: str) -> str:
    """Create a new note.

    Args:
        title: The note title.
        content: The note content.
    """
    note = await note_service.create(title=title, content=content)
    return f"Created note '{note.title}' with ID {note.id}"

@function_tool
async def list_notes() -> str:
    """List all notes."""
    notes = await note_service.list()
    if not notes:
        return "No notes found."
    return "\n".join(f"- [{n.id}] {n.title}" for n in notes)

@function_tool
async def delete_note(note_id: int) -> str:
    """Delete a note by ID.

    Args:
        note_id: The ID of the note to delete.
    """
    await note_service.delete(note_id)
    return f"Deleted note {note_id}"
```

## Error Handling

```python
from fastapi import HTTPException
from agents import InputGuardrailTripwireTriggered

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        result = await Runner.run(agent, request.message, session=session)
        return {"response": result.final_output}

    except InputGuardrailTripwireTriggered as e:
        raise HTTPException(400, f"Request blocked: {e.guardrail_result.output_info}")

    except Exception as e:
        # Log error
        logger.error(f"Chat error: {e}")
        raise HTTPException(500, "An error occurred processing your request")
```

## Best Practices

1. **Use async everywhere**: FastAPI + async agents = good performance
2. **Session per request**: Create session in endpoint, not globally
3. **Shared engine**: Reuse database engine across requests
4. **Error handling**: Catch guardrail exceptions specifically
5. **Streaming for long responses**: Better UX for slow operations
6. **Context injection**: Pass user info via RunContext, not agent input
