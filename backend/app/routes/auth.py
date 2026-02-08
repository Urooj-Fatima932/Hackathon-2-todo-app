"""Authentication routes for user registration and login."""
import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.models import User
from app.auth.password import hash_password, verify_password
from app.database import get_session
from app.config import settings
import logging

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """
    Register a new user account.

    Args:
        user_data: User registration data (email, password, optional name)
        session: Database session

    Returns:
        TokenResponse with JWT token and user information

    Raises:
        HTTPException 400: If email already registered
    """
    # Check if email already exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        logger.warning(f"Registration attempt with existing email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_pw = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pw,
        name=user_data.name
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    logger.info(f"New user registered: {new_user.email}")

    # Generate JWT token
    token = create_access_token({"sub": new_user.id, "email": new_user.email})

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    credentials: UserLogin,
    session: Session = Depends(get_session)
):
    """
    Login user with email and password.

    Args:
        credentials: User login credentials (email, password)
        session: Database session

    Returns:
        TokenResponse with JWT token and user information

    Raises:
        HTTPException 401: If credentials are invalid
    """
    # Find user by email
    statement = select(User).where(User.email == credentials.email)
    user = session.exec(statement).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.warning(f"Failed login attempt for email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    logger.info(f"User logged in: {user.email}")

    # Generate JWT token
    token = create_access_token({"sub": user.id, "email": user.email})

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )


def create_access_token(data: dict) -> str:
    """
    Create JWT access token.

    Args:
        data: Payload data to encode in token

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt
