# Quickstart: Agentic Task Management Chatbot

**Feature Branch**: `001-agentic-chatbot`

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL database (Neon or local)
- OpenAI API key

## Setup

### 1. Clone and checkout feature branch

```bash
git checkout 001-agentic-chatbot
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Create `backend/.env`:
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
JWT_SECRET=your-super-secret-jwt-key
OPENAI_API_KEY=sk-your-openai-api-key
```

### 4. Database Migration

The application automatically creates tables on startup via SQLModel.

```bash
# Start backend (tables created automatically)
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

## Usage

1. Open http://localhost:3000 in your browser
2. Register/login to your account
3. Click the chat bubble in the bottom-right corner
4. Start chatting with the AI assistant

### Example Commands

```
"Add a task to buy groceries"
"What tasks do I have?"
"Show me pending tasks"
"Mark task 5 as done"
"Delete the groceries task"
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/chat` | Send message to AI | Requires JWT |
| `GET /api/conversations` | List conversations | Requires JWT |
| `GET /api/conversations/{id}` | Get conversation | Requires JWT |
| `DELETE /api/conversations/{id}` | Delete conversation | Requires JWT |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                             │
│  ┌─────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │ ChatWidget  │──│ ChatProvider    │──│ API Client     │  │
│  │ (floating)  │  │ (React Context) │  │ (lib/api.ts)   │  │
│  └─────────────┘  └─────────────────┘  └────────────────┘  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP + JWT
┌──────────────────────────────▼──────────────────────────────┐
│                        Backend                              │
│  ┌─────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │ Chat Router │──│ Agent Service   │──│ Function Tools │  │
│  │ /api/chat   │  │ (OpenAI SDK)    │  │ (task CRUD)    │  │
│  └─────────────┘  └─────────────────┘  └────────────────┘  │
│         │                                      │           │
│  ┌──────▼──────────────────────────────────────▼───────┐   │
│  │                    PostgreSQL                        │   │
│  │  users | tasks | conversations | messages            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Manual Testing
1. Create a user account
2. Create some tasks via the existing todo UI
3. Open chat widget and ask "What tasks do I have?"
4. Verify AI lists your tasks correctly

## Troubleshooting

### "AI service timeout"
- Check OPENAI_API_KEY is valid
- Verify network connectivity to OpenAI API
- Check backend logs for detailed error

### "Conversation not found"
- Ensure you're logged in
- Verify JWT token is being sent in Authorization header
- Check that conversation belongs to your user

### Widget not appearing
- Check browser console for JavaScript errors
- Verify ChatProvider wraps your layout
- Ensure you're on a page that includes the layout

## Next Steps

After setup, run `/sp.tasks` to generate implementation tasks.
