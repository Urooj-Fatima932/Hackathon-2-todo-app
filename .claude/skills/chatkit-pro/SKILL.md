---
name: chatkit-pro
description: |
  Generates production-grade chat interfaces for AI chatbots using React, chatscope/chat-ui-kit,
  or Vercel AI SDK patterns. This skill should be used when users want to create chat UIs with
  streaming responses, message handling, typing indicators, and backend API integration.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
---

# ChatKit Pro

Generate chat interfaces for AI-powered chatbots and agentic applications.

## What This Skill Does

- Creates chat UI components with React/Next.js
- Implements streaming response rendering
- Sets up message state management
- Configures typing indicators and loading states
- Integrates with backend chat APIs
- Handles error states and retry logic
- Supports multiple chat libraries (chatscope, custom, Vercel AI SDK)

## What This Skill Does NOT Do

- Create backend chat endpoints (use fastapi-pro + agentic-chatbot-pro)
- Handle authentication (use fullstack-auth)
- Deploy chat applications
- Implement real-time WebSocket (focus is HTTP/SSE streaming)

---

## Before Implementation

| Source | Gather |
|--------|--------|
| **Conversation** | User's library preference, styling needs, backend API format |
| **Codebase** | Existing React/Next.js setup, styling approach (Tailwind, CSS) |
| **Skill References** | Component patterns, streaming handling, state management |

---

## Clarifications (Ask User)

1. **Library preference?** - chatscope, custom components, or Vercel AI SDK?
2. **Framework?** - Next.js App Router, Pages Router, or plain React?
3. **Styling?** - Tailwind CSS, chatscope styles, or custom CSS?
4. **Backend API format?** - Endpoint URL, request/response shape?
5. **Features needed?** - Streaming, typing indicator, file attachments?

---

## Library Comparison

| Library | Best For | Streaming | Complexity |
|---------|----------|-----------|------------|
| **chatscope** | Full-featured chat UI | Manual | Medium |
| **Vercel AI SDK** | AI chatbots with streaming | Built-in | Low |
| **Custom** | Full control, minimal deps | Manual | High |

---

## Architecture

```
┌─────────────────────────────────────────┐
│              Chat Interface              │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐    │
│  │         Message List            │    │
│  │  ┌─────────────────────────┐    │    │
│  │  │ User Message            │    │    │
│  │  └─────────────────────────┘    │    │
│  │  ┌─────────────────────────┐    │    │
│  │  │ Assistant Message       │    │    │
│  │  │ (streaming...)          │    │    │
│  │  └─────────────────────────┘    │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │ [Message Input]      [Send]     │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
           │
           ▼
    POST /api/chat
    {user_id, message}
           │
           ▼
    {response: "..."}
```

---

## Component Structure

```
components/
├── chat/
│   ├── ChatContainer.tsx      # Main wrapper
│   ├── MessageList.tsx        # Scrollable message area
│   ├── Message.tsx            # Individual message
│   ├── MessageInput.tsx       # Input + send button
│   ├── TypingIndicator.tsx    # Loading/typing state
│   └── index.ts               # Exports
└── hooks/
    └── useChat.ts             # Chat state management
```

---

## Generation Process

1. **Ask clarifications** (library, framework, styling)
2. **Generate hook** (useChat or use library's hook)
3. **Generate components** (container, list, message, input)
4. **Generate styles** (Tailwind or CSS)
5. **Wire up to API** (fetch/stream integration)

---

## Standards

| Component | Reference |
|-----------|-----------|
| Chatscope integration | `references/chatscope.md` |
| Custom components | `references/custom-components.md` |
| Vercel AI SDK | `references/vercel-ai-sdk.md` |
| Streaming patterns | `references/streaming.md` |
| State management | `references/state-management.md` |

---

## Quick Reference

### Basic Custom Chat (Tailwind)

```tsx
'use client';
import { useState } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user' as const, content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 'user123', message: input }),
    });

    const data = await res.json();
    setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m, i) => (
          <div key={i} className={`p-3 rounded-lg ${
            m.role === 'user' ? 'bg-blue-100 ml-auto' : 'bg-gray-100'
          } max-w-[80%]`}>
            {m.content}
          </div>
        ))}
        {loading && <div className="bg-gray-100 p-3 rounded-lg">Thinking...</div>}
      </div>
      <div className="p-4 border-t flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && sendMessage()}
          placeholder="Type a message..."
          className="flex-1 p-2 border rounded-lg"
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}
```

### With Streaming

```tsx
const sendMessage = async () => {
  // ... setup
  const res = await fetch('/api/chat/stream', {
    method: 'POST',
    body: JSON.stringify({ user_id: 'user123', message: input }),
  });

  const reader = res.body?.getReader();
  const decoder = new TextDecoder();
  let assistantContent = '';

  setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;

    const chunk = decoder.decode(value);
    assistantContent += chunk;

    setMessages(prev => {
      const updated = [...prev];
      updated[updated.length - 1].content = assistantContent;
      return updated;
    });
  }
};
```

---

## Checklist

- [ ] Library chosen and installed
- [ ] Components created (container, list, message, input)
- [ ] State management implemented (messages, input, loading)
- [ ] API integration working
- [ ] Streaming handled (if needed)
- [ ] Error states displayed
- [ ] Loading/typing indicator shown
- [ ] Responsive design tested
- [ ] Keyboard navigation (Enter to send)
