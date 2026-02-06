# FastAPI Error Handling Patterns

## HTTP Exceptions

```python
from fastapi import HTTPException, status

# Basic 404
if not item:
    raise HTTPException(status_code=404, detail="Item not found")

# With headers
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
```

## Custom Exception Classes

```python
from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    def __init__(self, resource: str, resource_id: str | int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with id '{resource_id}' not found"
        )

class DuplicateException(HTTPException):
    def __init__(self, field: str, value: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{field} '{value}' already exists"
        )

class PermissionDeniedException(HTTPException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

# Usage
if not user:
    raise NotFoundException("User", user_id)

if email_exists:
    raise DuplicateException("email", email)
```

## Exception Handler Registration

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc), "type": "validation_error"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
```

## Structured Error Responses

```python
from pydantic import BaseModel
from typing import Any

class ErrorDetail(BaseModel):
    field: str | None = None
    message: str
    type: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: list[ErrorDetail] | None = None
    request_id: str | None = None

# Validation error format
{
    "error": "validation_error",
    "message": "Request validation failed",
    "details": [
        {"field": "email", "message": "Invalid email format", "type": "value_error"},
        {"field": "password", "message": "Password too short", "type": "min_length"}
    ]
}
```

## Service Layer Errors

```python
class ServiceError(Exception):
    """Base service error"""
    pass

class ValidationError(ServiceError):
    """Validation failed"""
    pass

class DatabaseError(ServiceError):
    """Database operation failed"""
    pass

# In router
try:
    result = await service.create_item(data)
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))
except DatabaseError:
    raise HTTPException(status_code=500, detail="Database error")
```

## Error Status Codes Reference

| Code | Usage |
|------|-------|
| 400 | Bad request, validation errors |
| 401 | Unauthorized, missing/invalid auth |
| 403 | Forbidden, permission denied |
| 404 | Resource not found |
| 409 | Conflict, duplicate resource |
| 422 | Unprocessable entity (validation) |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
