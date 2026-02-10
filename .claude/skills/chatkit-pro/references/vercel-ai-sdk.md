# Vercel AI SDK useChat

## Installation

```bash
npm install ai
# or
yarn add ai
```

## Basic Usage

```tsx
'use client';
import { useChat } from 'ai/react';

export function Chat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
  });

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4">
      <div className="flex-1 overflow-y-auto space-y-4">
        {messages.map(m => (
          <div
            key={m.id}
            className={`p-3 rounded-lg ${
              m.role === 'user' ? 'bg-blue-100 ml-auto' : 'bg-gray-100'
            } max-w-[80%]`}
          >
            {m.content}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2 mt-4">
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="Type a message..."
          className="flex-1 p-2 border rounded-lg"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}
```

## useChat Return Values

| Property | Type | Description |
|----------|------|-------------|
| `messages` | `Message[]` | All chat messages |
| `input` | `string` | Current input value |
| `handleInputChange` | `function` | Input onChange handler |
| `handleSubmit` | `function` | Form submit handler |
| `isLoading` | `boolean` | Request in progress |
| `error` | `Error` | Error state |
| `stop` | `function` | Stop streaming |
| `reload` | `function` | Regenerate last response |
| `setMessages` | `function` | Manually set messages |
| `append` | `function` | Add message programmatically |

## Message Structure

```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt?: Date;
}
```

## With Custom Headers/Body

```tsx
const { messages, input, handleSubmit } = useChat({
  api: '/api/chat',
  headers: {
    Authorization: `Bearer ${token}`,
  },
  body: {
    user_id: userId,
    conversation_id: conversationId,
  },
});
```

## Error Handling

```tsx
const { messages, error, reload } = useChat({
  api: '/api/chat',
  onError: (err) => {
    console.error('Chat error:', err);
  },
});

return (
  <div>
    {error && (
      <div className="text-red-500">
        Error: {error.message}
        <button onClick={() => reload()}>Retry</button>
      </div>
    )}
    {/* messages */}
  </div>
);
```

## With Initial Messages

```tsx
const { messages } = useChat({
  api: '/api/chat',
  initialMessages: [
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! How can I help you today?',
    },
  ],
});
```

## Streaming Indicator

```tsx
const { messages, isLoading } = useChat({ api: '/api/chat' });

return (
  <div>
    {messages.map(m => (
      <div key={m.id}>{m.content}</div>
    ))}
    {isLoading && (
      <div className="animate-pulse">Thinking...</div>
    )}
  </div>
);
```

## Backend Route (Next.js)

```typescript
// app/api/chat/route.ts
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('gpt-4o'),
    messages,
  });

  return result.toDataStreamResponse();
}
```

## With Tool Calls

```tsx
const { messages } = useChat({
  api: '/api/chat',
  maxSteps: 5, // Allow up to 5 tool calls
});

// Render tool invocations
{messages.map(m => (
  <div key={m.id}>
    {m.content}
    {m.toolInvocations?.map(tool => (
      <div key={tool.toolCallId}>
        Tool: {tool.toolName}
        Result: {JSON.stringify(tool.result)}
      </div>
    ))}
  </div>
))}
```

## Callbacks

```tsx
const { messages } = useChat({
  api: '/api/chat',
  onFinish: (message) => {
    console.log('Response complete:', message);
  },
  onResponse: (response) => {
    console.log('Response started:', response.status);
  },
});
```

## Key Points

1. **Automatic streaming** - Built-in streaming support
2. **Managed state** - No manual useState for messages/input
3. **Form helpers** - handleInputChange/handleSubmit ready to use
4. **Error recovery** - reload() to retry failed requests
5. **Tool support** - Handles function calling automatically
