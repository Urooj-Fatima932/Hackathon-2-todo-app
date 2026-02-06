# FastAPI Validation Patterns

## Field Validation

```python
from pydantic import BaseModel, Field, EmailStr, HttpUrl, field_validator
from typing import Annotated
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")]
    password: Annotated[str, Field(min_length=8, max_length=100)]
    age: Annotated[int, Field(ge=13, le=120)]
    website: HttpUrl | None = None
    bio: Annotated[str | None, Field(max_length=500)] = None
```

## Custom Validators

```python
from pydantic import field_validator, model_validator

class UserCreate(BaseModel):
    email: str
    password: str
    password_confirm: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain an uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain a digit")
        if not any(c in "!@#$%^&*" for c in v):
            raise ValueError("Password must contain a special character")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "UserCreate":
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self
```

## Query Parameter Validation

```python
from fastapi import Query
from typing import Annotated

async def list_items(
    search: Annotated[str | None, Query(max_length=100)] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    sort_by: Annotated[str | None, Query(pattern=r"^(name|created_at|updated_at)$")] = None,
    sort_order: Annotated[str | None, Query(pattern=r"^(asc|desc)$")] = "asc"
):
    ...
```

## Path Parameter Validation

```python
from fastapi import Path
from typing import Annotated

@router.get("/{item_id}")
async def get_item(
    item_id: Annotated[int, Path(gt=0, title="Item ID", description="The ID of the item to retrieve")]
):
    ...
```

## Enum Validation

```python
from enum import Enum
from pydantic import BaseModel

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserCreate(BaseModel):
    role: UserRole = UserRole.USER

# In endpoint
async def create_user(role: Annotated[UserRole, Query()] = UserRole.USER):
    ...
```

## List Validation

```python
from pydantic import BaseModel, Field
from typing import Annotated

class BatchCreate(BaseModel):
    items: Annotated[list[str], Field(min_length=1, max_length=100)]
    tags: Annotated[list[str], Field(max_length=10)] = []

# Validate unique items
class UniqueBatchCreate(BaseModel):
    items: list[str]

    @field_validator("items")
    @classmethod
    def ensure_unique(cls, v: list[str]) -> list[str]:
        if len(v) != len(set(v)):
            raise ValueError("Items must be unique")
        return v
```
