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
) -> tuple[str, list[dict]]:
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
        Tuple of (assistant_response, tool_calls_made)
    """
    # Count tasks before agent runs to detect changes
    task_count_before = len(db.exec(select(Task).where(Task.user_id == user_id)).all())
    
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

    # Count tasks after agent runs to detect changes
    task_count_after = len(db.exec(select(Task).where(Task.user_id == user_id)).all())
    
    # Collect tool calls made during execution
    tool_calls = []
    print(f"[Agent] Result type: {type(result)}")
    print(f"[Agent] Result attributes: {dir(result)}")
    
    # Debug the result object
    print(f"[Agent] Result: {result}")
    
    # Different ways the result might contain tool calls depending on the agent library version
    if hasattr(result, 'tool_calls') and result.tool_calls:
        # Direct tool_calls attribute
        print(f"[Agent] Found direct tool_calls: {result.tool_calls}")
        for tc in result.tool_calls:
            tool_calls.append({
                "tool": getattr(tc, 'name', str(tc)) if tc else "",
                "args": getattr(tc, 'arguments', {}) if tc else {},
                "result": {}
            })
    elif hasattr(result, 'new_items'):
        print(f"[Agent] new_items count: {len(result.new_items)}")
        for i, item in enumerate(result.new_items):
            print(f"[Agent] Item {i}: type={type(item)}, attrs={dir(item)}")
            if hasattr(item, 'type'):
                print(f"[Agent] Item {i} type value: {item.type}")
            # Check for tool call items
            if hasattr(item, 'type') and item.type == 'function_call':
                tool_calls.append({
                    "tool": item.name if hasattr(item, 'name') else str(item),
                    "args": item.arguments if hasattr(item, 'arguments') else {},
                    "result": {}
                })
            # Also check for tool_calls attribute (legacy format)
            elif hasattr(item, 'tool_calls') and item.tool_calls:
                for tc in item.tool_calls:
                    tool_calls.append({
                        "tool": tc.name if hasattr(tc, 'name') else str(tc),
                        "args": tc.arguments if hasattr(tc, 'arguments') else {},
                        "result": {}
                    })
            # Check for function call results
            elif hasattr(item, 'type') and item.type == 'function_call_output':
                # Find matching tool call and add result
                if tool_calls and hasattr(item, 'output'):
                    tool_calls[-1]["result"] = item.output if isinstance(item.output, dict) else {"output": str(item.output)}
    else:
        # Check if result has any attributes that might contain tool call info
        for attr_name in dir(result):
            if 'tool' in attr_name.lower() or 'call' in attr_name.lower():
                attr_value = getattr(result, attr_name)
                print(f"[Agent] Found potential tool-related attribute '{attr_name}': {attr_value}")
    
    # Determine if tasks were modified (added, updated, or deleted)
    tasks_changed = task_count_before != task_count_after
    
    # If no tool calls were reported but tasks changed, add a generic task change indicator
    if not tool_calls and tasks_changed:
        print(f"[Agent] Tasks changed ({task_count_before} -> {task_count_after}) but no tool calls reported, adding generic indicator")
        tool_calls = [{
            "tool": "task_change_detected",
            "args": {"change_type": "unknown", "before_count": task_count_before, "after_count": task_count_after},
            "result": {"message": "Task state changed"}
        }]
    elif tasks_changed and tool_calls:
        print(f"[Agent] Tasks changed ({task_count_before} -> {task_count_after}) and tool calls were reported: {tool_calls}")
    
    print(f"[Agent] Final tool_calls: {tool_calls}")

    # Step 8: Return response (step 9 is automatic - no state retained)
    return result.final_output, tool_calls


# Synchronous version for compatibility
def run_agent_sync(
    user_id: str,
    db: Session,
    message: str,
    history: Optional[list[dict]] = None
) -> tuple[str, list[dict]]:
    """Synchronous wrapper for run_agent."""
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(run_agent(user_id, db, message, history))
