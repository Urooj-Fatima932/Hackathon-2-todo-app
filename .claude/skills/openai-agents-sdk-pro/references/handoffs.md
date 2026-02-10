# Handoffs

## Overview

Handoffs enable agents to delegate tasks to specialized agents. Useful for:
- Different domains (billing vs support)
- Different expertise levels (basic vs advanced)
- Complex workflows with multiple steps

## Basic Handoff

```python
from agents import Agent, handoff

# Specialist agents
billing_agent = Agent(
    name="BillingAgent",
    instructions="Handle billing questions and payment issues.",
    tools=[get_invoice, process_payment],
)

support_agent = Agent(
    name="SupportAgent",
    instructions="Handle general support questions.",
    tools=[search_faq, create_ticket],
)

# Triage agent that routes to specialists
triage_agent = Agent(
    name="TriageAgent",
    instructions="""Route users to the right specialist:
- Billing questions → BillingAgent
- General support → SupportAgent""",
    handoffs=[billing_agent, support_agent],
)
```

## Customizing Handoffs

```python
from agents import handoff

triage_agent = Agent(
    name="TriageAgent",
    handoffs=[
        handoff(
            billing_agent,
            tool_name_override="transfer_to_billing",
            tool_description_override="Transfer to billing for payment issues",
        ),
        handoff(
            support_agent,
            tool_name_override="transfer_to_support",
            tool_description_override="Transfer for general questions",
        ),
    ],
)
```

## Handoff with Data

Pass data when transferring:

```python
from pydantic import BaseModel
from agents import handoff

class EscalationData(BaseModel):
    reason: str
    priority: str
    customer_id: int

async def on_escalate(ctx, data: EscalationData):
    print(f"Escalating: {data.reason} (Priority: {data.priority})")
    # Log, notify, etc.

escalation_agent = Agent(
    name="EscalationAgent",
    instructions="Handle escalated issues.",
)

support_agent = Agent(
    name="SupportAgent",
    handoffs=[
        handoff(
            escalation_agent,
            input_type=EscalationData,
            on_handoff=on_escalate,
        ),
    ],
)
```

## Input Filters

Control what context passes to the next agent:

```python
from agents.extensions.handoff_filters import remove_tool_calls

triage_agent = Agent(
    name="TriageAgent",
    handoffs=[
        handoff(
            billing_agent,
            # Remove tool call history from conversation
            input_filter=remove_tool_calls,
        ),
    ],
)
```

## Dynamic Handoff Enabling

```python
def can_escalate(ctx, agent):
    # Only allow escalation for premium users
    return ctx.context.user.is_premium

support_agent = Agent(
    name="SupportAgent",
    handoffs=[
        handoff(
            escalation_agent,
            is_enabled=can_escalate,
        ),
    ],
)
```

## Handoff Prompt Helper

Use recommended prefix in instructions:

```python
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

triage_agent = Agent(
    name="TriageAgent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}

You are a triage agent. Route users to specialists:
- Billing issues → BillingAgent
- Technical problems → TechAgent
- General questions → SupportAgent""",
    handoffs=[billing_agent, tech_agent, support_agent],
)
```

## Multi-Agent Example: Notes App

```python
from agents import Agent, handoff, function_tool

# Note creation specialist
@function_tool
async def create_note(title: str, content: str) -> str:
    """Create a new note."""
    note = await note_service.create(title, content)
    return f"Created note: {note.title}"

create_agent = Agent(
    name="CreateAgent",
    instructions="""You create notes. Ask user for:
1. Title
2. Content
Then create the note.""",
    tools=[create_note],
)

# Note management specialist
@function_tool
async def list_notes() -> str:
    """List all notes."""
    notes = await note_service.list()
    return "\n".join(f"- [{n.id}] {n.title}" for n in notes)

@function_tool
async def delete_note(note_id: int) -> str:
    """Delete a note."""
    await note_service.delete(note_id)
    return f"Deleted note {note_id}"

manage_agent = Agent(
    name="ManageAgent",
    instructions="Help users view and delete notes.",
    tools=[list_notes, delete_note],
)

# Triage agent
triage_agent = Agent(
    name="NotesAssistant",
    instructions="""You are a notes assistant. Route users:
- Creating notes → CreateAgent
- Viewing/deleting notes → ManageAgent

Ask clarifying questions if intent is unclear.""",
    handoffs=[
        handoff(create_agent, tool_description_override="For creating new notes"),
        handoff(manage_agent, tool_description_override="For viewing or deleting notes"),
    ],
)

# Run
result = await Runner.run(triage_agent, "I want to make a new note")
# Agent will handoff to CreateAgent
```

## Handoff vs Agent-as-Tool

| Feature | Handoff | Agent-as-Tool |
|---------|---------|---------------|
| Control | Transfers to specialist | Returns to original |
| Context | Can filter history | Receives task only |
| Use case | Domain routing | Subtask delegation |

### Agent-as-Tool Pattern

```python
from agents import Agent

# Sub-agent for research
research_agent = Agent(
    name="ResearchAgent",
    instructions="Research topics and return summaries.",
)

# Main agent uses research as tool
main_agent = Agent(
    name="MainAgent",
    instructions="Help users. Use research tool for complex questions.",
    tools=[research_agent.as_tool(
        tool_name="research",
        tool_description="Research a topic and get summary",
    )],
)
```

## Best Practices

1. **Clear routing instructions**: Tell triage agent exactly when to handoff
2. **Descriptive handoff names**: Help LLM choose correctly
3. **Use input filters**: Don't pass unnecessary context
4. **Specialist focus**: Each agent should have narrow expertise
5. **Return paths**: Consider if specialists need to hand back
