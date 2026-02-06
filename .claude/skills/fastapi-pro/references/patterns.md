# FastAPI Patterns

## Project Structure

```
my_project/
├── app/
│   ├── __init__.py
│   ├── main.py              # App factory and lifespan
│   ├── config.py            # Pydantic Settings
│   ├── dependencies.py      # Common dependencies
│   ├── database.py          # Database setup
│   ├── routers/             # API route handlers
│   │   ├── __init__.py
│   │   ├── api.py           # Router aggregator
│   │   └── items.py         # Resource routers
│   ├── models/              # Pydantic schemas
│   │   ├── __init__.py
│   │   └── schemas.py
│   └── services/            # Business logic
│       ├── __init__.py
│       └── item_service.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_routers/
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## App Factory Pattern

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import Settings
from app.routers import api

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_database()
    yield
    await close_database()

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
    )
    app.include_router(api.router, prefix="/api/v1")
    return app

app = create_application()
```

## Pydantic v2 Schemas

```python
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: int
```

## CRUD Router Pattern

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated, List

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=List[ItemResponse])
async def list_items(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20
) -> List[ItemResponse]:
    ...

@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item(item_in: ItemCreate) -> ItemResponse:
    ...

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: Annotated[int, Path(gt=0)]) -> ItemResponse:
    ...

@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item_in: ItemUpdate) -> ItemResponse:
    ...

@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int) -> None:
    ...
```

## Dependency Injection

```python
from typing import Annotated
from fastapi import Depends

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

DbDep = Annotated[AsyncSession, Depends(get_db)]

@router.get("/")
async def list_items(db: DbDep) -> List[Item]:
    ...
```
