# Testing Guide

## Quick Start

### 1. Set Up Test Database

Before running tests for the first time, create the test database:

#### Option A: Automated (if your DB user has CREATE DATABASE privileges)

```bash
# From src/backend directory
python scripts/setup_test_db.py
```

**Options:**
- `--drop`: Drop and recreate the test database if it already exists

```bash
python scripts/setup_test_db.py --drop
```

#### Option B: Manual (if you get "permission denied" errors)

If your database user doesn't have CREATE DATABASE privileges, create the database manually:

```bash
# Create database with superuser access
sudo -u postgres psql -c 'CREATE DATABASE "ai_job_assistant_test" OWNER jsappuser'

# Grant privileges
sudo -u postgres psql -c 'GRANT ALL PRIVILEGES ON DATABASE "ai_job_assistant_test" TO jsappuser'

# Then run the setup script to create tables
python scripts/setup_test_db.py
```

**Or use the helper script:**

```bash
bash scripts/create_test_db_manual.sh
python scripts/setup_test_db.py
```

This creates a separate `ai_job_assistant_test` database with the same schema as your development database.

### 2. Run Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_health.py

# Run specific test
pytest tests/test_health.py::test_root_endpoint

# Run tests with coverage report
pytest --cov=app --cov-report=html
```

### 3. Run Tests by Marker

Tests are organized with markers for efficient execution:

```bash
# Run only unit tests (fast)
pytest -m unit

# Run integration tests
pytest -m integration

# Run end-to-end tests
pytest -m e2e

# Exclude slow tests
pytest -m "not slow"
```

## Test Organization

```
tests/
├── conftest.py           # Pytest fixtures and configuration
├── utils.py              # Test helper functions
├── test_health.py        # Health endpoint tests
├── test_exceptions.py    # Exception handling tests
├── test_models.py        # Database model tests
├── unit/                 # Unit tests (isolated, no DB/API)
├── integration/          # Integration tests (API endpoints with DB)
└── e2e/                  # End-to-end tests (full workflows)
```

## Test Fixtures

Available fixtures in `conftest.py`:

### Database Fixtures

- **`test_engine`**: Async database engine for tests
- **`db_session`**: Async database session with automatic rollback

```python
async def test_create_user(db_session):
    user = User(email="test@example.com", password_hash="hashed")
    db_session.add(user)
    await db_session.commit()
    assert user.id is not None
```

### API Client Fixtures

- **`client`**: Synchronous FastAPI test client
- **`async_client`**: Asynchronous HTTP client

```python
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200

async def test_async_endpoint(async_client):
    response = await async_client.get("/api/v1/users")
    assert response.status_code == 200
```

### User Fixtures

- **`test_user`**: Factory fixture for creating test users

```python
async def test_user_authentication(db_session, test_user):
    user = await test_user(email="user@example.com")
    assert user.email == "user@example.com"
```

- **`auth_headers`**: Authentication headers for protected endpoints

```python
async def test_protected_endpoint(async_client, auth_headers):
    response = await async_client.get(
        "/api/v1/profile",
        headers=auth_headers
    )
    assert response.status_code == 200
```

## Writing Tests

### Unit Test Example

```python
import pytest
from app.core.exceptions import NotFoundError

@pytest.mark.unit
def test_not_found_error():
    """Test NotFoundError exception."""
    error = NotFoundError("User not found")
    assert error.status_code == 404
    assert "User not found" in str(error)
```

### Integration Test Example

```python
import pytest
from app.models.user import User

@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_user(db_session):
    """Test creating a user in the database."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        full_name="Test User"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.is_active is True
```

### API Endpoint Test Example

```python
import pytest

@pytest.mark.integration
def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
```

## Test Markers

Defined markers (see `pytest.ini`):

- `unit`: Fast, isolated tests (no database or external dependencies)
- `integration`: Tests that interact with database or API
- `e2e`: End-to-end tests of complete workflows
- `slow`: Tests that take more than 1 second

Example usage:

```python
@pytest.mark.unit
def test_fast_function():
    """A fast unit test."""
    assert 1 + 1 == 2

@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_query(db_session):
    """An integration test with database."""
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1

@pytest.mark.slow
def test_expensive_operation():
    """A slow test that processes large data."""
    # ... long-running test
```

## Coverage Reports

Generate HTML coverage report:

```bash
pytest --cov=app --cov-report=html
```

View report: Open `htmlcov/index.html` in your browser.

### Coverage Requirements

- **Minimum coverage**: 80% (enforced in CI/CD)
- Excludes: `tests/`, `__init__.py`, migrations

## Helper Functions

Available in `tests/utils.py`:

### User Helpers

```python
from tests.utils import create_test_user, get_user_by_email

async def test_user_operations(db_session):
    # Create user
    user = await create_test_user(
        db_session,
        email="test@example.com",
        full_name="Test User"
    )
    
    # Retrieve user
    found_user = await get_user_by_email(db_session, "test@example.com")
    assert found_user.id == user.id
```

### Assertion Helpers

```python
from tests.utils import assert_valid_uuid, assert_dict_contains

def test_uuid_validation():
    assert_valid_uuid("550e8400-e29b-41d4-a716-446655440000")

def test_response_structure():
    response = {"id": "123", "name": "Test", "email": "test@example.com"}
    expected = {"name": "Test", "email": "test@example.com"}
    assert_dict_contains(response, expected)
```

## Database Isolation

Each test runs in its own transaction that is rolled back after the test:

```python
@pytest.mark.asyncio
async def test_user_isolation(db_session):
    # Create user (will be rolled back after test)
    user = User(email="temp@example.com")
    db_session.add(user)
    await db_session.commit()
    
    # User will not exist in other tests
```

## Debugging Tests

### Run with Print Statements

```bash
pytest -s  # Don't capture output
```

### Run with PDB Debugger

```bash
pytest --pdb  # Drop into debugger on failure
```

### Run Single Test with Debug Output

```bash
pytest -vv -s tests/test_health.py::test_root_endpoint
```

## Troubleshooting

### Test Database Doesn't Exist

```
asyncpg.exceptions.InvalidCatalogNameError: database "ai_job_assistant_test" does not exist
```

**Solution**: Run `python scripts/setup_test_db.py`

### Connection Pool Issues

If you see connection pool errors, reset the test database:

```bash
python scripts/setup_test_db.py --drop
```

### Tests Hang or Timeout

Check for:
- Unclosed database sessions
- Infinite loops
- Missing `await` in async functions

### Import Errors

Make sure you're in the virtual environment:

```bash
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

## CI/CD Integration

Tests run automatically on:
- Push to any branch
- Pull requests
- Before deployment

Requirements:
- All tests must pass
- Coverage must be ≥ 80%
- No linting errors

## Best Practices

1. **Keep tests isolated**: Each test should be independent
2. **Use fixtures**: Reuse common setup logic
3. **Test one thing**: Each test should verify one behavior
4. **Clear names**: Test names should describe what they test
5. **Arrange-Act-Assert**: Structure tests clearly
6. **Mock external services**: Don't make real API calls in tests
7. **Fast tests**: Keep unit tests under 100ms
8. **Clean up**: Use fixtures for setup/teardown

## Example Test Session

```bash
# Set up test database (first time only)
python scripts/setup_test_db.py

# Run unit tests (fast)
pytest -m unit -v

# Run integration tests
pytest -m integration -v

# Run all tests with coverage
pytest --cov=app --cov-report=term-missing

# View HTML coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
