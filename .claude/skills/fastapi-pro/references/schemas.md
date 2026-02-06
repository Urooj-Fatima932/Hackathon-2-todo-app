# Pydantic v2 Schema Patterns

## Required Dependencies

When using Pydantic v2 with email validation, install the required package:

```bash
pip install email-validator
# or
pip install 'pydantic[email]'
```

**pyproject.toml:**
```toml
dependencies = [
    "pydantic[email]>=2.0",
    # ...
]
```

> **Common Error:** If you use `EmailStr` without `email-validator` installed:
> ```
> ImportError: email-validator is not installed, run `pip install 'pydantic[email]'`
> ```

## Base Configuration

```python
from pydantic import BaseModel, ConfigDict, Field, field_validator

class MyBaseModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
```

## CRUD Schema Pattern

```python
class ItemBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str | None = Field(None, min_length=1)
    price: float | None = Field(None, gt=0)

class ItemResponse(ItemBase):
    id: int
    created_at: datetime
```

## Validators

```python
from pydantic import field_validator, model_validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    password_confirm: str

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain a digit")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "UserCreate":
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self
```

## Annotated Types

```python
from typing import Annotated
from pydantic import Field

Username = Annotated[str, Field(min_length=3, max_length=50)]
PositiveInt = Annotated[int, Field(gt=0)]

class Product(BaseModel):
    name: Annotated[str, Field(min_length=1)]
    price: Annotated[float, Field(gt=0)]
    stock: PositiveInt
```
