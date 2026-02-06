# FastAPI Async Patterns

## Database Session Lifecycle

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session
```

## Lifespan Events

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_database()
    await init_redis()
    yield
    # Shutdown
    await close_database()
    await close_redis()

app = FastAPI(lifespan=lifespan)
```

## Background Tasks

```python
from fastapi import BackgroundTasks

async def send_email_async(email: str, message: str):
    # Async email sending
    pass

@app.post("/users/")
async def create_user(
    user: UserCreate,
    background_tasks: BackgroundTasks
) -> UserResponse:
    user = await create_user_db(user)
    background_tasks.add_task(send_email_async, user.email, "Welcome!")
    return user
```

## Concurrent Operations

```python
import asyncio

async def fetch_multiple_items(ids: list[int]) -> list[Item]:
    tasks = [fetch_item(id) for id in ids]
    return await asyncio.gather(*tasks, return_exceptions=True)

# With timeout
try:
    result = await asyncio.wait_for(slow_operation(), timeout=5.0)
except asyncio.TimeoutError:
    raise HTTPException(status_code=504, detail="Operation timeout")
```

## Async Generators (Streaming)

```python
from fastapi.responses import StreamingResponse

async def generate_log_stream():
    for i in range(100):
        yield f"data: Log line {i}\n\n"
        await asyncio.sleep(0.1)

@app.get("/logs/stream")
async def stream_logs() -> StreamingResponse:
    return StreamingResponse(
        generate_log_stream(),
        media_type="text/event-stream"
    )
```

## Async Context Managers for Resources

```python
class RedisCache:
    def __init__(self):
        self.client = None

    async def __aenter__(self):
        self.client = await aioredis.create_redis_pool("redis://localhost")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.client.close()
        await self.client.wait_closed()

    async def get(self, key: str) -> str | None:
        return await self.client.get(key, encoding="utf-8")

# Usage
async with RedisCache() as cache:
    value = await cache.get("mykey")
```

## Async Rate Limiting

```python
import asyncio
from functools import wraps

def rate_limit(requests: int, window: int):
    """Simple in-memory rate limiter"""
    clients: dict[str, list[float]] = {}

    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host
            now = asyncio.get_event_loop().time()

            if client_ip not in clients:
                clients[client_ip] = []

            # Remove old requests
            clients[client_ip] = [t for t in clients[client_ip] if now - t < window]

            if len(clients[client_ip]) >= requests:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            clients[client_ip].append(now)
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
```
