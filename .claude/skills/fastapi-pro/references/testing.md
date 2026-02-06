# FastAPI Testing Patterns

## Test Setup with pytest

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from app.database import get_db, Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
```

## CRUD Endpoint Tests

```python
# tests/test_items.py
import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_create_item(client: AsyncClient):
    response = await client.post(
        "/api/v1/items/",
        json={"name": "Test Item", "price": 10.99}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["price"] == 10.99
    assert "id" in data

@pytest.mark.anyio
async def test_get_item(client: AsyncClient, db_session):
    # Create item first
    create_response = await client.post(
        "/api/v1/items/",
        json={"name": "Test Item", "price": 10.99}
    )
    item_id = create_response.json()["id"]

    # Get item
    response = await client.get(f"/api/v1/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["id"] == item_id

@pytest.mark.anyio
async def test_get_item_not_found(client: AsyncClient):
    response = await client.get("/api/v1/items/999")
    assert response.status_code == 404

@pytest.mark.anyio
async def test_list_items_with_pagination(client: AsyncClient):
    # Create multiple items
    for i in range(25):
        await client.post(
            "/api/v1/items/",
            json={"name": f"Item {i}", "price": i * 1.0}
        )

    # Test default pagination
    response = await client.get("/api/v1/items/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 20  # Default limit

    # Test custom pagination
    response = await client.get("/api/v1/items/?skip=10&limit=5")
    data = response.json()
    assert len(data) == 5
```

## Authentication Tests

```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_login_success(client: AsyncClient, db_session):
    # Create user first
    await client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "password": "TestPass123!"}
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "TestPass123!"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.anyio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "wrong@example.com", "password": "wrong"}
    )
    assert response.status_code == 401

@pytest.mark.anyio
async def test_protected_endpoint_without_token(client: AsyncClient):
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401

@pytest.mark.anyio
async def test_protected_endpoint_with_token(client: AsyncClient, db_session):
    # Create user and login
    await client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "password": "TestPass123!"}
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "TestPass123!"}
    )
    token = login_response.json()["access_token"]

    # Access protected endpoint
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
```

## Validation Tests

```python
@pytest.mark.anyio
async def test_create_item_validation_error(client: AsyncClient):
    # Missing required field
    response = await client.post("/api/v1/items/", json={"name": "Test"})
    assert response.status_code == 422

    # Invalid price
    response = await client.post(
        "/api/v1/items/",
        json={"name": "Test", "price": -10}
    )
    assert response.status_code == 422

@pytest.mark.anyio
async def test_invalid_query_params(client: AsyncClient):
    response = await client.get("/api/v1/items/?limit=500")  # Max is 100
    assert response.status_code == 422
```

## Factory Fixtures

```python
# tests/factories.py
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

async def create_user(
    db: AsyncSession,
    email: str = "test@example.com",
    password: str = "TestPass123!",
    **kwargs: Any
) -> User:
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        **kwargs
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def create_item(
    db: AsyncSession,
    name: str = "Test Item",
    price: float = 10.99,
    owner_id: int | None = None,
    **kwargs: Any
) -> Item:
    item = Item(name=name, price=price, owner_id=owner_id, **kwargs)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

# Usage in tests
@pytest.mark.anyio
async def test_user_items(client: AsyncClient, db_session):
    user = await create_user(db_session)
    item = await create_item(db_session, owner_id=user.id)
    # Test...
```

## Test Requirements

```
# requirements-test.txt
pytest>=7.0.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
aiosqlite>=0.19.0
factory-boy>=3.3.0
```
