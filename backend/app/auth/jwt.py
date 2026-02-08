"""JWT token verification utilities."""
import jwt
from datetime import datetime
from fastapi import HTTPException, status
from app.config import settings


def verify_jwt_token(token: str) -> dict:
    """
    Verify JWT token and return decoded payload.

    Args:
        token: JWT token string to verify

    Returns:
        Decoded JWT payload dictionary

    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )


def extract_user_from_token(payload: dict) -> dict:
    """
    Extract user identity from JWT payload.

    Args:
        payload: Decoded JWT payload dictionary

    Returns:
        Dictionary with user_id and email

    Raises:
        HTTPException: If token missing required user identifier
    """
    user_id = payload.get("sub") or payload.get("userId")
    email = payload.get("email")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier"
        )

    return {
        "user_id": user_id,
        "email": email
    }
