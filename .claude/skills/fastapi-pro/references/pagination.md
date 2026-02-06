# FastAPI Pagination & Filtering Patterns

## Basic Pagination

```python
from typing import Annotated, Generic, TypeVar
from pydantic import BaseModel, Field
from fastapi import Query

T = TypeVar("T")

class PaginationParams(BaseModel):
    skip: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1, le=100)] = 20

async def get_pagination(
    skip: Annotated[int, Query(ge=0, description="Records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Max records")] = 20,
) -> PaginationParams:
    return PaginationParams(skip=skip, limit=limit)

PaginationDep = Annotated[PaginationParams, Depends(get_pagination)]

@router.get("/items/")
async def list_items(pagination: PaginationDep):
    items = await repo.get_all(
        skip=pagination.skip,
        limit=pagination.limit
    )
    return items
```

## Paginated Response Model

```python
from typing import Generic, TypeVar, Sequence
from pydantic import BaseModel

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    skip: int
    limit: int
    has_more: bool

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        total: int,
        skip: int,
        limit: int
    ) -> "PaginatedResponse[T]":
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=skip + len(items) < total
        )

# Usage
@router.get("/items/", response_model=PaginatedResponse[ItemResponse])
async def list_items(pagination: PaginationDep, repo: ItemRepoDep):
    items = await repo.get_all(skip=pagination.skip, limit=pagination.limit)
    total = await repo.count()
    return PaginatedResponse.create(
        items=items,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit
    )
```

## Cursor-Based Pagination

```python
from datetime import datetime
from typing import Annotated
from pydantic import BaseModel
import base64

class CursorParams(BaseModel):
    cursor: str | None = None
    limit: int = 20

def encode_cursor(item_id: int, created_at: datetime) -> str:
    data = f"{item_id}:{created_at.isoformat()}"
    return base64.urlsafe_b64encode(data.encode()).decode()

def decode_cursor(cursor: str) -> tuple[int, datetime]:
    data = base64.urlsafe_b64decode(cursor.encode()).decode()
    item_id, created_at = data.split(":")
    return int(item_id), datetime.fromisoformat(created_at)

class CursorPaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: str | None
    has_more: bool

@router.get("/items/cursor/")
async def list_items_cursor(
    cursor: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    repo: ItemRepoDep = Depends(),
):
    if cursor:
        after_id, after_created = decode_cursor(cursor)
        items = await repo.get_after(after_id, after_created, limit + 1)
    else:
        items = await repo.get_all(limit=limit + 1)

    has_more = len(items) > limit
    items = items[:limit]

    next_cursor = None
    if has_more and items:
        last = items[-1]
        next_cursor = encode_cursor(last.id, last.created_at)

    return CursorPaginatedResponse(
        items=items,
        next_cursor=next_cursor,
        has_more=has_more
    )
```

## Filtering

```python
from enum import Enum
from typing import Annotated
from pydantic import BaseModel
from fastapi import Query

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class ItemFilter(BaseModel):
    search: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    category: str | None = None
    is_active: bool | None = None
    sort_by: str = "created_at"
    sort_order: SortOrder = SortOrder.DESC

async def get_item_filter(
    search: Annotated[str | None, Query(max_length=100)] = None,
    min_price: Annotated[float | None, Query(ge=0)] = None,
    max_price: Annotated[float | None, Query(ge=0)] = None,
    category: Annotated[str | None, Query()] = None,
    is_active: Annotated[bool | None, Query()] = None,
    sort_by: Annotated[str, Query(pattern="^(name|price|created_at)$")] = "created_at",
    sort_order: Annotated[SortOrder, Query()] = SortOrder.DESC,
) -> ItemFilter:
    return ItemFilter(
        search=search,
        min_price=min_price,
        max_price=max_price,
        category=category,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )

ItemFilterDep = Annotated[ItemFilter, Depends(get_item_filter)]
```

## Repository with Filtering

```python
from sqlalchemy import select, func, or_

class ItemRepository:
    async def get_filtered(
        self,
        filter: ItemFilter,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Item]:
        query = select(Item)

        # Apply filters
        if filter.search:
            query = query.where(
                or_(
                    Item.name.ilike(f"%{filter.search}%"),
                    Item.description.ilike(f"%{filter.search}%")
                )
            )
        if filter.min_price is not None:
            query = query.where(Item.price >= filter.min_price)
        if filter.max_price is not None:
            query = query.where(Item.price <= filter.max_price)
        if filter.category:
            query = query.where(Item.category == filter.category)
        if filter.is_active is not None:
            query = query.where(Item.is_active == filter.is_active)

        # Apply sorting
        sort_column = getattr(Item, filter.sort_by)
        if filter.sort_order == SortOrder.DESC:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_filtered(self, filter: ItemFilter) -> int:
        query = select(func.count(Item.id))
        # Apply same filters (without pagination/sorting)
        if filter.search:
            query = query.where(
                or_(
                    Item.name.ilike(f"%{filter.search}%"),
                    Item.description.ilike(f"%{filter.search}%")
                )
            )
        # ... other filters
        result = await self.db.execute(query)
        return result.scalar() or 0
```

## Combined Endpoint

```python
@router.get("/items/", response_model=PaginatedResponse[ItemResponse])
async def list_items(
    pagination: PaginationDep,
    filter: ItemFilterDep,
    repo: ItemRepoDep,
):
    items = await repo.get_filtered(
        filter=filter,
        skip=pagination.skip,
        limit=pagination.limit,
    )
    total = await repo.count_filtered(filter)

    return PaginatedResponse.create(
        items=items,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )
```

## Link Header Pagination (REST Standard)

```python
from fastapi import Response
from urllib.parse import urlencode

@router.get("/items/")
async def list_items(
    request: Request,
    response: Response,
    pagination: PaginationDep,
    repo: ItemRepoDep,
):
    items = await repo.get_all(skip=pagination.skip, limit=pagination.limit)
    total = await repo.count()

    # Build Link header
    base_url = str(request.url).split("?")[0]
    links = []

    if pagination.skip > 0:
        prev_skip = max(0, pagination.skip - pagination.limit)
        links.append(f'<{base_url}?skip={prev_skip}&limit={pagination.limit}>; rel="prev"')

    if pagination.skip + len(items) < total:
        next_skip = pagination.skip + pagination.limit
        links.append(f'<{base_url}?skip={next_skip}&limit={pagination.limit}>; rel="next"')

    if links:
        response.headers["Link"] = ", ".join(links)

    response.headers["X-Total-Count"] = str(total)

    return items
```
