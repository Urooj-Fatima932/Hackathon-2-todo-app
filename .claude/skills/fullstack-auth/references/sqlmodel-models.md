# SQLModel Models for Better Auth

These models are compatible with Better Auth's database schema, allowing the FastAPI backend to share the same database as the Next.js frontend.

## Project Structure

```
app/
├── models/
│   ├── __init__.py
│   ├── user.py           # User model
│   ├── session.py        # Session model
│   ├── account.py        # OAuth account model
│   └── verification.py   # Verification token model
```

## User Model

### models/user.py

```python
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
import uuid

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.account import Account


class UserBase(SQLModel):
    """Base user fields shared between models."""

    email: str = Field(unique=True, index=True, max_length=255)
    name: str | None = Field(default=None, max_length=255)
    email_verified: bool = Field(default=False)
    image: str | None = Field(default=None, max_length=512)


class User(UserBase, table=True):
    """User database model compatible with Better Auth."""

    __tablename__ = "user"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )

    # Password for email/password auth (hashed)
    hashed_password: str | None = Field(default=None, max_length=255)

    # Optional custom fields
    role: str = Field(default="user", max_length=50)
    is_active: bool = Field(default=True)

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    sessions: list["Session"] = Relationship(back_populates="user")
    accounts: list["Account"] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    """Schema for creating a new user."""

    email: str
    name: str | None = None
    password: str | None = None  # For email/password auth


class UserUpdate(SQLModel):
    """Schema for updating a user."""

    email: str | None = None
    name: str | None = None
    image: str | None = None
    role: str | None = None


class UserResponse(UserBase):
    """Schema for user response (public)."""

    id: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserPrivate(UserResponse):
    """Schema for user response (private/self)."""

    is_active: bool
    updated_at: datetime

    model_config = {"from_attributes": True}
```

## Session Model

### models/session.py

```python
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
import uuid

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User


class SessionBase(SQLModel):
    """Base session fields."""

    token: str = Field(unique=True, index=True, max_length=255)
    expires_at: datetime
    ip_address: str | None = Field(default=None, max_length=45)
    user_agent: str | None = Field(default=None, max_length=512)


class Session(SessionBase, table=True):
    """Session database model compatible with Better Auth."""

    __tablename__ = "session"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )

    user_id: str = Field(foreign_key="user.id", index=True)

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user: Optional["User"] = Relationship(back_populates="sessions")

    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.now(timezone.utc) > self.expires_at


class SessionCreate(SQLModel):
    """Schema for creating a session."""

    user_id: str
    token: str
    expires_at: datetime
    ip_address: str | None = None
    user_agent: str | None = None


class SessionResponse(SessionBase):
    """Schema for session response."""

    id: str
    user_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
```

## Account Model (OAuth)

### models/account.py

```python
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
import uuid

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User


class AccountBase(SQLModel):
    """Base account fields for OAuth providers."""

    provider_id: str = Field(max_length=50, index=True)  # github, google, etc.
    account_id: str = Field(max_length=255)  # Provider's user ID
    scope: str | None = Field(default=None, max_length=512)


class Account(AccountBase, table=True):
    """Account database model for OAuth providers, compatible with Better Auth."""

    __tablename__ = "account"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )

    user_id: str = Field(foreign_key="user.id", index=True)

    # OAuth tokens
    access_token: str | None = Field(default=None, max_length=2048)
    refresh_token: str | None = Field(default=None, max_length=2048)
    id_token: str | None = Field(default=None, max_length=4096)

    # Token expiry
    access_token_expires_at: datetime | None = None
    refresh_token_expires_at: datetime | None = None

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user: Optional["User"] = Relationship(back_populates="accounts")

    # Unique constraint on provider + account_id
    __table_args__ = (
        {"unique_together": [("provider_id", "account_id")]},
    )


class AccountCreate(SQLModel):
    """Schema for creating an account."""

    user_id: str
    provider_id: str
    account_id: str
    access_token: str | None = None
    refresh_token: str | None = None
    scope: str | None = None


class AccountResponse(AccountBase):
    """Schema for account response."""

    id: str
    user_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
```

## Verification Token Model

### models/verification.py

```python
from datetime import datetime, timezone
import uuid

from sqlmodel import SQLModel, Field


class VerificationBase(SQLModel):
    """Base verification token fields."""

    identifier: str = Field(max_length=255, index=True)  # Usually email
    value: str = Field(max_length=255)  # The token value


class Verification(VerificationBase, table=True):
    """Verification token model compatible with Better Auth."""

    __tablename__ = "verification"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )

    expires_at: datetime

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.now(timezone.utc) > self.expires_at


class VerificationCreate(SQLModel):
    """Schema for creating a verification token."""

    identifier: str
    value: str
    expires_at: datetime
```

## Models __init__.py

### models/__init__.py

```python
from app.models.user import (
    User,
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserPrivate,
)
from app.models.session import (
    Session,
    SessionBase,
    SessionCreate,
    SessionResponse,
)
from app.models.account import (
    Account,
    AccountBase,
    AccountCreate,
    AccountResponse,
)
from app.models.verification import (
    Verification,
    VerificationBase,
    VerificationCreate,
)

__all__ = [
    # User
    "User",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserPrivate",
    # Session
    "Session",
    "SessionBase",
    "SessionCreate",
    "SessionResponse",
    # Account
    "Account",
    "AccountBase",
    "AccountCreate",
    "AccountResponse",
    # Verification
    "Verification",
    "VerificationBase",
    "VerificationCreate",
]
```

## Extended User Model Examples

### Adding Custom Fields

```python
class User(UserBase, table=True):
    __tablename__ = "user"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    # Standard fields
    hashed_password: str | None = None
    email_verified: bool = Field(default=False)

    # Custom fields
    role: str = Field(default="user")  # user, admin, moderator
    bio: str | None = Field(default=None, max_length=500)
    website: str | None = Field(default=None, max_length=255)
    location: str | None = Field(default=None, max_length=100)

    # Subscription/billing
    stripe_customer_id: str | None = Field(default=None, max_length=255)
    subscription_status: str | None = Field(default=None, max_length=50)

    # Preferences
    theme: str = Field(default="system")  # light, dark, system
    notifications_enabled: bool = Field(default=True)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: datetime | None = None

    # Relationships
    sessions: list["Session"] = Relationship(back_populates="user")
    accounts: list["Account"] = Relationship(back_populates="user")
```

### User with Profile

```python
# models/profile.py
class Profile(SQLModel, table=True):
    __tablename__ = "profile"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", unique=True)

    # Profile fields
    display_name: str | None = None
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = None
    cover_url: str | None = None
    website: str | None = None
    location: str | None = None
    twitter_handle: str | None = None
    github_username: str | None = None

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationship
    user: Optional["User"] = Relationship(back_populates="profile")


# Update User model
class User(UserBase, table=True):
    # ... existing fields ...
    profile: Optional["Profile"] = Relationship(back_populates="user")
```

## Query Examples

### Get User with Sessions

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

async def get_user_with_sessions(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.sessions))
    )
    return result.scalar_one_or_none()
```

### Get User by Email

```python
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
```

### Get Active Sessions for User

```python
from datetime import datetime, timezone

async def get_active_sessions(db: AsyncSession, user_id: str) -> list[Session]:
    result = await db.execute(
        select(Session)
        .where(Session.user_id == user_id)
        .where(Session.expires_at > datetime.now(timezone.utc))
    )
    return list(result.scalars().all())
```

### Invalidate All User Sessions

```python
async def invalidate_user_sessions(db: AsyncSession, user_id: str) -> int:
    result = await db.execute(
        delete(Session).where(Session.user_id == user_id)
    )
    await db.commit()
    return result.rowcount
```

### Get User's OAuth Accounts

```python
async def get_user_accounts(db: AsyncSession, user_id: str) -> list[Account]:
    result = await db.execute(
        select(Account).where(Account.user_id == user_id)
    )
    return list(result.scalars().all())
```

### Find Account by Provider

```python
async def get_account_by_provider(
    db: AsyncSession,
    provider_id: str,
    account_id: str,
) -> Account | None:
    result = await db.execute(
        select(Account)
        .where(Account.provider_id == provider_id)
        .where(Account.account_id == account_id)
    )
    return result.scalar_one_or_none()
```
