# Tracing

## Overview

Tracing captures agent execution for debugging and monitoring. Enabled by default.

## Disable Tracing

```python
# Environment variable
# OPENAI_AGENTS_DISABLE_TRACING=1

# Per-run
from agents import Runner, RunConfig

result = await Runner.run(
    agent,
    message,
    run_config=RunConfig(tracing_disabled=True),
)
```

## What Gets Traced

- Agent executions
- LLM generations (inputs/outputs)
- Function tool calls
- Guardrail operations
- Handoffs
- MCP tool listings and calls

## Custom Traces

Group multiple runs under one trace:

```python
from agents import Agent, Runner, trace

agent = Agent(name="NotesAgent", instructions="...")

async def create_and_verify():
    with trace("Create Note Workflow"):
        # First run
        result1 = await Runner.run(agent, "Create a note titled Test")

        # Second run (same trace)
        result2 = await Runner.run(agent, "Verify the note was created")

    return result2.final_output
```

## Trace Metadata

```python
with trace(
    "Note Operations",
    group_id="user_123",  # Group related traces
    metadata={"user_tier": "premium"},
):
    result = await Runner.run(agent, message)
```

## Sensitive Data

Control what gets captured:

```python
# Disable sensitive data (LLM inputs/outputs, tool data)
result = await Runner.run(
    agent,
    message,
    run_config=RunConfig(trace_include_sensitive_data=False),
)

# Or via environment
# OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA=false
```

## Custom Trace Processors

### Add Processor (alongside default)

```python
from agents.tracing import add_trace_processor

class CustomProcessor:
    async def process_trace(self, trace_data):
        # Send to your logging system
        await my_logger.log(trace_data)

add_trace_processor(CustomProcessor())
```

### Replace Default Processors

```python
from agents.tracing import set_trace_processors

set_trace_processors([CustomProcessor()])
```

## External Integrations

Supported platforms:
- Weights & Biases
- Arize-Phoenix
- MLflow
- LangSmith
- Datadog
- And 20+ more

## FastAPI Integration

```python
from fastapi import FastAPI
from agents import Agent, Runner, trace

app = FastAPI()
agent = Agent(name="NotesAgent", instructions="...")

@app.post("/chat")
async def chat(user_id: str, message: str):
    with trace(
        "Chat Request",
        group_id=user_id,
        metadata={"endpoint": "/chat"},
    ):
        result = await Runner.run(agent, message)
        return {"response": result.final_output}
```

## Best Practices

1. **Keep tracing enabled** in development for debugging
2. **Disable sensitive data** in production if needed
3. **Use group_id** to correlate traces per user/session
4. **Add metadata** for filtering and analytics
5. **Custom processors** for your observability stack
