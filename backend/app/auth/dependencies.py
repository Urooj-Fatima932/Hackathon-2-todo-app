"""FastAPI authentication dependencies."""
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.auth.jwt import verify_jwt_token, extract_user_from_token
from app.models import User
from app.database import get_session

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[Session, Depends(get_session)]
) -> User:
    """
    FastAPI dependency to extract and verify current user from JWT token.

    Args:
        credentials: HTTP Bearer credentials from request header
        session: Database session

    Returns:
        User model instance for the authenticated user

    Raises:
        HTTPException: If token invalid or user not found

    Usage:
        @app.get("/api/tasks")
        async def get_tasks(user: User = Depends(get_current_user)):
            # user is the authenticated User object
            return await get_tasks_for_user(user.id)
    """
    token = credentials.credentials
    payload = verify_jwt_token(token)
    user_info = extract_user_from_token(payload)

    # Fetch user from database
    statement = select(User).where(User.id == user_info["user_id"])
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# Type alias for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
