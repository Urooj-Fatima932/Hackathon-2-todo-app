# Research: Agentic Task Management Chatbot

**Feature Branch**: `001-agentic-chatbot`
**Created**: 2026-02-09

## Research Questions

1. How to integrate OpenAI Agents SDK for stateless task management?
2. How to design MCP-style function tools for CRUD operations?
3. How to implement a persistent floating chat widget in Next.js?

---

## 1. OpenAI Agents SDK Integration

### Question
How to configure a stateless agent with function tools that can handle task management operations?

### Findings

**Package**: `openai-agents` (official OpenAI Agents SDK)

**Key Features**:
- Built-in function tool support via `@function_tool` decorator
- Automatic tool dispatch and result handling
- Support for conversation history injection
- Pydantic integration for tool schemas

**Stateless Pattern**:
The SDK supports stateless operation by accepting a `messages` parameter containing conversation history. On each request:
1. Load last N messages from database
2. Pass messages to agent runner
3. Agent processes input with full context
4. Store new messages to database

**Code Pattern**:
```python
from agents import Agent, Runner, function_tool
from pydantic import BaseModel

# Define tools with Pydantic schemas
class AddTaskInput(BaseModel):
    title: str
    description: str | None = None

@function_tool
def add_task(input: AddTaskInput) -> dict:
    """Add a new task to the user's list."""
    # Implementation here
    return {"task_id": "...", "status": "created"}

# Configure agent
agent = Agent(
    name="TaskBot",
    instructions="""You are a helpful task management assistant.
    You help users manage their tasks through natural conversation.
    When users want to create, view, update, or delete tasks, use the available tools.
    Always confirm actions and be conversational.""",
    tools=[add_task, list_tasks, get_task, update_task, complete_task, delete_task]
)

# Stateless execution with history
async def process_message(user_message: str, history: list[dict]) -> str:
    result = await Runner.run(
        agent,
        messages=history,  # Previous conversation
        input=user_message  # Current user input
    )
    return result.final_output
```

**Decision**: Use `openai-agents` SDK with synchronous function tools

**Rationale**:
- Clean abstraction over OpenAI's function calling
- Native Pydantic support matches existing codebase
- Well-documented, production-ready

**Alternatives Rejected**:
- Raw OpenAI API: Requires manual tool dispatch logic
- LangChain: Heavier dependency, unnecessary abstractions

---

## 2. MCP-Style Function Tools

### Question
How to design function tools that perform CRUD operations on tasks while maintaining user isolation?

### Findings

**Tool Design Principles**:
1. Each tool has a single responsibility
2. Tools receive user context (user_id) from the agent context
3. Tools return structured results for the agent to interpret
4. Tools validate inputs before database operations

**Tool Inventory**:

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `add_task` | Create new task | title, description? | task_id, title, status |
| `list_tasks` | Get user's tasks | status_filter? | tasks[], count |
| `get_task` | Get single task | task_id | task details |
| `update_task` | Modify task | task_id, title?, description? | updated task |
| `complete_task` | Mark as done | task_id | task_id, status |
| `delete_task` | Remove task | task_id | task_id, status |

**User Context Injection**:
```python
from agents import RunContext

@function_tool
def add_task(input: AddTaskInput, context: RunContext) -> dict:
    user_id = context.context["user_id"]  # Injected by caller
    # Create task for this user only
```

**Error Handling Pattern**:
```python
@function_tool
def get_task(input: GetTaskInput, context: RunContext) -> dict:
    user_id = context.context["user_id"]
    task = db.get_task(input.task_id)

    if not task:
        return {"error": "Task not found", "task_id": input.task_id}

    if task.user_id != user_id:
        return {"error": "Task not found", "task_id": input.task_id}  # Same error for security

    return {"task_id": task.id, "title": task.title, ...}
```

**Decision**: Define tools as decorated Python functions with Pydantic schemas

**Rationale**:
- Type safety and validation built-in
- Consistent with FastAPI patterns in codebase
- Auto-generates JSON schema for OpenAI

---

## 3. Floating Chat Widget

### Question
How to implement a persistent chat widget that maintains state across page navigation in Next.js?

### Findings

**Challenge**: Next.js App Router re-renders layouts on navigation, potentially losing widget state.

**Solution**: React Context + Client Component + Portal

**Architecture**:
```
RootLayout (server component)
└── ChatProvider (client component wrapper)
    ├── {children} (page content)
    └── ChatWidget (client component, portal to body)
```

**State Management**:
- Widget open/closed state
- Current conversation ID
- Messages for current conversation
- Conversation list

**React Context Pattern**:
```tsx
'use client';

import { createContext, useContext, useState, ReactNode } from 'react';
import { createPortal } from 'react-dom';

interface ChatContextType {
  isOpen: boolean;
  toggleChat: () => void;
  conversationId: string | null;
  setConversationId: (id: string | null) => void;
  // ... other state
}

const ChatContext = createContext<ChatContextType | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const value = {
    isOpen,
    toggleChat: () => setIsOpen(prev => !prev),
    conversationId,
    setConversationId,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
      {typeof window !== 'undefined' && createPortal(
        <ChatWidget />,
        document.body
      )}
    </ChatContext.Provider>
  );
}
```

**UI Library**: @chatscope/chat-ui-kit-react

**Benefits**:
- Pre-built, accessible chat components
- Styling customization via CSS variables
- Message bubbles, typing indicators, conversation list
- MIT licensed

**Decision**: Use React Context + Portal for persistent widget with @chatscope/chat-ui-kit-react

**Rationale**:
- Context preserves state across Next.js navigation
- Portal ensures widget renders above all content
- Chat UI kit reduces custom component work

**Alternatives Rejected**:
- Zustand/Redux: Overkill for single widget state
- iframe: Poor integration, styling limitations
- Full custom build: More effort, accessibility concerns

---

## Dependencies

### Backend (Python)
```
openai-agents>=0.1.0
```

### Frontend (NPM)
```
@chatscope/chat-ui-kit-react@^2.0.0
@chatscope/chat-ui-kit-styles@^1.4.0
```

### Environment
```
OPENAI_API_KEY=sk-...
```

---

## Outstanding Questions

None - all research questions resolved.

---

## References

- [OpenAI Agents SDK Documentation](https://github.com/openai/openai-agents-python)
- [@chatscope/chat-ui-kit-react](https://chatscope.io/docs/getting-started/)
- [Next.js App Router Client Components](https://nextjs.org/docs/app/building-your-application/rendering/client-components)
