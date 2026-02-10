# Chatscope Chat UI Kit

## Installation

```bash
npm install @chatscope/chat-ui-kit-react @chatscope/chat-ui-kit-styles
# or
yarn add @chatscope/chat-ui-kit-react @chatscope/chat-ui-kit-styles
```

## Core Components

| Component | Purpose |
|-----------|---------|
| `MainContainer` | Root wrapper for chat app |
| `ChatContainer` | Houses conversation elements |
| `MessageList` | Scrollable message container |
| `Message` | Individual message display |
| `MessageInput` | Text input with send button |
| `TypingIndicator` | Shows typing state |
| `Avatar` | User/bot avatar |
| `ConversationHeader` | Chat header with info |

## Basic Setup

```tsx
import styles from '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator,
} from '@chatscope/chat-ui-kit-react';

export function ChatUI() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = async (text: string) => {
    const userMsg = {
      message: text,
      sender: 'user',
      direction: 'outgoing',
    };
    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);

    // Call API
    const response = await fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message: text }),
    });
    const data = await response.json();

    setMessages(prev => [...prev, {
      message: data.response,
      sender: 'assistant',
      direction: 'incoming',
    }]);
    setIsTyping(false);
  };

  return (
    <div style={{ position: 'relative', height: '500px' }}>
      <MainContainer>
        <ChatContainer>
          <MessageList
            typingIndicator={isTyping ? <TypingIndicator content="Thinking..." /> : null}
          >
            {messages.map((msg, i) => (
              <Message
                key={i}
                model={{
                  message: msg.message,
                  sender: msg.sender,
                  direction: msg.direction,
                  position: 'single',
                }}
              />
            ))}
          </MessageList>
          <MessageInput
            placeholder="Type message here..."
            onSend={handleSend}
            attachButton={false}
          />
        </ChatContainer>
      </MainContainer>
    </div>
  );
}
```

## Message Model Properties

```typescript
interface MessageModel {
  message: string;           // Message content
  sender: string;            // Sender name
  direction: 'incoming' | 'outgoing';
  position: 'single' | 'first' | 'normal' | 'last';
  sentTime?: string;         // Timestamp
  type?: 'text' | 'html' | 'image' | 'custom';
}
```

## With Avatar

```tsx
<Message
  model={{
    message: 'Hello!',
    sender: 'Assistant',
    direction: 'incoming',
    position: 'single',
  }}
  avatarPosition="tl"
>
  <Avatar src="/bot-avatar.png" name="Bot" />
</Message>
```

## With Header

```tsx
<ChatContainer>
  <ConversationHeader>
    <Avatar src="/bot-avatar.png" name="Assistant" />
    <ConversationHeader.Content userName="AI Assistant" info="Online" />
  </ConversationHeader>
  <MessageList>
    {/* messages */}
  </MessageList>
  <MessageInput />
</ChatContainer>
```

## Custom Styling

Override default styles:

```css
/* Custom message colors */
.cs-message--incoming .cs-message__content {
  background-color: #f0f0f0;
}

.cs-message--outgoing .cs-message__content {
  background-color: #0084ff;
  color: white;
}

/* Custom input styling */
.cs-message-input__content-editor {
  background-color: #f5f5f5;
}
```

## With Sidebar (Multi-conversation)

```tsx
<MainContainer>
  <Sidebar position="left">
    <ConversationList>
      <Conversation name="Chat 1" lastSenderName="Bot" info="Hello!" />
      <Conversation name="Chat 2" lastSenderName="Bot" info="Hi there!" />
    </ConversationList>
  </Sidebar>
  <ChatContainer>
    {/* chat content */}
  </ChatContainer>
</MainContainer>
```

## Key Points

1. **Container height required** - Set explicit height on parent div
2. **Import styles** - Must import CSS from chat-ui-kit-styles
3. **Message direction** - 'incoming' for bot, 'outgoing' for user
4. **Position prop** - Use 'single' for standalone, others for grouped
5. **TypeScript support** - Types available since v1.9.3
