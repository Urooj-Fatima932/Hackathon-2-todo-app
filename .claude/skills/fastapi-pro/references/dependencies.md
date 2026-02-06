# FastAPI Dependency Injection Patterns

## Basic Dependencies

```python
from typing import Annotated
from fastapi import Depends, Query

# Simple dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Type alias for reuse
DbDep = Annotated[AsyncSession, Depends(get_db)]

@router.get("/items/")
async def list_items(db: DbDep):
    ...
```

## Parameterized Dependencies

```python
from fastapi import Query

def pagination_params(
    skip: Annotated[int, Query(ge=0, description="Records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Max records")] = 20,
) -> dict:
    return {"skip": skip, "limit": limit}

PaginationDep = Annotated[dict, Depends(pagination_params)]

@router.get("/items/")
async def list_items(pagination: PaginationDep):
    return await get_items(
        skip=pagination["skip"],
        limit=pagination["limit"]
    )
```

## Class-Based Dependencies

```python
from dataclasses import dataclass

@dataclass
class CommonParams:
    skip: int = 0
    limit: int = 20

class Pagination:
    def __init__(
        self,
        skip: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
    ):
        self.skip = skip
        self.limit = limit

PaginationDep = Annotated[Pagination, Depends()]

@router.get("/items/")
async def list_items(pagination: PaginationDep):
    return await get_items(skip=pagination.skip, limit=pagination.limit)
```

## Dependency with Sub-Dependencies

```python
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbDep,
) -> User:
    user = await verify_token_and_get_user(token, db)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

async def get_current_active_user(current_user: CurrentUser) -> User:
    if not current_user.is_active:
        raise HTTPException(400, "Inactive user")
    return current_user

ActiveUser = Annotated[User, Depends(get_current_active_user)]
```

## Factory Dependencies

```python
def require_role(required_role: str):
    async def role_checker(current_user: CurrentUser) -> User:
        if current_user.role != required_role:
            raise HTTPException(403, "Insufficient permissions")
        return current_user
    return role_checker

AdminUser = Annotated[User, Depends(require_role("admin"))]

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, admin: AdminUser):
    # Only admins can delete users
    ...
```

## Repository Dependencies

```python
class ItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, item_id: int) -> Item | None:
        ...

async def get_item_repository(db: DbDep) -> ItemRepository:
    return ItemRepository(db)

ItemRepoDep = Annotated[ItemRepository, Depends(get_item_repository)]

@router.get("/items/{item_id}")
async def get_item(item_id: int, repo: ItemRepoDep):
    item = await repo.get(item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    return item
```

## Service Layer Dependencies

```python
class ItemService:
    def __init__(self, repo: ItemRepository, cache: Redis):
        self.repo = repo
        self.cache = cache

    async def get_item(self, item_id: int) -> Item:
        cached = await self.cache.get(f"item:{item_id}")
        if cached:
            return Item.model_validate_json(cached)
        item = await self.repo.get(item_id)
        if item:
            await self.cache.set(f"item:{item_id}", item.model_dump_json())
        return item

async def get_item_service(
    repo: ItemRepoDep,
    cache: Annotated[Redis, Depends(get_redis)],
) -> ItemService:
    return ItemService(repo, cache)

ItemServiceDep = Annotated[ItemService, Depends(get_item_service)]
```

## Path-Based Dependencies

```python
async def get_item_by_id(
    item_id: Annotated[int, Path(gt=0)],
    repo: ItemRepoDep,
) -> Item:
    item = await repo.get(item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    return item

ItemDep = Annotated[Item, Depends(get_item_by_id)]

@router.get("/items/{item_id}")
async def get_item(item: ItemDep):
    return item

@router.patch("/items/{item_id}")
async def update_item(item: ItemDep, data: ItemUpdate):
    # Item is already fetched and validated
    ...
```

## Request Context Dependencies

```python
from fastapi import Request

async def get_request_id(request: Request) -> str:
    return request.state.request_id

RequestIdDep = Annotated[str, Depends(get_request_id)]

async def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

ClientIpDep = Annotated[str, Depends(get_client_ip)]
```

## Caching Dependency

```python
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    return Settings()

SettingsDep = Annotated[Settings, Depends(get_settings)]
```

## Background Task Dependencies

```python
from fastapi import BackgroundTasks

async def send_notification(
    background_tasks: BackgroundTasks,
    user: CurrentUser,
) -> BackgroundTasks:
    # Add common background task
    background_tasks.add_task(log_user_activity, user.id)
    return background_tasks

@router.post("/items/")
async def create_item(
    item_in: ItemCreate,
    background_tasks: Annotated[BackgroundTasks, Depends(send_notification)],
):
    ...
```

## Dependency Override for Testing

```python
# In conftest.py
async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

## Common Dependency Patterns Summary

| Pattern | Use Case |
|---------|----------|
| `Annotated[T, Depends(fn)]` | Type-safe dependency injection |
| Class with `__init__` | Dependencies with multiple parameters |
| Factory function | Parameterized dependencies |
| Sub-dependencies | Layered/chained dependencies |
| Path dependencies | Pre-fetch and validate resources |
| `lru_cache` | Singleton/cached dependencies |
