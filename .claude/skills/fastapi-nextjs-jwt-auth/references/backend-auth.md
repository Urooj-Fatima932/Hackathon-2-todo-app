# Backend Authentication Implementation

Complete FastAPI JWT authentication implementation.

## File Structure

```
backend/
├── app/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── password.py      # bcrypt hashing
│   │   ├── jwt.py           # JWT utilities
│   │   └── dependencies.py  # get_current_user
│   ├── routes/
│   │   └── auth.py          # register/login endpoints
│   ├── models.py            # User model
│   ├── schemas.py           # Auth schemas
│   ├── config.py            # JWT settings
│   └── main.py              # Register router
└── .env
```

---

## 1. Password Hashing (`app/auth/password.py`)

**CRITICAL: Use bcrypt directly, NOT passlib**

```python
"""Password hashing utilities using bcrypt directly."""
import bcrypt

# Bcrypt has a 72-byte limit for passwords
BCRYPT_MAX_LENGTH = 72


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    Truncates to 72 bytes to avoid bcrypt limit error.
    """
    password_bytes = password.encode('utf-8')[:BCRYPT_MAX_LENGTH]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against its hash."""
    password_bytes = plain_password.encode('utf-8')[:BCRYPT_MAX_LENGTH]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)
```

---

## 2. JWT Utilities (`app/auth/jwt.py`)

```python
"""JWT token verification utilities."""
import jwt
from fastapi import HTTPException, status
from app.config import settings


def verify_jwt_token(token: str) -> dict:
    """
    Verify JWT token and return decoded payload.

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
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
    """Extract user identity from JWT payload."""
    user_id = payload.get("sub")
    email = payload.get("email")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier"
        )

    return {"user_id": user_id, "email": email}
```

---

## 3. Auth Dependencies (`app/auth/dependencies.py`)

```python
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

    Usage:
        @app.get("/api/tasks")
        async def get_tasks(user: User = Depends(get_current_user)):
            return get_tasks_for_user(user.id)
    """
    token = credentials.credentials
    payload = verify_jwt_token(token)
    user_info = extract_user_from_token(payload)

    statement = select(User).where(User.id == user_info["user_id"])
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# Type alias for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
```

---

## 4. Auth Routes (`app/routes/auth.py`)

```python
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


def create_access_token(data: dict) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """Register a new user account."""
    # Check if email exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        logger.warning(f"Registration attempt with existing email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
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

    token = create_access_token({"sub": new_user.id, "email": new_user.email})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(new_user))


@router.post("/login", response_model=TokenResponse)
async def login_user(
    credentials: UserLogin,
    session: Session = Depends(get_session)
):
    """Login user with email and password."""
    statement = select(User).where(User.email == credentials.email)
    user = session.exec(statement).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.warning(f"Failed login attempt for email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    logger.info(f"User logged in: {user.email}")

    token = create_access_token({"sub": user.id, "email": user.email})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))
```

---

## 5. Schemas (`app/schemas.py`)

```python
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


# User Schemas
class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    name: Optional[str] = Field(default=None, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response."""
    id: str
    email: str
    name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

---

## 6. User Model (`app/models.py`)

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import uuid


class User(SQLModel, table=True):
    """User model for authentication."""
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str = Field()
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Add relationships as needed
    # tasks: list["Task"] = Relationship(back_populates="user")
```

---

## 7. Config (`app/config.py`)

```python
from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # CORS
    cors_origins: str = '["http://localhost:3000"]'

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.cors_origins)

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
```

---

## 8. Main App (`app/main.py`)

Add auth router:

```python
from app.routes import auth

# Include routers
app.include_router(auth.router)
```

---

## 9. Protected Routes Example

```python
from app.auth.dependencies import CurrentUser

@router.get("/api/tasks")
async def list_tasks(
    current_user: CurrentUser,
    session: Session = Depends(get_session)
):
    """List tasks for authenticated user only."""
    query = select(Task).where(Task.user_id == current_user.id)
    tasks = session.exec(query).all()
    return tasks
```
