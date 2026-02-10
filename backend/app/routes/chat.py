"""Chat API routes for AI-powered task management.

Implements the 9-step STATELESS conversation flow:
┌─────────────────────────────────────────────────────────────────────────────┐
│  CONVERSATION FLOW (Stateless Request Cycle)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Receive user message                                                    │
│  2. Fetch conversation history from database                                │
│  3. Build message array for agent (history + new message)                   │
│  4. Store user message in database                                          │
│  5. Run agent with MCP tools                                                │
│  6. Agent invokes appropriate MCP tool(s)                                   │
│  7. Store assistant response in database                                    │
│  8. Return response to client                                               │
│  9. Server holds NO state (ready for next request)                          │
└─────────────────────────────────────────────────────────────────────────────┘

Key Design Principles:
- State is NEVER held in memory between requests
- All conversation state is persisted to and loaded from database
- Each request is self-contained and independently processable
- Enables horizontal scaling (any server can handle any request)
"""
import asyncio
from datetime import datetime
from typing import Annotated
from sqlmodel import Session, select

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_session
from app.auth.dependencies import CurrentUser
from app.models import Conversation, Message
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ToolCall,
    ConversationListResponse,
    ConversationSummary,
    ConversationDetailResponse,
    MessageResponse,
)
from app.agent.agent import run_agent

router = APIRouter(prefix="/api", tags=["Chat"])

# Constants per spec
MAX_HISTORY_MESSAGES = 20  # FR-027
AI_TIMEOUT_SECONDS = 30   # FR-022


@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)]
):
    """Send a message to the AI assistant and receive a response.

    Implements the 9-step stateless flow:
    - Creates new conversation if conversation_id not provided
    - Loads last 20 messages for context
    - Runs AI agent with task management tools
    - Returns response with tool calls made

    Args:
        request: ChatRequest with message and optional conversation_id
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        ChatResponse with AI response, conversation_id, and tool_calls

    Raises:
        HTTPException 400: Message validation failed
        HTTPException 404: Conversation not found or not owned
        HTTPException 504: AI service timeout
    """
    # ┌─────────────────────────────────────────────────────────────────────┐
    # │  STEP 1: Receive user message                                       │
    # └─────────────────────────────────────────────────────────────────────┘
    # (Already done via FastAPI request validation)

    # ┌─────────────────────────────────────────────────────────────────────┐
    # │  STEP 2: Fetch conversation history from database                   │
    # └─────────────────────────────────────────────────────────────────────┘
    conversation = None
    if request.conversation_id:
        # Verify ownership (return 404 not 403 per FR-029)
        conversation = session.exec(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id
            )
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=current_user.id,
            title=None,  # Will be set from first message
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # Fetch conversation history (last 20 messages per FR-027)
    history_messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.desc())
        .limit(MAX_HISTORY_MESSAGES)
    ).all()

    # Reverse to get chronological order (oldest first)
    history_messages = list(reversed(history_messages))

    # ┌─────────────────────────────────────────────────────────────────────┐
    # │  STEP 3: Build message array for agent (history + new message)      │
    # └─────────────────────────────────────────────────────────────────────┘
    # Convert to OpenAI message format for structured conversation state
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in history_messages
    ]

    # ┌─────────────────────────────────────────────────────────────────────┐
    # │  STEP 4: Store user message in database                             │
    # └─────────────────────────────────────────────────────────────────────┘
    # Store BEFORE calling AI for durability (message persists even if AI fails)
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
        created_at=datetime.utcnow()
    )
    session.add(user_message)
    session.commit()

    # Auto-generate title from first user message (T044)
    if conversation.title is None:
        conversation.title = request.message[:100]  # Truncate to 100 chars
        session.add(conversation)
        session.commit()

    # ┌─────────────────────────────────────────────────────────────────────┐
    # │  STEPS 5-6: Run agent with MCP tools                                │
    # └─────────────────────────────────────────────────────────────────────┘
    # Agent receives full history + new message, invokes tools as needed
    try:
        response_text, tool_calls_raw = await asyncio.wait_for(
            run_agent(
                user_id=current_user.id,
                db=session,
                message=request.message,
                history=history
            ),
            timeout=AI_TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI service timeout. Please try again."
        )
    except Exception as e:
        # Log error but return friendly message per SC-007
        print(f"Agent error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="I'm having trouble processing your request. Please try again."
        )

    # ┌─────────────────────────────────────────────────────────────────────┐
    # │  STEP 7: Store assistant response in database                       │
    # └─────────────────────────────────────────────────────────────────────┘
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
        created_at=datetime.utcnow()
    )
    session.add(assistant_message)

    # Update conversation timestamp (FR-010)
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    session.commit()

    # ┌─────────────────────────────────────────────────────────────────────┐
    # │  STEP 8: Return response to client                                  │
    # └─────────────────────────────────────────────────────────────────────┘
    tool_calls = [
        ToolCall(
            tool=tc.get("tool", ""),
            args=tc.get("args", {}),
            result=tc.get("result", {})
        )
        for tc in tool_calls_raw
    ]

    # ┌─────────────────────────────────────────────────────────────────────┐
    # │  STEP 9: Server holds NO state (ready for next request)             │
    # └─────────────────────────────────────────────────────────────────────┘
    # All state has been persisted to database. Server memory is clean.
    # Any server instance can handle the next request for this conversation.
    return ChatResponse(
        response=response_text,
        conversation_id=conversation.id,
        tool_calls=tool_calls
    )


@router.get("/conversations", response_model=ConversationListResponse)
def list_conversations(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)]
):
    """List all conversations for the current user.

    Returns conversations ordered by most recently updated first.

    Args:
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        ConversationListResponse with list of conversations and total count
    """
    conversations = session.exec(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    ).all()

    return ConversationListResponse(
        conversations=[
            ConversationSummary(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at
            )
            for conv in conversations
        ],
        total=len(conversations)
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: str,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)]
):
    """Get a specific conversation with its messages.

    Returns last 20 messages ordered by created_at ascending (oldest first).

    Args:
        conversation_id: UUID of the conversation
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        ConversationDetailResponse with conversation and messages

    Raises:
        HTTPException 404: Conversation not found or not owned
    """
    # Verify ownership (return 404 not 403 per FR-029)
    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get last 20 messages ordered by created_at ASC
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(MAX_HISTORY_MESSAGES)
    ).all()

    # Reverse to get chronological order
    messages = list(reversed(messages))

    return ConversationDetailResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at
            )
            for msg in messages
        ]
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: str,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)]
):
    """Delete a conversation and all its messages.

    Messages are cascade deleted via the relationship.

    Args:
        conversation_id: UUID of the conversation
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        204 No Content on success

    Raises:
        HTTPException 404: Conversation not found or not owned
    """
    # Verify ownership (return 404 not 403 per FR-029)
    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Delete conversation (messages cascade delete via relationship)
    session.delete(conversation)
    session.commit()

    return None
