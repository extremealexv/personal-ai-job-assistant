# API Development Guide

**Personal AI Job Assistant - Backend Development**

This guide provides information for developers working on the backend API.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Database Management](#database-management)
- [Testing](#testing)
- [Code Style](#code-style)
- [Debugging](#debugging)
- [Performance](#performance)

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Poetry (dependency management)
- Git

### Initial Setup

```bash
# Clone repository
git clone https://github.com/extremealexv/personal-ai-job-assistant.git
cd personal-ai-job-assistant/src/backend

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### Environment Variables

Required variables in `.env`:

```bash
# Application
APP_NAME=Personal AI Job Assistant
APP_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_job_assistant

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# AI Provider
OPENAI_API_KEY=your-openai-key

# Email (optional for local dev)
GMAIL_CLIENT_ID=your-client-id
GMAIL_CLIENT_SECRET=your-client-secret

# Logging
LOG_LEVEL=INFO
```

### Database Setup

```bash
# Create database
createdb ai_job_assistant

# Run migrations
alembic upgrade head

# (Optional) Seed database with sample data
python scripts/seed_db.py
```

### Run Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

Visit:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Project Structure

```
src/backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py              # API router aggregator
│   │       └── endpoints/
│   │           └── health.py       # Health check endpoints
│   ├── core/
│   │   ├── error_handlers.py       # Exception handlers
│   │   ├── exceptions.py           # Custom exceptions
│   │   ├── logging.py              # Logging configuration
│   │   └── middleware.py           # Request middleware
│   ├── models/
│   │   ├── base.py                 # Base model class
│   │   ├── user.py                 # User model
│   │   ├── resume.py               # Resume models
│   │   ├── job.py                  # Job posting models
│   │   └── ...                     # Other models
│   ├── schemas/
│   │   ├── user.py                 # User Pydantic schemas
│   │   ├── resume.py               # Resume schemas
│   │   └── ...                     # Other schemas
│   ├── services/
│   │   ├── ai/                     # AI service integrations
│   │   ├── email/                  # Email integrations
│   │   └── ...                     # Other services
│   ├── config.py                   # Application configuration
│   ├── db.py                       # Database connection
│   └── main.py                     # FastAPI application
├── alembic/                        # Database migrations
├── tests/
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_health.py              # Health endpoint tests
│   └── ...                         # Other tests
├── scripts/
│   ├── seed_db.py                  # Database seeding
│   └── setup_test_db.py            # Test database setup
├── alembic.ini                     # Alembic configuration
├── pytest.ini                      # Pytest configuration
├── pyproject.toml                  # Poetry dependencies
└── README.md                       # Backend documentation
```

---

## Development Workflow

### Creating New Features

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/add-resume-parser
   ```

2. **Create database models** (if needed):
   ```python
   # app/models/my_model.py
   from app.models.base import Base
   from sqlalchemy.orm import Mapped, mapped_column
   
   class MyModel(Base):
       __tablename__ = "my_models"
       
       name: Mapped[str] = mapped_column(String(255))
   ```

3. **Create migration:**
   ```bash
   alembic revision --autogenerate -m "Add my_model table"
   alembic upgrade head
   ```

4. **Create Pydantic schemas:**
   ```python
   # app/schemas/my_schema.py
   from pydantic import BaseModel, Field
   
   class MyModelCreate(BaseModel):
       name: str = Field(..., min_length=1, max_length=255)
   
   class MyModelResponse(BaseModel):
       id: UUID
       name: str
       created_at: datetime
       
       class Config:
           from_attributes = True
   ```

5. **Create API endpoint:**
   ```python
   # app/api/v1/endpoints/my_endpoint.py
   from fastapi import APIRouter, Depends
   
   router = APIRouter()
   
   @router.post("/", response_model=MyModelResponse)
   async def create_item(
       data: MyModelCreate,
       db: AsyncSession = Depends(get_db)
   ):
       # Implementation
       pass
   ```

6. **Register router:**
   ```python
   # app/api/v1/api.py
   from app.api.v1.endpoints import my_endpoint
   
   api_router.include_router(
       my_endpoint.router,
       prefix="/my-items",
       tags=["My Items"]
   )
   ```

7. **Write tests:**
   ```python
   # tests/test_my_endpoint.py
   import pytest
   from httpx import AsyncClient
   
   @pytest.mark.asyncio
   async def test_create_item(async_client: AsyncClient):
       response = await async_client.post(
           "/api/v1/my-items/",
           json={"name": "Test Item"}
       )
       assert response.status_code == 201
       assert response.json()["name"] == "Test Item"
   ```

8. **Run tests:**
   ```bash
   pytest tests/test_my_endpoint.py -v
   ```

9. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat(api): add my_items endpoint"
   git push origin feature/add-resume-parser
   ```

---

## Database Management

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Review generated migration file
nano alembic/versions/xxxxx_description_of_changes.py

# Apply migration
alembic upgrade head
```

### Rollback Migrations

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Show migration history
alembic history
```

### Manual Migrations

```bash
# Create empty migration
alembic revision -m "Manual migration"

# Edit migration file
nano alembic/versions/xxxxx_manual_migration.py
```

Example migration:

```python
def upgrade() -> None:
    op.create_table(
        'my_table',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('my_table')
```

### Database Seeding

```bash
# Seed development database
python scripts/seed_db.py

# Seed with specific data
python scripts/seed_db.py --users 10 --jobs 50
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_health.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests in parallel
pytest -n auto
```

### Test Markers

```python
@pytest.mark.unit          # Fast, isolated unit tests
@pytest.mark.integration   # Tests with database/API
@pytest.mark.slow          # Slow-running tests
@pytest.mark.asyncio       # Async tests
```

### Writing Tests

**Unit Test Example:**
```python
import pytest
from app.models.user import User

@pytest.mark.unit
def test_user_to_dict():
    user = User(email="test@example.com", password_hash="hashed")
    user_dict = user.to_dict()
    
    assert "email" in user_dict
    assert "password_hash" not in user_dict
```

**Integration Test Example:**
```python
import pytest
from httpx import AsyncClient

@pytest.mark.integration
async def test_create_job_posting(
    async_client: AsyncClient,
    auth_headers: dict
):
    response = await async_client.post(
        "/api/v1/jobs/",
        json={
            "company_name": "TechCorp",
            "job_title": "Backend Engineer",
            "job_url": "https://example.com/job"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["company_name"] == "TechCorp"
```

### Test Fixtures

Available fixtures (see `tests/conftest.py`):

- `test_engine`: SQLAlchemy async engine
- `db_session`: Database session with automatic rollback
- `client`: Synchronous TestClient
- `async_client`: Asynchronous HTTP client
- `test_user`: Factory for creating test users
- `auth_headers`: Authentication headers with JWT token

---

## Code Style

### Formatting

```bash
# Format with Black
black .

# Check formatting
black --check .
```

### Linting

```bash
# Lint with Ruff
ruff check .

# Fix auto-fixable issues
ruff check . --fix
```

### Type Checking

```bash
# Check types with mypy
mypy app/
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Code Conventions

**Naming:**
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`

**Type Hints:**
```python
def get_user(user_id: UUID) -> Optional[User]:
    """Get user by ID."""
    pass

async def create_resume(
    data: ResumeCreate,
    db: AsyncSession
) -> Resume:
    """Create new resume."""
    pass
```

**Docstrings (Google Style):**
```python
def tailor_resume(resume: Resume, job: JobPosting) -> Resume:
    """Tailor resume for specific job posting.
    
    Args:
        resume: Master resume to tailor
        job: Target job posting
        
    Returns:
        Tailored resume version
        
    Raises:
        ValueError: If resume or job is invalid
    """
    pass
```

---

## Debugging

### VS Code Launch Configuration

`.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": false
    }
  ]
}
```

### Logging

**Configure log level:**
```python
# config.py
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

**Use logger:**
```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.exception("Exception message")  # Includes traceback
```

### Database Query Logging

Enable SQLAlchemy query logging:

```python
# config.py
SQLALCHEMY_ECHO = True  # Logs all SQL queries
```

### Request Debugging

FastAPI automatically includes request IDs in headers:

```python
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

Access in endpoint:
```python
from fastapi import Request

@router.get("/")
async def my_endpoint(request: Request):
    request_id = request.state.request_id
    logger.info(f"Processing request {request_id}")
```

---

## Performance

### Database Query Optimization

**Use eager loading:**
```python
from sqlalchemy.orm import selectinload

stmt = (
    select(User)
    .options(selectinload(User.master_resumes))
    .where(User.id == user_id)
)
result = await db.execute(stmt)
user = result.scalar_one_or_none()
```

**Use indexes:**
```python
# In model definition
class JobPosting(Base):
    company_name: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(index=True)
```

**Pagination:**
```python
@router.get("/jobs/", response_model=PaginatedJobResponse)
async def list_jobs(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(JobPosting).offset(skip).limit(limit)
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    return {"items": jobs, "skip": skip, "limit": limit}
```

### Caching

**Use Redis for caching (future):**
```python
from redis import asyncio as aioredis

@router.get("/expensive-operation/")
async def expensive_operation(redis: Redis = Depends(get_redis)):
    cached = await redis.get("cache_key")
    if cached:
        return json.loads(cached)
    
    result = await perform_expensive_operation()
    await redis.setex("cache_key", 3600, json.dumps(result))
    return result
```

### Async Operations

**Use async where possible:**
```python
# Good - async
async def fetch_multiple_users(user_ids: list[UUID], db: AsyncSession):
    stmt = select(User).where(User.id.in_(user_ids))
    result = await db.execute(stmt)
    return result.scalars().all()

# Bad - synchronous in async context
def sync_operation():
    time.sleep(1)  # Blocks event loop
```

### Monitoring

**Health checks:**
- Endpoint: `/api/v1/health`
- Database connectivity check
- Response time monitoring

**Metrics (future):**
- Prometheus integration
- Request duration
- Error rates
- Database query times

---

## Troubleshooting

### Common Issues

**Database connection errors:**
```bash
# Check database is running
pg_isready -h localhost -p 5432

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL
```

**Migration conflicts:**
```bash
# Check current revision
alembic current

# View migration history
alembic history

# Stamp database with current revision
alembic stamp head
```

**Import errors:**
```bash
# Ensure virtual environment is activated
poetry shell

# Reinstall dependencies
poetry install

# Check Python path
python -c "import sys; print(sys.path)"
```

**Test failures:**
```bash
# Drop and recreate test database
dropdb ai_job_assistant_test
createdb ai_job_assistant_test

# Clear pytest cache
pytest --cache-clear

# Run tests with verbose output
pytest -vv --tb=short
```

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)

---

## Contributing

See [CONTRIBUTING.md](../../../CONTRIBUTING.md) for contribution guidelines.
