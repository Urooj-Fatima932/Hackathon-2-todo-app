# Streaming Responses

Handle real-time streaming from AI backends.

## Server-Sent Events (SSE)

### Backend (FastAPI)

```python
# app/routers/chat.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from agents import Agent, Runner

router = APIRouter()

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        async with MCPServerStreamableHttp(...) as mcp:
            agent = Agent(name="Assistant", mcp_servers=[mcp])
            result = Runner.run_streamed(agent, request.message)

            async for event in result.stream_events():
                if hasattr(event, 'delta') and event.delta:
                    yield f"data: {json.dumps({'delta': event.delta})}\n\n"

            await result.wait()
            yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )
```

### Frontend (EventSource)

```tsx
const sendMessageStreaming = async (text: string) => {
  setMessages(prev => [...prev, { role: 'user', content: text }]);
  setMessages(prev => [...prev, { role: 'assistant', content: '' }]);
  setIsLoading(true);

  const eventSource = new EventSource(
    `/api/chat/stream?message=${encodeURIComponent(text)}&user_id=${userId}`
  );

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.done) {
      eventSource.close();
      setIsLoading(false);
      return;
    }

    if (data.delta) {
      setMessages(prev => {
        const updated = [...prev];
        const lastIdx = updated.length - 1;
        updated[lastIdx] = {
          ...updated[lastIdx],
          content: updated[lastIdx].content + data.delta,
        };
        return updated;
      });
    }
  };

  eventSource.onerror = () => {
    eventSource.close();
    setIsLoading(false);
  };
};
```

## Fetch with ReadableStream

For POST requests (EventSource only supports GET):

```tsx
const sendMessageStreaming = async (text: string) => {
  const userMessage = { role: 'user' as const, content: text };
  setMessages(prev => [...prev, userMessage]);
  setIsLoading(true);

  // Add empty assistant message for streaming
  setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

  try {
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, message: text }),
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    if (!response.body) throw new Error('No response body');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });

      // Parse SSE format
      const lines = chunk.split('\n');
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          if (data.delta) {
            setMessages(prev => {
              const updated = [...prev];
              const lastIdx = updated.length - 1;
              updated[lastIdx] = {
                ...updated[lastIdx],
                content: updated[lastIdx].content + data.delta,
              };
              return updated;
            });
          }
        }
      }
    }
  } catch (error) {
    console.error('Streaming error:', error);
  } finally {
    setIsLoading(false);
  }
};
```

## Custom useStreamingChat Hook

```tsx
// hooks/useStreamingChat.ts
import { useState, useCallback } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export function useStreamingChat(apiUrl: string, userId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    // Add placeholder for assistant
    const assistantId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: assistantId, role: 'assistant', content: '' }]);

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, message: text }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Process complete SSE messages
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.delta) {
                setMessages(prev =>
                  prev.map(m =>
                    m.id === assistantId
                      ? { ...m, content: m.content + data.delta }
                      : m
                  )
                );
              }
            } catch {
              // Ignore parse errors for incomplete JSON
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setIsLoading(false);
    }
  }, [apiUrl, userId, isLoading]);

  const stop = useCallback(() => {
    // AbortController can be added for cancellation
    setIsLoading(false);
  }, []);

  return { messages, isLoading, error, sendMessage, stop };
}
```

## With AbortController (Cancellation)

```tsx
const [abortController, setAbortController] = useState<AbortController | null>(null);

const sendMessage = async (text: string) => {
  const controller = new AbortController();
  setAbortController(controller);

  try {
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
      signal: controller.signal,
    });

    // ... streaming logic
  } catch (err) {
    if (err.name === 'AbortError') {
      console.log('Request cancelled');
    } else {
      throw err;
    }
  } finally {
    setAbortController(null);
  }
};

const stop = () => {
  abortController?.abort();
};
```

## Streaming Message Component

```tsx
interface StreamingMessageProps {
  content: string;
  isStreaming: boolean;
}

export function StreamingMessage({ content, isStreaming }: StreamingMessageProps) {
  return (
    <div className="bg-gray-100 p-3 rounded-lg">
      <p className="whitespace-pre-wrap">
        {content}
        {isStreaming && (
          <span className="inline-block w-2 h-4 bg-gray-400 ml-1 animate-pulse" />
        )}
      </p>
    </div>
  );
}
```

## Key Points

1. **SSE format** - `data: {json}\n\n` for each chunk
2. **ReadableStream** - Use for POST requests (EventSource is GET only)
3. **Buffer incomplete lines** - SSE can split across chunks
4. **Placeholder message** - Add empty assistant message before streaming
5. **AbortController** - Allow users to stop generation
6. **Cursor animation** - Show typing cursor during stream
