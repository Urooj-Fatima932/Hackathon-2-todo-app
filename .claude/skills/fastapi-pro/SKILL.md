---
name: fastapi-pro
description: |
  Generates production-grade FastAPI endpoints, schemas, and project structures.
  This skill should be used when users want to create new FastAPI endpoints, define
  Pydantic schemas, set up projects, or add authentication/dependencies. Builds
  type-safe, documented APIs following FastAPI best practices.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash, Skill
---

# FastAPI Pro

Generate production-grade FastAPI endpoints, schemas, and project structures.

## What This Skill Does

- Generates FastAPI endpoints (CRUD, nested resources, custom actions)
- Creates Pydantic v2 schemas (request/response, validation, nested models)
- Sets up project structure with best practices
- Adds authentication and authorization patterns (JWT, OAuth2, API keys, RBAC)
- Configures middleware, dependencies, and exception handlers
- Generates async database integrations with SQLAlchemy 2.0
- Creates tests with pytest-asyncio

## What This Skill Does NOT Do

- Deploy FastAPI applications
- Manage infrastructure or containers
- Migrate from other frameworks
- Handle real-time WebSocket features

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing endpoint patterns, project structure, alembic setup, db models |
| **Conversation** | User's specific requirements, entity relationships, auth needs |
| **Skill References** | FastAPI patterns from `references/` (validation, dependencies, errors) |
| **User Guidelines** | Project conventions, naming patterns, team standards |

---

## Clarifications (Ask User)

Ask before generating:

1. **What entities/resources?** - What models/tables need endpoints?
2. **Relationships?** - One-to-many, many-to-many between entities?
3. **Authentication?** - JWT, OAuth2, API keys, or none?
4. **Database?** - SQLAlchemy async/sync, PostgreSQL/SQLite?
5. **Special requirements?** - Pagination, filtering, file uploads, caching?

---

## Generation Process

```
Gather context → Analyze existing patterns → Generate files → Validate output
```

### Step 1: Analyze Existing Project

Check for existing patterns using Glob and Grep:

```
# Find routers
Glob: **/routers/*.py, **/api/**/*.py

# Find models
Grep: "class.*Base\)|DeclarativeBase" in *.py

# Find auth patterns
Grep: "OAuth2|JWT|Depends.*get_current" in *.py

# Check project structure
Glob: **/app/**/*.py, **/src/**/*.py
```

### Step 2: Generate Based on Pattern

| Existing Pattern | Generation Approach |
|------------------|---------------------|
| Router-based (`routers/*.py`) | Add new router file |
| Module-based (`api/v1/*.py`) | Add to appropriate module |
| Flat structure | Create routers/ directory |
| No project | Use `scripts/init_project.py` |

### Step 3: Create Files

Generate in this order:

1. **Model** (`models/{entity}.py`) - If new entity
   - SQLAlchemy model with relationships
   - Timestamps, indexes

2. **Schemas** (`schemas/{entity}.py`)
   - Pydantic models for request/response
   - Validation rules, ConfigDict

3. **Repository** (`repositories/{entity}_repository.py`)
   - CRUD operations
   - Query methods

4. **Router** (`routers/{entity}.py`)
   - CRUD endpoints
   - Dependencies, error handling

5. **Update api.py or main.py**
   - Include new router
   - Add tags for docs

---

## Output Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py              # App factory, lifespan
│   ├── config.py            # Pydantic Settings
│   ├── database.py          # Async SQLAlchemy setup
│   ├── dependencies.py      # Common dependencies
│   ├── models/
│   │   └── {entity}.py      # SQLAlchemy models
│   ├── schemas/
│   │   └── {entity}.py      # Pydantic schemas
│   ├── repositories/
│   │   └── {entity}_repository.py
│   ├── routers/
│   │   ├── api.py           # Router aggregator
│   │   └── {entity}.py      # Endpoints
│   └── services/            # Business logic
├── tests/
│   ├── conftest.py          # Fixtures
│   └── test_{entity}.py     # Tests
└── alembic/                 # Migrations
```

---

## Standards

Follow patterns in `references/`:

| Standard | Implementation |
|----------|----------------|
| **Types** | Full type hints with `Annotated` |
| **Validation** | `Field()` with constraints, descriptions |
| **Errors** | Custom HTTPException classes |
| **Dependencies** | Type aliases with `Annotated[..., Depends()]` |
| **Async** | `async def` + `AsyncSession` for all new code |
| **Docs** | Docstrings on endpoints, Field descriptions |

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/patterns.md` | Project structure, app factory, CRUD routers |
| `references/schemas.md` | Pydantic v2 patterns, validators |
| `references/validation.md` | Field validation, query/path params |
| `references/errors.md` | Exception handling, status codes |
| `references/auth.md` | JWT, OAuth2, RBAC, API keys |
| `references/security.md` | Protected routes, CORS |
| `references/async.md` | Async patterns, lifespan, background tasks |
| `references/database.md` | SQLAlchemy async, repository pattern |
| `references/middleware.md` | Request ID, logging, rate limiting |
| `references/pagination.md` | Offset/cursor pagination, filtering |
| `references/config.md` | Pydantic Settings, environment config |
| `references/testing.md` | pytest-asyncio, fixtures, test patterns |
| `references/dependencies.md` | Dependency injection patterns, type aliases |
| `references/file-uploads.md` | File upload, S3, streaming, image processing |

---

## Scripts

| Script | Usage |
|--------|-------|
| `scripts/init_project.py` | Initialize new FastAPI project structure |
| `scripts/generate_crud.py` | Generate CRUD for an entity |

### Initialize Project
```bash
python scripts/init_project.py my_api --async --auth
```

### Generate CRUD
```bash
python scripts/generate_crud.py item --fields "name:str,price:float" --auth
```

---

## Common Patterns Quick Reference

### Endpoint with Dependencies
```python
@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: Annotated[int, Path(gt=0)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ItemResponse:
    ...
```

### Schema with Validation
```python
class ItemCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: Annotated[str, Field(min_length=1, max_length=200)]
    price: Annotated[float, Field(gt=0)]
```

### Custom Exception
```python
class NotFoundException(HTTPException):
    def __init__(self, resource: str, id: int):
        super().__init__(
            status_code=404,
            detail=f"{resource} {id} not found"
        )
```

### Repository Method
```python
async def get(self, id: int) -> Item | None:
    result = await self.db.execute(
        select(Item).where(Item.id == id)
    )
    return result.scalar_one_or_none()
```

---

## Checklist

Before completing, verify:

- [ ] All endpoints have response_model
- [ ] All path/query params have validation
- [ ] Proper status codes (201 for create, 204 for delete)
- [ ] Error handling with HTTPException
- [ ] Type hints on all functions
- [ ] Docstrings on endpoints
- [ ] Tests for happy path and errors
- [ ] Router included in api.py/main.py
