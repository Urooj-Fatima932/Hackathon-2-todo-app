# FastAPI Database Patterns

## Async SQLAlchemy Setup

```python
# app/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

## Model Definition

```python
# app/models/item.py
from datetime import datetime
from sqlalchemy import String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str | None] = mapped_column(String(1000))
    price: Mapped[float] = mapped_column(Float)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="items")
```

## CRUD Repository Pattern

```python
# app/repositories/item_repository.py
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate

class ItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, item_id: int) -> Item | None:
        result = await self.db.execute(
            select(Item).where(Item.id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_by_owner(
        self, owner_id: int, skip: int = 0, limit: int = 20
    ) -> list[Item]:
        result = await self.db.execute(
            select(Item)
            .where(Item.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .order_by(Item.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, item_in: ItemCreate, owner_id: int) -> Item:
        item = Item(**item_in.model_dump(), owner_id=owner_id)
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def update(self, item: Item, item_in: ItemUpdate) -> Item:
        update_data = item_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def delete(self, item: Item) -> None:
        await self.db.delete(item)
        await self.db.flush()

    async def count(self, owner_id: int | None = None) -> int:
        query = select(func.count(Item.id))
        if owner_id:
            query = query.where(Item.owner_id == owner_id)
        result = await self.db.execute(query)
        return result.scalar() or 0
```

## Repository Dependency

```python
# app/dependencies.py
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repositories.item_repository import ItemRepository

async def get_item_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ItemRepository:
    return ItemRepository(db)

ItemRepoDep = Annotated[ItemRepository, Depends(get_item_repository)]
```

## Using in Endpoints

```python
# app/routers/items.py
from fastapi import APIRouter, HTTPException, status
from app.dependencies import ItemRepoDep, CurrentUser
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])

@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item(
    item_in: ItemCreate,
    repo: ItemRepoDep,
    current_user: CurrentUser,
) -> ItemResponse:
    item = await repo.create(item_in, owner_id=current_user.id)
    return item

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    repo: ItemRepoDep,
) -> ItemResponse:
    item = await repo.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

## Eager Loading Relationships

```python
from sqlalchemy.orm import selectinload, joinedload

async def get_with_owner(self, item_id: int) -> Item | None:
    result = await self.db.execute(
        select(Item)
        .options(selectinload(Item.owner))
        .where(Item.id == item_id)
    )
    return result.scalar_one_or_none()

async def get_user_with_items(self, user_id: int) -> User | None:
    result = await self.db.execute(
        select(User)
        .options(selectinload(User.items))
        .where(User.id == user_id)
    )
    return result.scalar_one_or_none()
```

## Transaction Management

```python
from sqlalchemy.ext.asyncio import AsyncSession

async def transfer_ownership(
    db: AsyncSession,
    item_id: int,
    from_user_id: int,
    to_user_id: int
) -> None:
    async with db.begin_nested():  # Savepoint
        item = await db.get(Item, item_id)
        if item.owner_id != from_user_id:
            raise ValueError("Not owner")
        item.owner_id = to_user_id
        # If this fails, only this savepoint is rolled back
```

## Alembic Migrations

```python
# alembic/env.py (async version)
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from app.database import Base
from app.config import settings

def run_migrations_offline():
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=Base.metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

## Multi-Tenancy Pattern

```python
from sqlalchemy import event

class TenantBase(Base):
    __abstract__ = True
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)

# Automatically filter by tenant
def add_tenant_filter(query, tenant_id: int):
    return query.where(Item.tenant_id == tenant_id)

# Or use row-level security in PostgreSQL
```
