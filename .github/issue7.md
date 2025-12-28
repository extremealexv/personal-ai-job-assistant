### Overview

Set up the FastAPI application foundation with SQLAlchemy models, Alembic migrations, and basic API structure according to Phase 1 (Week 1-2) of the ROADMAP.

### Prerequisites

- All setup issues completed (PostgreSQL, Python, Node.js, Docker, dev tools, environment config)
- Database schema documented in `docs/architecture/DATABASE_SCHEMA.md`
- Environment variables configured in `.env` file

### Goals

Create a working FastAPI backend with:
- Database connection and ORM models
- Migration system
- Basic API endpoints
- Health checks
- CORS configuration
- Error handling

### Tasks

#### 1. FastAPI Application Structure

**Create main application file:**
```bash
# File: src/backend/app/main.py
```

**Requirements:**
- Initialize FastAPI app with metadata (title, version, description)
- Configure CORS middleware using settings from config.py
- Add global exception handlers
- Include API routers
- Add startup/shutdown event handlers for database connection

**Acceptance Criteria:**
- [ ] `app/main.py` exists and runs without errors
- [ ] Health check endpoint returns 200: `GET /health`
- [ ] API docs accessible at `/docs` and `/redoc`
- [ ] CORS properly configured for frontend origins
- [ ] Server starts with `uvicorn app.main:app --reload`

#### 2. SQLAlchemy Models

**Create database models from schema (DATABASE_SCHEMA.md):**

```bash
# File structure:
src/backend/app/models/
├── __init__.py
├── base.py           # Base model class
├── user.py           # User model
├── resume.py         # MasterResume, WorkExperience, Education, Skills, Certifications
├── job.py            # JobPosting, Application
├── prompt.py         # PromptTemplate
├── credential.py     # Credentials (encrypted)
├── email.py          # EmailThread
└── analytics.py      # AnalyticsSnapshot, InterviewEvent
```

**Requirements:**
- Implement all 15 tables as SQLAlchemy models
- Use UUID primary keys (`id: Mapped[uuid.UUID]`)
- Add proper relationships (ForeignKey, relationship())
- Implement soft deletes with `deleted_at` column
- Add `created_at` and `updated_at` with auto-update
- Use proper type hints with `Mapped[]`
- Add docstrings to all models and fields

**Acceptance Criteria:**
- [ ] All 15 models created matching DATABASE_SCHEMA.md
- [ ] UUID primary keys on all tables
- [ ] Proper foreign key relationships defined
- [ ] Soft delete support (deleted_at field)
- [ ] Timestamp fields with auto-update
- [ ] Type hints using SQLAlchemy 2.0 `Mapped[]` syntax
- [ ] All models import successfully: `from app.models import User, MasterResume, etc.`

#### 3. Database Configuration

**Create database connection module:**
```bash
# File: src/backend/app/db.py
```

**Requirements:**
- Create async SQLAlchemy engine using DATABASE_ASYNC_URL
- Create async session factory
- Implement `get_db()` dependency for FastAPI
- Add connection pooling configuration
- Add connection retry logic
- Create `init_db()` function to create tables

**Acceptance Criteria:**
- [ ] `app/db.py` created with async engine
- [ ] `get_db()` dependency works in endpoints
- [ ] Connection pooling configured
- [ ] Tables can be created with `await init_db()`
- [ ] Database connections properly closed after requests

#### 4. Alembic Migrations

**Initialize Alembic and create initial migration:**

```bash
cd src/backend
poetry run alembic init alembic
```

**Requirements:**
- Configure `alembic.ini` with database URL from env
- Update `alembic/env.py` to import models and use async engine
- Create initial migration from current schema
- Add migration helper script

**Files to create/modify:**
- `src/backend/alembic.ini` - Alembic configuration
- `src/backend/alembic/env.py` - Migration environment setup
- `src/backend/alembic/versions/XXXX_initial_schema.py` - Initial migration
- `src/backend/scripts/create_migration.sh` - Helper script

**Acceptance Criteria:**
- [ ] Alembic initialized in `src/backend/alembic/`
- [ ] `alembic.ini` configured with correct database URL
- [ ] `env.py` uses async engine and imports all models
- [ ] Initial migration created: `alembic revision --autogenerate -m "Initial schema"`
- [ ] Migration applies successfully: `alembic upgrade head`
- [ ] Migration rollback works: `alembic downgrade -1`
- [ ] All 15 tables created in database after migration

#### 5. API Router Structure

**Create API router organization:**

```bash
src/backend/app/api/
├── __init__.py
├── deps.py          # Shared dependencies
└── v1/
    ├── __init__.py
    ├── api.py       # Main v1 router
    └── endpoints/
        ├── __init__.py
        ├── health.py     # Health check
        └── users.py      # User endpoints (placeholder)
```

**Requirements:**
- Organize endpoints by version (v1)
- Create health check endpoint
- Add dependency injection utilities
- Implement error response schemas
- Add request validation

**Acceptance Criteria:**
- [ ] Router structure created
- [ ] Health endpoint: `GET /api/v1/health` returns `{"status": "ok", "version": "0.1.0"}`
- [ ] Database health check: `GET /api/v1/health/db` tests connection
- [ ] All routes prefixed with `/api/v1`
- [ ] OpenAPI docs show organized endpoints

#### 6. Pydantic Schemas

**Create request/response schemas:**

```bash
src/backend/app/schemas/
├── __init__.py
├── base.py          # Base schemas
├── user.py          # User schemas
├── resume.py        # Resume schemas
└── health.py        # Health check schemas
```

**Requirements:**
- Create base schemas with common fields (id, created_at, updated_at)
- Create request/response schemas for each model
- Add validation rules
- Use Pydantic v2 features

**Acceptance Criteria:**
- [ ] Base schemas created with UUID, timestamp handling
- [ ] Schemas separate Create/Update/Response models
- [ ] Field validation implemented (email, URL, etc.)
- [ ] Schemas match database models
- [ ] Example: `UserCreate`, `UserUpdate`, `UserResponse`

#### 7. Error Handling & Middleware

**Create error handlers and middleware:**

```bash
# Files:
src/backend/app/core/
├── __init__.py
├── exceptions.py    # Custom exceptions
└── middleware.py    # Custom middleware
```

**Requirements:**
- Custom exception classes (NotFoundError, ValidationError, etc.)
- Global exception handlers
- Request logging middleware
- Response time middleware

**Acceptance Criteria:**
- [ ] Custom exceptions defined (NotFoundError, AuthError, etc.)
- [ ] Exception handlers return proper status codes
- [ ] Exceptions return consistent JSON format
- [ ] Request ID added to all responses
- [ ] Request/response logged (excluding sensitive data)

#### 8. Testing Setup

**Create test infrastructure:**

```bash
src/backend/tests/
├── conftest.py           # Pytest fixtures
├── test_main.py          # App startup tests
├── test_db.py            # Database connection tests
└── api/
    └── test_health.py    # Health endpoint tests
```

**Requirements:**
- Test database setup/teardown fixtures
- Test client fixture
- Factory fixtures for models
- Mock external services

**Acceptance Criteria:**
- [ ] `conftest.py` with database fixtures
- [ ] Test database creates/drops automatically
- [ ] FastAPI test client fixture available
- [ ] Health endpoint tests pass
- [ ] Database connection tests pass
- [ ] Run with: `pytest tests/`

#### 9. Documentation

**Create API documentation:**

```bash
docs/api/
├── ENDPOINTS.md         # Endpoint documentation
└── DEVELOPMENT.md       # Development guide
```

**Requirements:**
- Document all endpoints with examples
- Add development workflow guide
- Document testing procedures
- Add troubleshooting section

**Acceptance Criteria:**
- [ ] All endpoints documented with curl examples
- [ ] Setup instructions for new developers
- [ ] Testing guide included
- [ ] Common errors and solutions documented

#### 10. Helper Scripts

**Create development scripts:**

```bash
src/backend/scripts/
├── run_server.sh         # Start development server
├── create_migration.sh   # Create new migration
├── run_migration.sh      # Apply migrations
└── reset_db.sh           # Drop and recreate database
```

**Acceptance Criteria:**
- [ ] Server starts with `./scripts/run_server.sh`
- [ ] Migrations easy to create and apply
- [ ] Database reset script works
- [ ] All scripts have proper error handling

### Verification Checklist

After completing all tasks:

- [ ] Server starts successfully: `uvicorn app.main:app --reload`
- [ ] Health check works: `curl http://localhost:8000/api/v1/health`
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Database connection works
- [ ] All migrations applied: `alembic current`
- [ ] All 15 tables exist in database
- [ ] Tests pass: `pytest tests/ -v`
- [ ] Test coverage > 80%: `pytest --cov=app tests/`
- [ ] No linting errors: `ruff check .`
- [ ] No type errors: `mypy app/`
- [ ] Pre-commit hooks pass

### Testing Commands

```bash
# Start server
cd src/backend
poetry run uvicorn app.main:app --reload

# Test health endpoint
curl http://localhost:8000/api/v1/health

# Check database
curl http://localhost:8000/api/v1/health/db

# View API docs
open http://localhost:8000/docs

# Run tests
poetry run pytest tests/ -v

# Check coverage
poetry run pytest --cov=app tests/

# Run migrations
poetry run alembic upgrade head

# Create new migration
poetry run alembic revision --autogenerate -m "description"
```

### Deliverables

1. Working FastAPI application with all endpoints
2. All 15 SQLAlchemy models implemented
3. Alembic migrations configured and working
4. Health check endpoints functional
5. Comprehensive test suite with >80% coverage
6. Complete API documentation
7. Development helper scripts

### Dependencies

- Issue #1: PostgreSQL installed ✅
- Issue #2: Python + Poetry installed ✅
- Issue #3: Node.js + pnpm installed ✅
- Issue #23: Dev tools configured ✅
- Issue #24: Environment configured ✅

### References

- [ROADMAP.md](../ROADMAP.md) - Phase 1, Week 1-2
- [DATABASE_SCHEMA.md](../docs/architecture/DATABASE_SCHEMA.md) - Complete schema
- [TECH_STACK.md](../docs/architecture/TECH_STACK.md) - Technology choices
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

### Estimated Effort

- **Time:** 3-5 days
- **Complexity:** Medium-High
- **Priority:** High (blocks all other backend development)

### Success Criteria

The issue is complete when:
1. FastAPI server starts and serves requests
2. All database models working with proper relationships
3. Migrations create all 15 tables successfully
4. Health checks return proper responses
5. Test suite passes with >80% coverage
6. API documentation generated and accessible
7. Pre-commit hooks pass all checks
