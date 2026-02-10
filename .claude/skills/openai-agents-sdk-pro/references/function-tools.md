# Function Tools

## Overview

Function tools allow Python functions to be exposed as callable tools for agents. The SDK automatically generates JSON schemas from function signatures and docstrings.

## The @function_tool Decorator

```python
from agents import function_tool

@function_tool
async def fetch_weather(location: str) -> str:
    """Fetch the weather for a given location.

    Args:
        location: The city name to get weather for.

    Returns:
        Weather description string.
    """
    return f"Weather in {location}: sunny"
```

### Key Features

- **Async/sync support**: Both function types work
- **Docstring parsing**: Extracts descriptions for tool and arguments (Google, Sphinx, NumPy formats)
- **Type annotations**: Required for schema generation
- **Pydantic models**: Supported for complex input types

### Name Override

```python
@function_tool(name_override="get_weather")
async def fetch_weather(location: str) -> str:
    """Fetch weather."""
    return "sunny"
```

## Pydantic Input Models

For complex inputs, use Pydantic models:

```python
from pydantic import BaseModel, Field
from agents import function_tool

class NoteInput(BaseModel):
    title: str = Field(description="The note title")
    content: str = Field(description="The note content")
    tags: list[str] = Field(default=[], description="Optional tags")

@function_tool
async def create_note(note: NoteInput) -> str:
    """Create a new note.

    Args:
        note: The note data to create.
    """
    # note.title, note.content, note.tags available
    return f"Created note: {note.title}"
```

## Context Access

Tools can access run context:

```python
from agents import function_tool, RunContextWrapper

@function_tool
async def get_user_notes(ctx: RunContextWrapper, limit: int = 10) -> str:
    """Get notes for current user.

    Args:
        ctx: Run context (injected automatically).
        limit: Maximum notes to return.
    """
    user_id = ctx.context.user_id  # Access context data
    return f"Found {limit} notes for user {user_id}"
```

## Return Types

### Text Output (default)

```python
@function_tool
async def search(query: str) -> str:
    return f"Results for: {query}"
```

### Structured Output

```python
from agents import ToolOutputText, ToolOutputImage

@function_tool
async def generate_report(topic: str) -> ToolOutputText:
    return ToolOutputText(text=f"Report on {topic}")
```

## Error Handling

### Default Behavior

Exceptions are caught and reported to the LLM:

```python
@function_tool
async def risky_operation(data: str) -> str:
    raise ValueError("Invalid data")
    # LLM receives error message, can retry or inform user
```

### Custom Error Handler

```python
def custom_error_handler(ctx, error: Exception) -> str:
    return f"Operation failed: {str(error)}. Please try again."

@function_tool(failure_error_function=custom_error_handler)
async def risky_operation(data: str) -> str:
    raise ValueError("Invalid data")
```

### Manual Error Handling

```python
@function_tool(failure_error_function=None)
async def critical_operation(data: str) -> str:
    # Exceptions will propagate up
    raise ValueError("Critical error")
```

## Custom FunctionTool

For advanced scenarios:

```python
from agents import FunctionTool
from pydantic import BaseModel

class SearchParams(BaseModel):
    query: str
    limit: int = 10

async def search_handler(ctx, args_json: str) -> str:
    import json
    args = json.loads(args_json)
    return f"Found {args['limit']} results for {args['query']}"

search_tool = FunctionTool(
    name="search",
    description="Search for items",
    params_json_schema=SearchParams.model_json_schema(),
    on_invoke_tool=search_handler,
)
```

## CRUD Tool Examples

### Create

```python
@function_tool
async def create_note(title: str, content: str) -> str:
    """Create a new note.

    Args:
        title: The note title.
        content: The note content.
    """
    # Call your service/repository
    note = await note_service.create(title=title, content=content)
    return f"Created note '{note.title}' with ID {note.id}"
```

### Read

```python
@function_tool
async def get_note(note_id: int) -> str:
    """Get a note by ID.

    Args:
        note_id: The note ID to retrieve.
    """
    note = await note_service.get(note_id)
    if not note:
        return f"Note {note_id} not found"
    return f"Note: {note.title}\n\n{note.content}"
```

### Update

```python
@function_tool
async def update_note(note_id: int, title: str | None = None, content: str | None = None) -> str:
    """Update an existing note.

    Args:
        note_id: The note ID to update.
        title: New title (optional).
        content: New content (optional).
    """
    note = await note_service.update(note_id, title=title, content=content)
    return f"Updated note {note_id}"
```

### Delete

```python
@function_tool
async def delete_note(note_id: int) -> str:
    """Delete a note.

    Args:
        note_id: The note ID to delete.
    """
    await note_service.delete(note_id)
    return f"Deleted note {note_id}"
```

### List

```python
@function_tool
async def list_notes(limit: int = 10, offset: int = 0) -> str:
    """List all notes.

    Args:
        limit: Maximum notes to return.
        offset: Number of notes to skip.
    """
    notes = await note_service.list(limit=limit, offset=offset)
    if not notes:
        return "No notes found"
    return "\n".join(f"- [{n.id}] {n.title}" for n in notes)
```

## Best Practices

1. **Clear docstrings**: The LLM uses these to understand when/how to use tools
2. **Typed parameters**: Always use type annotations
3. **Descriptive returns**: Return human-readable strings the LLM can relay to users
4. **Handle errors gracefully**: Return error messages, don't crash
5. **Limit side effects**: Make it clear when tools modify data
6. **Use Pydantic for complex inputs**: Better validation and schema generation
