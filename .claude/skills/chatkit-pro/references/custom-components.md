# Custom Chat Components

Build chat UI from scratch with React and Tailwind CSS.

## Component Structure

```
components/chat/
├── ChatContainer.tsx
├── MessageList.tsx
├── Message.tsx
├── MessageInput.tsx
├── TypingIndicator.tsx
├── useChat.ts
└── index.ts
```

## useChat Hook

```tsx
// hooks/useChat.ts
import { useState, useCallback } from 'react';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface UseChatOptions {
  apiUrl: string;
  userId: string;
  onError?: (error: Error) => void;
}

export function useChat({ apiUrl, userId, onError }: UseChatOptions) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const sendMessage = useCallback(async (text?: string) => {
    const messageText = text || input;
    if (!messageText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          message: messageText,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      onError?.(error);
    } finally {
      setIsLoading(false);
    }
  }, [apiUrl, userId, input, isLoading, onError]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    input,
    setInput,
    isLoading,
    error,
    sendMessage,
    clearMessages,
  };
}
```

## ChatContainer

```tsx
// components/chat/ChatContainer.tsx
'use client';
import { ReactNode } from 'react';

interface ChatContainerProps {
  children: ReactNode;
  className?: string;
}

export function ChatContainer({ children, className = '' }: ChatContainerProps) {
  return (
    <div className={`flex flex-col h-full bg-white rounded-lg shadow-lg ${className}`}>
      {children}
    </div>
  );
}
```

## MessageList

```tsx
// components/chat/MessageList.tsx
'use client';
import { useEffect, useRef, ReactNode } from 'react';

interface MessageListProps {
  children: ReactNode;
  className?: string;
}

export function MessageList({ children, className = '' }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  });

  return (
    <div className={`flex-1 overflow-y-auto p-4 space-y-4 ${className}`}>
      {children}
      <div ref={bottomRef} />
    </div>
  );
}
```

## Message

```tsx
// components/chat/Message.tsx
interface MessageProps {
  content: string;
  role: 'user' | 'assistant';
  timestamp?: Date;
  avatar?: string;
}

export function Message({ content, role, timestamp, avatar }: MessageProps) {
  const isUser = role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex items-end gap-2 max-w-[80%] ${isUser ? 'flex-row-reverse' : ''}`}>
        {avatar && (
          <img
            src={avatar}
            alt={role}
            className="w-8 h-8 rounded-full"
          />
        )}
        <div
          className={`px-4 py-2 rounded-2xl ${
            isUser
              ? 'bg-blue-500 text-white rounded-br-md'
              : 'bg-gray-100 text-gray-900 rounded-bl-md'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap">{content}</p>
          {timestamp && (
            <p className={`text-xs mt-1 ${isUser ? 'text-blue-100' : 'text-gray-400'}`}>
              {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
```

## MessageInput

```tsx
// components/chat/MessageInput.tsx
'use client';
import { useState, KeyboardEvent } from 'react';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function MessageInput({
  onSend,
  disabled = false,
  placeholder = 'Type a message...',
}: MessageInputProps) {
  const [value, setValue] = useState('');

  const handleSend = () => {
    if (value.trim() && !disabled) {
      onSend(value);
      setValue('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t p-4">
      <div className="flex items-center gap-2">
        <input
          type="text"
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={disabled}
          placeholder={placeholder}
          className="flex-1 px-4 py-2 border rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        />
        <button
          onClick={handleSend}
          disabled={disabled || !value.trim()}
          className="px-4 py-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            className="w-5 h-5"
          >
            <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
          </svg>
        </button>
      </div>
    </div>
  );
}
```

## TypingIndicator

```tsx
// components/chat/TypingIndicator.tsx
export function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-gray-100 px-4 py-2 rounded-2xl rounded-bl-md">
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
}
```

## Complete Chat Page

```tsx
// app/chat/page.tsx
'use client';
import {
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator,
} from '@/components/chat';
import { useChat } from '@/hooks/useChat';

export default function ChatPage() {
  const { messages, isLoading, sendMessage, error } = useChat({
    apiUrl: '/api/chat',
    userId: 'user123',
  });

  return (
    <div className="h-screen max-w-2xl mx-auto p-4">
      <ChatContainer>
        <div className="p-4 border-b">
          <h1 className="text-lg font-semibold">AI Assistant</h1>
        </div>

        <MessageList>
          {messages.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              Start a conversation!
            </div>
          )}
          {messages.map(m => (
            <Message
              key={m.id}
              content={m.content}
              role={m.role}
              timestamp={m.timestamp}
            />
          ))}
          {isLoading && <TypingIndicator />}
          {error && (
            <div className="text-center text-red-500 py-2">
              Error: {error.message}
            </div>
          )}
        </MessageList>

        <MessageInput
          onSend={sendMessage}
          disabled={isLoading}
          placeholder="Type your message..."
        />
      </ChatContainer>
    </div>
  );
}
```

## Index Export

```tsx
// components/chat/index.ts
export { ChatContainer } from './ChatContainer';
export { MessageList } from './MessageList';
export { Message } from './Message';
export { MessageInput } from './MessageInput';
export { TypingIndicator } from './TypingIndicator';
```

## Key Points

1. **Auto-scroll** - MessageList scrolls to bottom on new messages
2. **Enter to send** - MessageInput handles keyboard submit
3. **Disabled states** - Components handle loading state
4. **Tailwind styling** - Fully customizable with utility classes
5. **TypeScript** - Full type safety throughout
