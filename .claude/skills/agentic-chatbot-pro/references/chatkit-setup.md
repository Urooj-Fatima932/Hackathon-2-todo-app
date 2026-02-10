# ChatKit Setup

## Overview

OpenAI ChatKit provides a hosted chat UI that connects to your backend.

## Domain Allowlist Configuration (Required)

Before deploying, configure OpenAI's domain allowlist:

### Step 1: Deploy Frontend

Get your production URL:
- Vercel: `https://your-app.vercel.app`
- GitHub Pages: `https://username.github.io/repo-name`
- Custom: `https://yourdomain.com`

### Step 2: Add Domain to OpenAI

1. Navigate to: https://platform.openai.com/settings/organization/security/domain-allowlist
2. Click "Add domain"
3. Enter your frontend URL (without trailing slash)
4. Save changes

### Step 3: Get Domain Key

After adding domain, OpenAI provides a domain key.

### Step 4: Configure Environment

```bash
# frontend/.env.local
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here
NEXT_PUBLIC_API_URL=https://your-backend.com
```

**Note**: `localhost` typically works without domain allowlist for development.

---

## Frontend Implementation

### Next.js App Router Setup

```tsx
// frontend/src/app/page.tsx
'use client';

import { useState } from 'react';

export default function ChatPage() {
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'user123', // Get from auth
          message: input,
        }),
      });

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4">
      <div className="flex-1 overflow-y-auto space-y-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`p-3 rounded-lg ${
              msg.role === 'user'
                ? 'bg-blue-100 ml-auto max-w-[80%]'
                : 'bg-gray-100 mr-auto max-w-[80%]'
            }`}
          >
            {msg.content}
          </div>
        ))}
        {loading && (
          <div className="bg-gray-100 p-3 rounded-lg mr-auto">
            Thinking...
          </div>
        )}
      </div>

      <div className="flex gap-2 mt-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
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

---

## With OpenAI ChatKit Component

If using the official ChatKit React component:

```tsx
// frontend/src/app/page.tsx
'use client';

import { ChatKit } from '@openai/chatkit';

export default function ChatPage() {
  return (
    <ChatKit
      domainKey={process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY}
      apiEndpoint={`${process.env.NEXT_PUBLIC_API_URL}/api/chat`}
      userId="user123"
    />
  );
}
```

---

## Backend Chat Endpoint

```python
# backend/app/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.chat_service import ChatService
from app.config import settings

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    user_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db, mcp_url=settings.mcp_url)

    try:
        response = await service.process_message(
            user_id=request.user_id,
            message=request.message,
        )
        return ChatResponse(
            response=response,
            user_id=request.user_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## CORS Configuration

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Package.json

```json
{
  "name": "chatbot-frontend",
  "version": "0.1.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.0.0",
    "autoprefixer": "^10.0.0",
    "postcss": "^8.0.0"
  }
}
```

---

## Key Points

1. **Domain allowlist required** for hosted ChatKit in production
2. **localhost works** without allowlist for development
3. **CORS must be configured** on backend for frontend domain
4. **Environment variables** keep keys out of code
5. **user_id required** in every request for multi-tenancy
