# Agent Configuration

## Basic Agent

```python
from agents import Agent

agent = Agent(
    name="NotesAgent",
    instructions="You help users manage their notes.",
    tools=[create_note, list_notes, delete_note],
)
```

## Core Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Required identifier |
| `instructions` | str \| callable | System prompt |
| `model` | str | Model to use (default: gpt-4o) |
| `tools` | list | Function tools |
| `mcp_servers` | list | MCP server connections |
| `handoffs` | list | Agents to delegate to |
| `output_type` | type | Structured output schema |
| `input_guardrails` | list | Input validation |
| `output_guardrails` | list | Output validation |

## Dynamic Instructions

```python
def get_instructions(context, agent):
    user = context.context.user
    return f"""You are a notes assistant for {user.name}.

Available actions:
- Create notes
- List notes
- Delete notes

Be helpful and confirm actions with the user."""

agent = Agent(
    name="NotesAgent",
    instructions=get_instructions,
    tools=[create_note, list_notes, delete_note],
)
```

## Model Selection

```python
agent = Agent(
    name="NotesAgent",
    model="gpt-4o",  # Default
    # model="gpt-4o-mini",  # Faster, cheaper
    # model="gpt-4-turbo",  # Older model
    instructions="...",
)
```

## Tool Choice

Control how the agent uses tools:

```python
agent = Agent(
    name="NotesAgent",
    tools=[create_note, list_notes],
    tool_choice="auto",  # LLM decides (default)
    # tool_choice="required",  # Must use a tool
    # tool_choice="none",  # Cannot use tools
    # tool_choice="create_note",  # Must use specific tool
)
```

## Structured Output

Force agent to return specific structure:

```python
from pydantic import BaseModel

class NoteResponse(BaseModel):
    success: bool
    message: str
    note_id: int | None = None

agent = Agent(
    name="NotesAgent",
    instructions="Create notes and return structured response.",
    tools=[create_note],
    output_type=NoteResponse,
)

result = await Runner.run(agent, "Create a note titled 'Test'")
response: NoteResponse = result.final_output
```

## Tool Use Behavior

Control what happens after tool execution:

```python
from agents import StopAtTools

agent = Agent(
    name="NotesAgent",
    tools=[create_note, list_notes],
    # Default: LLM processes tool results
    tool_use_behavior="run_llm_again",

    # Stop after first tool, use its output directly
    # tool_use_behavior="stop_on_first_tool",

    # Stop at specific tools
    # tool_use_behavior=StopAtTools(["list_notes"]),
)
```

## Complete Example: CRUD Agent

```python
from agents import Agent, function_tool, Runner
from pydantic import BaseModel

# Define tools
@function_tool
async def create_note(title: str, content: str) -> str:
    """Create a new note."""
    note = await note_service.create(title, content)
    return f"Created note '{title}' with ID {note.id}"

@function_tool
async def list_notes() -> str:
    """List all notes."""
    notes = await note_service.list()
    if not notes:
        return "No notes found."
    return "\n".join(f"- [{n.id}] {n.title}" for n in notes)

@function_tool
async def get_note(note_id: int) -> str:
    """Get a note by ID."""
    note = await note_service.get(note_id)
    if not note:
        return f"Note {note_id} not found."
    return f"**{note.title}**\n\n{note.content}"

@function_tool
async def delete_note(note_id: int) -> str:
    """Delete a note by ID."""
    await note_service.delete(note_id)
    return f"Deleted note {note_id}"

# Create agent
notes_agent = Agent(
    name="NotesAgent",
    instructions="""You are a helpful notes assistant.

You can help users:
- Create new notes (ask for title and content)
- List all their notes
- View a specific note
- Delete notes (confirm before deleting)

Always be helpful and confirm destructive actions.""",
    tools=[create_note, list_notes, get_note, delete_note],
    model="gpt-4o",
)

# Run agent
async def chat(message: str) -> str:
    result = await Runner.run(notes_agent, message)
    return result.final_output
```

## Agent with Context

```python
from dataclasses import dataclass
from agents import Agent, Runner, RunContextWrapper, function_tool

@dataclass
class UserContext:
    user_id: int
    user_name: str

@function_tool
async def list_notes(ctx: RunContextWrapper[UserContext]) -> str:
    """List notes for current user."""
    user_id = ctx.context.user_id
    notes = await note_service.list_for_user(user_id)
    return "\n".join(f"- {n.title}" for n in notes)

agent = Agent(
    name="NotesAgent",
    instructions=lambda ctx, agent: f"Help {ctx.context.user_name} manage notes.",
    tools=[list_notes],
)

# Run with context
context = UserContext(user_id=123, user_name="Alice")
result = await Runner.run(agent, "List my notes", context=context)
```

## Best Practices

1. **Clear instructions**: Be specific about capabilities and limitations
2. **Confirm destructive actions**: Have agent ask before deleting
3. **Use context**: Pass user info via RunContext, not instructions
4. **Choose appropriate model**: gpt-4o for complex, gpt-4o-mini for simple
5. **Structured output**: Use when you need predictable response format
