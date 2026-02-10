# Stateless Conversation Flow

## The 9-Step Request Cycle

Server holds NO state between requests. Each request is independent.

```
1. Receive user message
2. Fetch conversation history from database
3. Build message array for agent (history + new message)
4. Store user message in database
5. Run agent with MCP tools
6. Agent invokes appropriate MCP tool(s)
7. Store assistant response in database
8. Return response to client
9. Server holds NO state (ready for next request)
```

## Implementation

```python
# app/services/chat_service.py
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

class ChatService:
    def __init__(self, db: AsyncSession, mcp_url: str):
        self.db = db
        self.mcp_url = mcp_url
        self.message_repo = MessageRepository(db)

    async def process_message(
        self,
        user_id: str,
        message: str,
    ) -> str:
        """Execute the 9-step stateless flow."""

        # Step 1: Receive (already done - message parameter)

        # Step 2: Fetch conversation history
        history = await self.message_repo.get_history(user_id)

        # Step 3: Build message array
        messages = self._build_messages(history, message)

        # Step 4: Store user message
        await self.message_repo.create(
            user_id=user_id,
            role="user",
            content=message,
        )

        # Step 5-6: Run agent with MCP tools
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

        assistant_response = result.final_output

        # Step 7: Store assistant response
        await self.message_repo.create(
            user_id=user_id,
            role="assistant",
            content=assistant_response,
        )

        # Step 8: Return response
        # Step 9: Server stateless (no cleanup needed)
        return assistant_response

    def _build_messages(
        self,
        history: list[Message],
        new_message: str,
    ) -> list[dict]:
        """Build OpenAI-format message array."""
        messages = []

        for msg in history:
            messages.append({
                "role": msg.role,
                "content": msg.content,
            })

        messages.append({
            "role": "user",
            "content": new_message,
        })

        return messages

    def _get_instructions(self) -> str:
        """Return agent system instructions."""
        return """You are a helpful assistant.

Use the available tools to help users manage their data.
Always confirm actions with a friendly response.
Handle errors gracefully."""
```

## Why Stateless?

| Benefit | Explanation |
|---------|-------------|
| **Resilience** | Server restarts don't lose conversation state |
| **Horizontal Scaling** | Load balancer can route to any backend instance |
| **Testability** | Each request is independent and reproducible |
| **Simplicity** | No session management, no memory leaks |

## Key Points

1. **Database is source of truth** - All conversation state lives in DB
2. **Each request fetches fresh** - No in-memory caching of conversations
3. **Store before and after** - User message stored before agent, response stored after
4. **MCP connection per request** - Create and dispose MCP connection each time
5. **No global state** - Service instance can be created fresh each request
