"""OpenAI Agent configuration for task management chatbot.

Following the openai-agents-sdk-pro skill and agentic-chatbot-pro stateless flow pattern.
Uses native function tools for task operations.
"""
import os
from typing import Optional
from dotenv import load_dotenv
from agents import Agent, Runner, RunConfig
from agents.extensions.models.litellm_model import LitellmModel
from sqlmodel import Session, select

from app.agent.tools import ALL_TOOLS, UserContext
from app.models import Task

load_dotenv()
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

# Configure model using LiteLLM for OpenRouter compatibility
model = LitellmModel(
    model="openrouter/nvidia/nemotron-3-nano-30b-a3b:free",
    api_key=openrouter_api_key,
)
config = RunConfig(
    model=model,
    tracing_disabled=True
)

# Agent system instructions
AGENT_INSTRUCTIONS = """You are TaskBot, a friendly and helpful task management assistant.

## Your Capabilities
You help users manage their tasks through natural conversation. You can:
- Create new tasks when users want to add, create, or remember something
- List tasks when users want to see, show, or view their tasks
- Complete tasks when users say done, finished, complete, or mark as done
- Update tasks when users want to change, rename, or modify
- Delete tasks when users want to remove, delete, or cancel

## How to Respond

### Understanding User Intent
- "Add a task to buy groceries" → Use add_task with title "Buy groceries"
- "I need to remember to call mom" → Use add_task with title "Call mom"
- "What tasks do I have?" → Use list_tasks
- "Show me pending tasks" → Use list_tasks with status="pending"
- "Mark task 5 as done" → Use complete_task with the task_id
- "Delete the groceries task" → Use delete_task (find by title context)
- "Change the meeting task title" → Use update_task

### Pronoun Resolution
When users say "it", "that", or "the first one", use context from the conversation:
- If you just created a task, "it" refers to that task
- If you just listed tasks, "the first one" refers to the first in the list
- Ask for clarification if the reference is ambiguous

### Clarifying Questions
If the user's intent is unclear, ask a brief clarifying question:
- "Which task would you like me to complete?"
- "Could you tell me more about what you'd like to add?"
- "I found multiple tasks. Which one did you mean?"

### Response Style
- Be conversational and friendly, not robotic
- Confirm actions: "I've added 'Buy groceries' to your tasks!"
- Be concise but helpful
- Never show raw JSON or technical errors to users
- If a task isn't found, say "I couldn't find that task" not "Error: not found"

### Example Conversations

User: "Add a task to finish the report"
Assistant: "I've added 'Finish the report' to your tasks! Is there anything else you'd like to add?"

User: "What do I have to do today?"
Assistant: "Here are your pending tasks:
1. Finish the report
2. Call mom
3. Buy groceries
Would you like to mark any of these as complete?"

User: "Mark the first one as done"
Assistant: "Great job! I've marked 'Finish the report' as complete. You have 2 tasks remaining."

User: "Actually, delete that"
Assistant: "I've removed 'Finish the report' from your tasks."

## Important Rules
- Always confirm what action you took
- Never access tasks from other users (this is handled automatically)
- Handle errors gracefully with friendly messages
- Keep responses concise but informative
"""


async def run_agent(
    user_id: str,
    db: Session,
    message: str,
    history: Optional[list[dict]] = None
) -> tuple[str, list[dict], bool]:
    """Run the TaskBot agent with user context and message history.

    Implements the 9-step stateless conversation flow:
    1. Receive user message (done by caller)
    2. Fetch conversation history from database (done by caller)
    3. Build message array for agent (history + new message) <- THIS FUNCTION
    4. Store user message in database (done by caller)
    5. Run agent with MCP tools <- THIS FUNCTION
    6. Agent invokes appropriate MCP tool(s) <- THIS FUNCTION
    7. Store assistant response in database (done by caller)
    8. Return response to client <- THIS FUNCTION
    9. Server holds NO state (ready for next request)

    Args:
        user_id: The authenticated user's ID.
        db: Database session for tool operations.
        message: The user's current message.
        history: Previous messages in OpenAI format [{"role": "...", "content": "..."}]

    Returns:
        Tuple of (assistant_response, tool_calls_made, tasks_changed)
    """
    # Snapshot task states before agent runs to detect any changes (add/delete/update/complete)
    tasks_before = db.exec(select(Task).where(Task.user_id == user_id)).all()
    task_count_before = len(tasks_before)
    task_states_before = {t.id: (t.title, t.is_completed, str(t.updated_at)) for t in tasks_before}
    
    # Create agent with tools
    agent = Agent(
        name="TaskBot",
        instructions=AGENT_INSTRUCTIONS,
        tools=ALL_TOOLS,
    )

    # Create user context for tool execution
    context = UserContext(user_id=user_id, db=db)

    # Step 3: Build message array (history + new message)
    # Use structured OpenAI message format for proper conversation state
    input_messages = []

    if history and len(history) > 0:
        # Add conversation history (last 20 messages per FR-027)
        for msg in history:
            input_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    # Add current user message
    input_messages.append({
        "role": "user",
        "content": message
    })

    # Steps 5-6: Run agent with tools
    # Agent will invoke MCP tools as needed based on user intent
    result = await Runner.run(
        agent,
        input=input_messages,
        context=context,
        run_config=config
    )

    # Snapshot task states after agent runs to detect any changes
    tasks_after = db.exec(select(Task).where(Task.user_id == user_id)).all()
    task_count_after = len(tasks_after)
    task_states_after = {t.id: (t.title, t.is_completed, str(t.updated_at)) for t in tasks_after}

    # Detect changes: count difference (add/delete) OR state difference (update/complete)
    tasks_changed = (
        task_count_before != task_count_after
        or task_states_before != task_states_after
    )

    # Collect tool calls made during execution
    tool_calls = []

    if hasattr(result, 'new_items'):
        for item in result.new_items:
            # Function call items
            if hasattr(item, 'type') and item.type == 'function_call':
                tool_calls.append({
                    "tool": getattr(item, 'name', str(item)),
                    "args": getattr(item, 'arguments', {}),
                    "result": {}
                })
            # Function call output items - attach result to the last tool call
            elif hasattr(item, 'type') and item.type == 'function_call_output':
                if tool_calls and hasattr(item, 'output'):
                    tool_calls[-1]["result"] = item.output if isinstance(item.output, dict) else {"output": str(item.output)}

    # Fallback: if no tool calls were parsed but task state changed, report it
    if not tool_calls and tasks_changed:
        tool_calls = [{
            "tool": "task_change_detected",
            "args": {},
            "result": {"message": "Task state changed"}
        }]

    # Step 8: Return response (step 9 is automatic - no state retained)
    return result.final_output, tool_calls, tasks_changed


# Synchronous version for compatibility
def run_agent_sync(
    user_id: str,
    db: Session,
    message: str,
    history: Optional[list[dict]] = None
) -> tuple[str, list[dict], bool]:
    """Synchronous wrapper for run_agent."""
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(run_agent(user_id, db, message, history))
