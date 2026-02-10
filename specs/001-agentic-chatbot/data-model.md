# Data Model: Agentic Task Management Chatbot

**Feature Branch**: `001-agentic-chatbot`
**Created**: 2026-02-09

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────────┐       ┌─────────────────┐
│     User        │       │    Conversation     │       │    Message      │
├─────────────────┤       ├─────────────────────┤       ├─────────────────┤
│ id (PK)         │──1:N──│ id (PK)             │──1:N──│ id (PK)         │
│ email           │       │ user_id (FK)        │       │ conversation_id │
│ hashed_password │       │ title               │       │ role            │
│ name            │       │ created_at          │       │ content         │
│ created_at      │       │ updated_at          │       │ created_at      │
│ updated_at      │       └─────────────────────┘       └─────────────────┘
├─────────────────┤
│     Task        │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ title           │
│ description     │
│ is_completed    │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

## Entities

### User (Existing)

User model for authentication and resource ownership.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | string | PK, UUID | uuid4() | Unique identifier |
| email | string | UNIQUE, NOT NULL, indexed | - | User email address |
| hashed_password | string | NOT NULL | - | Bcrypt hashed password |
| name | string | nullable | NULL | Optional display name |
| created_at | datetime | NOT NULL | utcnow() | Account creation time |
| updated_at | datetime | NOT NULL | utcnow() | Last update time |

**Relationships**:
- User 1:N Task (user owns tasks)
- User 1:N Conversation (user owns conversations)

---

### Task (Existing)

User's todo task items.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | string | PK, UUID | uuid4() | Unique identifier |
| user_id | string | FK → users.id, NOT NULL, indexed | - | Owner |
| title | string | NOT NULL, 1-200 chars | - | Task title |
| description | string | nullable, max 1000 chars | NULL | Optional details |
| is_completed | boolean | NOT NULL, indexed | false | Completion status |
| created_at | datetime | NOT NULL | utcnow() | Creation time |
| updated_at | datetime | NOT NULL | utcnow() | Last update time |

**Indexes**:
- `user_id` - Fast lookup by owner
- `is_completed` - Filter by status

---

### Conversation (NEW)

Represents a chat thread between user and AI assistant.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | string | PK, UUID | uuid4() | Unique identifier |
| user_id | string | FK → users.id, NOT NULL, indexed | - | Owner |
| title | string | nullable, max 100 chars | NULL | Auto-generated from first message |
| created_at | datetime | NOT NULL | utcnow() | Creation time |
| updated_at | datetime | NOT NULL | utcnow() | Last message time |

**Relationships**:
- Conversation N:1 User (conversation belongs to user)
- Conversation 1:N Message (conversation has messages)

**Cascade Behavior**:
- ON DELETE User → CASCADE (delete all user's conversations)

**Indexes**:
- `user_id` - Fast lookup by owner

**SQLModel Definition**:
```python
class Conversation(SQLModel, table=True):
    """Conversation model - chat thread between user and AI."""
    __tablename__ = "conversations"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

---

### Message (NEW)

Individual message within a conversation.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | string | PK, UUID | uuid4() | Unique identifier |
| conversation_id | string | FK → conversations.id, NOT NULL, indexed | - | Parent conversation |
| role | string | NOT NULL, enum: 'user', 'assistant' | - | Message sender type |
| content | text | NOT NULL, 1-10000 chars | - | Message text |
| created_at | datetime | NOT NULL | utcnow() | Send time |

**Relationships**:
- Message N:1 Conversation (message belongs to conversation)

**Cascade Behavior**:
- ON DELETE Conversation → CASCADE (delete all conversation's messages)

**Indexes**:
- `conversation_id` - Fast lookup by conversation
- Composite index: `(conversation_id, created_at)` - Efficient message ordering

**SQLModel Definition**:
```python
class Message(SQLModel, table=True):
    """Message model - single message in a conversation."""
    __tablename__ = "messages"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", index=True)
    role: str = Field(...)  # 'user' or 'assistant'
    content: str = Field(min_length=1, max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
```

---

## Validation Rules

### Conversation
- `title`: If provided, must be 1-100 characters
- `user_id`: Must reference existing user

### Message
- `role`: Must be exactly 'user' or 'assistant'
- `content`: Must be 1-10000 characters (non-empty)
- `conversation_id`: Must reference existing conversation

### Task (existing, used by agent tools)
- `title`: 1-200 characters (from FR-012)
- `description`: Max 1000 characters if provided (from FR-012)

---

## State Transitions

### Conversation Lifecycle
```
Created → Active → Deleted
   │         │
   │         └── Updated (on new message)
   │
   └── Title generated (from first user message)
```

### Message Lifecycle
```
Created → Persisted (immutable)
```

Messages are immutable once created (no edit functionality per spec).

---

## Queries

### Load Conversation History (per request)
```sql
SELECT id, role, content, created_at
FROM messages
WHERE conversation_id = :id
ORDER BY created_at DESC
LIMIT 20;
-- Then reverse in application for chronological order
```

### List User Conversations
```sql
SELECT id, title, created_at, updated_at
FROM conversations
WHERE user_id = :user_id
ORDER BY updated_at DESC;
```

### Check Conversation Ownership
```sql
SELECT id FROM conversations
WHERE id = :conversation_id AND user_id = :user_id;
-- Returns NULL if not owned by user
```

---

## Migration Notes

### New Tables
1. Create `conversations` table
2. Create `messages` table with FK to conversations
3. Add index on `messages(conversation_id, created_at)`

### Existing Tables
- `users`: Add relationship to conversations (no schema change)
- `tasks`: No changes required

### Rollback Strategy
1. Drop `messages` table (cascade from conversations)
2. Drop `conversations` table
