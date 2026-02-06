#!/usr/bin/env python3
"""
Generate CRUD router, schema, and repository for an entity.

Usage:
    python generate_crud.py <entity_name> [--fields name:str,price:float] [--auth]
"""

import argparse
import re
from pathlib import Path
from typing import List, Tuple


def parse_fields(fields_str: str) -> List[Tuple[str, str]]:
    """Parse field definitions like 'name:str,price:float'."""
    if not fields_str:
        return [("name", "str")]
    fields = []
    for field in fields_str.split(","):
        name, type_ = field.strip().split(":")
        fields.append((name.strip(), type_.strip()))
    return fields


def to_pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return "".join(word.capitalize() for word in name.split("_"))


def to_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def generate_schema(entity: str, fields: List[Tuple[str, str]]) -> str:
    """Generate Pydantic schemas."""
    pascal = to_pascal_case(entity)

    field_defs = []
    update_field_defs = []
    for name, type_ in fields:
        field_defs.append(f"    {name}: {type_}")
        update_field_defs.append(f"    {name}: {type_} | None = None")

    return f'''"""Schemas for {entity}."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class {pascal}Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)
{chr(10).join(field_defs)}

class {pascal}Create({pascal}Base):
    pass

class {pascal}Update(BaseModel):
    model_config = ConfigDict(from_attributes=True)
{chr(10).join(update_field_defs)}

class {pascal}Response({pascal}Base):
    id: int
    created_at: datetime
    updated_at: datetime
'''


def generate_model(entity: str, fields: List[Tuple[str, str]]) -> str:
    """Generate SQLAlchemy model."""
    pascal = to_pascal_case(entity)
    table_name = to_snake_case(entity) + "s"

    type_map = {
        "str": ("String(255)", "str"),
        "int": ("Integer", "int"),
        "float": ("Float", "float"),
        "bool": ("Boolean", "bool"),
        "datetime": ("DateTime(timezone=True)", "datetime"),
    }

    field_defs = []
    for name, type_ in fields:
        sql_type, py_type = type_map.get(type_, ("String(255)", "str"))
        field_defs.append(f"    {name}: Mapped[{py_type}] = mapped_column({sql_type})")

    return f'''"""Model for {entity}."""
from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class {pascal}(Base):
    __tablename__ = "{table_name}"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
{chr(10).join(field_defs)}
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
'''


def generate_repository(entity: str) -> str:
    """Generate repository class."""
    pascal = to_pascal_case(entity)
    snake = to_snake_case(entity)

    return f'''"""Repository for {entity}."""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.{snake} import {pascal}
from app.schemas.{snake} import {pascal}Create, {pascal}Update

class {pascal}Repository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, {snake}_id: int) -> {pascal} | None:
        result = await self.db.execute(
            select({pascal}).where({pascal}.id == {snake}_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[{pascal}]:
        result = await self.db.execute(
            select({pascal})
            .offset(skip)
            .limit(limit)
            .order_by({pascal}.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, data: {pascal}Create) -> {pascal}:
        obj = {pascal}(**data.model_dump())
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: {pascal}, data: {pascal}Update) -> {pascal}:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(obj, field, value)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: {pascal}) -> None:
        await self.db.delete(obj)
        await self.db.flush()

    async def count(self) -> int:
        result = await self.db.execute(select(func.count({pascal}.id)))
        return result.scalar() or 0
'''


def generate_router(entity: str, with_auth: bool = False) -> str:
    """Generate FastAPI router."""
    pascal = to_pascal_case(entity)
    snake = to_snake_case(entity)
    plural = snake + "s"

    auth_import = ""
    auth_dep = ""
    if with_auth:
        auth_import = "from app.dependencies import CurrentUser"
        auth_dep = ", current_user: CurrentUser"

    return f'''"""Router for {entity}."""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repositories.{snake}_repository import {pascal}Repository
from app.schemas.{snake} import {pascal}Create, {pascal}Update, {pascal}Response
{auth_import}

router = APIRouter(prefix="/{plural}", tags=["{plural}"])

async def get_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> {pascal}Repository:
    return {pascal}Repository(db)

RepoDep = Annotated[{pascal}Repository, Depends(get_repository)]

@router.get("/", response_model=list[{pascal}Response])
async def list_{plural}(
    repo: RepoDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20{auth_dep}
) -> list[{pascal}Response]:
    """List all {plural}."""
    return await repo.get_all(skip=skip, limit=limit)

@router.post("/", response_model={pascal}Response, status_code=status.HTTP_201_CREATED)
async def create_{snake}(
    data: {pascal}Create,
    repo: RepoDep{auth_dep}
) -> {pascal}Response:
    """Create a new {snake}."""
    return await repo.create(data)

@router.get("/{{{snake}_id}}", response_model={pascal}Response)
async def get_{snake}(
    {snake}_id: Annotated[int, Path(gt=0)],
    repo: RepoDep{auth_dep}
) -> {pascal}Response:
    """Get a {snake} by ID."""
    obj = await repo.get({snake}_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{pascal} not found"
        )
    return obj

@router.patch("/{{{snake}_id}}", response_model={pascal}Response)
async def update_{snake}(
    {snake}_id: Annotated[int, Path(gt=0)],
    data: {pascal}Update,
    repo: RepoDep{auth_dep}
) -> {pascal}Response:
    """Update a {snake}."""
    obj = await repo.get({snake}_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{pascal} not found"
        )
    return await repo.update(obj, data)

@router.delete("/{{{snake}_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{snake}(
    {snake}_id: Annotated[int, Path(gt=0)],
    repo: RepoDep{auth_dep}
) -> None:
    """Delete a {snake}."""
    obj = await repo.get({snake}_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{pascal} not found"
        )
    await repo.delete(obj)
'''


def main():
    parser = argparse.ArgumentParser(description="Generate CRUD for entity")
    parser.add_argument("entity", help="Entity name (e.g., item, user_profile)")
    parser.add_argument("--fields", help="Field definitions (name:str,price:float)")
    parser.add_argument("--auth", action="store_true", help="Add authentication")
    parser.add_argument("--output", "-o", help="Output directory", default=".")
    args = parser.parse_args()

    entity = args.entity.lower()
    snake = to_snake_case(entity)
    fields = parse_fields(args.fields)
    output = Path(args.output)

    # Generate files
    files = {
        f"schemas/{snake}.py": generate_schema(entity, fields),
        f"models/{snake}.py": generate_model(entity, fields),
        f"repositories/{snake}_repository.py": generate_repository(entity),
        f"routers/{snake}.py": generate_router(entity, args.auth),
    }

    for path, content in files.items():
        file_path = output / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        print(f"Created: {file_path}")

    print(f"""
CRUD generated for '{entity}'!

Add to your router aggregator (app/routers/api.py):
    from app.routers.{snake} import router as {snake}_router
    router.include_router({snake}_router)

Run migration:
    alembic revision --autogenerate -m "Add {entity}"
    alembic upgrade head
""")


if __name__ == "__main__":
    main()
