# Chat State Management

Patterns for managing chat state in React applications.

## State Shape

```typescript
interface ChatState {
  messages: Message[];
  input: string;
  isLoading: boolean;
  error: Error | null;
  conversationId: string | null;
}

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
  metadata?: Record<string, unknown>;
}
```

## Simple useState Approach

For basic use cases:

```tsx
function useSimpleChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const addMessage = (message: Omit<Message, 'id' | 'timestamp'>) => {
    setMessages(prev => [...prev, {
      ...message,
      id: Date.now().toString(),
      timestamp: new Date(),
    }]);
  };

  const updateLastMessage = (content: string) => {
    setMessages(prev => {
      const updated = [...prev];
      if (updated.length > 0) {
        updated[updated.length - 1] = {
          ...updated[updated.length - 1],
          content,
        };
      }
      return updated;
    });
  };

  return { messages, input, setInput, isLoading, setIsLoading, addMessage, updateLastMessage };
}
```

## useReducer for Complex State

```tsx
type ChatAction =
  | { type: 'ADD_MESSAGE'; message: Message }
  | { type: 'UPDATE_MESSAGE'; id: string; content: string }
  | { type: 'SET_LOADING'; isLoading: boolean }
  | { type: 'SET_ERROR'; error: Error | null }
  | { type: 'SET_INPUT'; input: string }
  | { type: 'CLEAR_MESSAGES' };

function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.message] };

    case 'UPDATE_MESSAGE':
      return {
        ...state,
        messages: state.messages.map(m =>
          m.id === action.id ? { ...m, content: action.content } : m
        ),
      };

    case 'SET_LOADING':
      return { ...state, isLoading: action.isLoading };

    case 'SET_ERROR':
      return { ...state, error: action.error };

    case 'SET_INPUT':
      return { ...state, input: action.input };

    case 'CLEAR_MESSAGES':
      return { ...state, messages: [] };

    default:
      return state;
  }
}

function useChat() {
  const [state, dispatch] = useReducer(chatReducer, {
    messages: [],
    input: '',
    isLoading: false,
    error: null,
    conversationId: null,
  });

  const addMessage = (message: Omit<Message, 'id' | 'timestamp'>) => {
    dispatch({
      type: 'ADD_MESSAGE',
      message: {
        ...message,
        id: Date.now().toString(),
        timestamp: new Date(),
      },
    });
  };

  return { ...state, dispatch, addMessage };
}
```

## Context for Global Chat State

```tsx
// context/ChatContext.tsx
import { createContext, useContext, useReducer, ReactNode } from 'react';

interface ChatContextValue extends ChatState {
  dispatch: React.Dispatch<ChatAction>;
  sendMessage: (text: string) => Promise<void>;
}

const ChatContext = createContext<ChatContextValue | null>(null);

export function ChatProvider({ children, apiUrl, userId }: {
  children: ReactNode;
  apiUrl: string;
  userId: string;
}) {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  const sendMessage = async (text: string) => {
    dispatch({ type: 'SET_LOADING', isLoading: true });

    dispatch({
      type: 'ADD_MESSAGE',
      message: { id: Date.now().toString(), role: 'user', content: text, timestamp: new Date() },
    });

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, message: text }),
      });

      const data = await response.json();

      dispatch({
        type: 'ADD_MESSAGE',
        message: {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.response,
          timestamp: new Date(),
        },
      });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', error: error as Error });
    } finally {
      dispatch({ type: 'SET_LOADING', isLoading: false });
    }
  };

  return (
    <ChatContext.Provider value={{ ...state, dispatch, sendMessage }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (!context) throw new Error('useChat must be used within ChatProvider');
  return context;
}
```

## Zustand Store (Recommended for Complex Apps)

```tsx
// stores/chatStore.ts
import { create } from 'zustand';

interface ChatStore {
  messages: Message[];
  input: string;
  isLoading: boolean;
  error: Error | null;

  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  updateMessage: (id: string, content: string) => void;
  setInput: (input: string) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: Error | null) => void;
  clearMessages: () => void;

  sendMessage: (apiUrl: string, userId: string, text: string) => Promise<void>;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  messages: [],
  input: '',
  isLoading: false,
  error: null,

  addMessage: (message) => set(state => ({
    messages: [...state.messages, {
      ...message,
      id: Date.now().toString(),
      timestamp: new Date(),
    }],
  })),

  updateMessage: (id, content) => set(state => ({
    messages: state.messages.map(m =>
      m.id === id ? { ...m, content } : m
    ),
  })),

  setInput: (input) => set({ input }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  clearMessages: () => set({ messages: [] }),

  sendMessage: async (apiUrl, userId, text) => {
    const { addMessage, setLoading, setError } = get();

    setLoading(true);
    addMessage({ role: 'user', content: text });

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, message: text }),
      });

      const data = await response.json();
      addMessage({ role: 'assistant', content: data.response });
    } catch (error) {
      setError(error as Error);
    } finally {
      setLoading(false);
    }
  },
}));

// Usage
function ChatPage() {
  const { messages, isLoading, sendMessage } = useChatStore();

  return (
    // ...
  );
}
```

## Message Persistence (localStorage)

```tsx
const STORAGE_KEY = 'chat_messages';

function usePersistentChat() {
  const [messages, setMessages] = useState<Message[]>(() => {
    if (typeof window === 'undefined') return [];
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  const clearMessages = () => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  return { messages, setMessages, clearMessages };
}
```

## Optimistic Updates

```tsx
const sendMessage = async (text: string) => {
  const tempId = `temp_${Date.now()}`;

  // Optimistic add
  addMessage({
    id: tempId,
    role: 'user',
    content: text,
    status: 'sending',
  });

  try {
    const response = await fetch('/api/chat', { ... });
    const data = await response.json();

    // Update status
    updateMessage(tempId, { status: 'sent' });

    // Add response
    addMessage({ role: 'assistant', content: data.response });
  } catch (error) {
    // Mark as error
    updateMessage(tempId, { status: 'error' });
  }
};
```

## Key Points

1. **Start simple** - useState for basic apps
2. **useReducer** - When state logic is complex
3. **Context** - When multiple components need chat state
4. **Zustand** - Best for larger apps (simple API, no boilerplate)
5. **Persistence** - Consider localStorage for conversation history
6. **Optimistic updates** - Better UX with sending status
