# Guardrails

## Overview

Guardrails validate agent inputs and outputs. They can:
- Block inappropriate requests
- Validate output quality
- Save costs by rejecting bad inputs early

## Input Guardrails

Run before agent processes input:

```python
from agents import Agent, InputGuardrail, GuardrailFunctionOutput

async def check_appropriate(ctx, agent, input_data) -> GuardrailFunctionOutput:
    """Check if input is appropriate."""
    # Simple keyword check
    blocked_words = ["hack", "exploit", "bypass"]
    text = str(input_data).lower()

    if any(word in text for word in blocked_words):
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info="Request contains blocked content.",
        )

    return GuardrailFunctionOutput(tripwire_triggered=False)

guardrail = InputGuardrail(guardrail_function=check_appropriate)

agent = Agent(
    name="NotesAgent",
    instructions="Help with notes.",
    input_guardrails=[guardrail],
)
```

### Using LLM for Input Validation

```python
from agents import Agent, Runner, InputGuardrail, GuardrailFunctionOutput

# Validation agent
validator_agent = Agent(
    name="Validator",
    instructions="""Check if the request is appropriate for a notes app.
Return "ALLOWED" if ok, "BLOCKED: reason" if not.""",
)

async def llm_input_check(ctx, agent, input_data) -> GuardrailFunctionOutput:
    result = await Runner.run(validator_agent, str(input_data))
    output = result.final_output

    if output.startswith("BLOCKED"):
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info=output,
        )
    return GuardrailFunctionOutput(tripwire_triggered=False)

guardrail = InputGuardrail(guardrail_function=llm_input_check)
```

### Execution Modes

```python
# Parallel (default) - guardrail runs alongside agent
# Faster but agent may start before guardrail finishes
guardrail = InputGuardrail(
    guardrail_function=check_appropriate,
    parallel=True,  # default
)

# Blocking - guardrail must pass before agent starts
# Slower but safer, prevents any token usage if blocked
guardrail = InputGuardrail(
    guardrail_function=check_appropriate,
    parallel=False,
)
```

## Output Guardrails

Run after agent produces output:

```python
from agents import Agent, OutputGuardrail, GuardrailFunctionOutput

async def check_output(ctx, agent, output) -> GuardrailFunctionOutput:
    """Ensure output doesn't contain sensitive info."""
    text = str(output).lower()

    # Check for accidentally exposed data
    if "password" in text or "secret" in text:
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info="Output may contain sensitive information.",
        )

    return GuardrailFunctionOutput(tripwire_triggered=False)

guardrail = OutputGuardrail(guardrail_function=check_output)

agent = Agent(
    name="NotesAgent",
    instructions="Help with notes.",
    output_guardrails=[guardrail],
)
```

## Tool Guardrails

Validate tool inputs/outputs:

```python
from agents import (
    function_tool,
    InputToolGuardrail,
    OutputToolGuardrail,
    ToolGuardrailFunctionOutput,
)

# Input guardrail - runs before tool
async def check_delete_permission(ctx, agent, tool_input) -> ToolGuardrailFunctionOutput:
    """Confirm user has permission to delete."""
    if not ctx.context.user.can_delete:
        return ToolGuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info="User cannot delete notes.",
        )
    return ToolGuardrailFunctionOutput(tripwire_triggered=False)

# Output guardrail - runs after tool
async def sanitize_output(ctx, agent, tool_output) -> ToolGuardrailFunctionOutput:
    """Ensure output doesn't leak data."""
    return ToolGuardrailFunctionOutput(
        tripwire_triggered=False,
        output_info=tool_output.replace("internal_id=", "id="),
    )

@function_tool(
    input_guardrails=[InputToolGuardrail(guardrail_function=check_delete_permission)],
    output_guardrails=[OutputToolGuardrail(guardrail_function=sanitize_output)],
)
async def delete_note(note_id: int) -> str:
    """Delete a note."""
    await note_service.delete(note_id)
    return f"Deleted note internal_id={note_id}"
```

## Handling Tripwires

```python
from agents import Runner, InputGuardrailTripwireTriggered

agent = Agent(
    name="NotesAgent",
    input_guardrails=[guardrail],
)

try:
    result = await Runner.run(agent, user_message)
    return result.final_output
except InputGuardrailTripwireTriggered as e:
    return f"Request blocked: {e.guardrail_result.output_info}"
```

## Multiple Guardrails

```python
agent = Agent(
    name="NotesAgent",
    instructions="Help with notes.",
    input_guardrails=[
        profanity_guardrail,
        injection_guardrail,
        rate_limit_guardrail,
    ],
    output_guardrails=[
        pii_guardrail,
        quality_guardrail,
    ],
)
```

## Complete Example

```python
from agents import (
    Agent,
    Runner,
    InputGuardrail,
    OutputGuardrail,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
)

# Input: Check for prompt injection attempts
async def check_injection(ctx, agent, input_data) -> GuardrailFunctionOutput:
    text = str(input_data).lower()
    injection_patterns = [
        "ignore previous",
        "disregard instructions",
        "new instructions",
        "system prompt",
    ]

    if any(p in text for p in injection_patterns):
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info="Potential prompt injection detected.",
        )
    return GuardrailFunctionOutput(tripwire_triggered=False)

# Output: Ensure no PII in responses
async def check_pii(ctx, agent, output) -> GuardrailFunctionOutput:
    import re
    text = str(output)

    # Check for email patterns
    if re.search(r'\b[\w.-]+@[\w.-]+\.\w+\b', text):
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info="Output contains email address.",
        )
    return GuardrailFunctionOutput(tripwire_triggered=False)

agent = Agent(
    name="NotesAgent",
    instructions="Help users manage notes.",
    input_guardrails=[InputGuardrail(guardrail_function=check_injection)],
    output_guardrails=[OutputGuardrail(guardrail_function=check_pii)],
)

async def chat(message: str) -> str:
    try:
        result = await Runner.run(agent, message)
        return result.final_output
    except InputGuardrailTripwireTriggered:
        return "I can't process that request."
```

## Best Practices

1. **Use blocking mode** for critical input validation
2. **Cheap checks first**: Simple patterns before LLM-based checks
3. **Clear error messages**: Help users understand rejections
4. **Log tripwires**: Track what's being blocked for analysis
5. **Test guardrails**: Ensure they don't block legitimate requests
6. **Tool guardrails**: Protect destructive operations specifically
