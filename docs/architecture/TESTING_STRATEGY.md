# Testing Strategy & Framework Setup

**Project:** Personal AI Job Assistant  
**Date:** December 26, 2025

---

## Overview

This document outlines the testing strategy, frameworks, and workflow for ensuring code quality across all components of the Personal AI Job Assistant.

---

## Testing Philosophy

### Principles

1. **Test-Driven Development (TDD)** encouraged for new features
2. **Manual testing first** → validate functionality → create automated test
3. **80% code coverage minimum** for all components
4. **Test types**: Unit → Integration → E2E (testing pyramid)
5. **Fast feedback**: Unit tests run locally, full suite in CI/CD

### Manual → Automated Workflow

```
1. Feature Development → Manual Testing
2. Create GitHub Issue with `tested:manual` label
3. Develop Automated Test → Link to Issue
4. Submit PR with test → Merge after review
5. Test added to regression suite (runs on all PRs)
```

---

## Backend Testing (Python + FastAPI)

### Framework: **pytest**

#### Directory Structure

```
src/backend/
├── app/
│   ├── api/
│   ├── models/
│   ├── services/
│   └── utils/
└── tests/
    ├── __init__.py
    ├── conftest.py           # Shared fixtures
    ├── unit/                 # Fast, isolated tests
    │   ├── __init__.py
    │   ├── test_resume_parser.py
    │   ├── test_ai_service.py
    │   ├── test_encryption.py
    │   └── test_models.py
    ├── integration/          # API endpoint tests
    │   ├── __init__.py
    │   ├── test_auth_api.py
    │   ├── test_resume_api.py
    │   ├── test_job_api.py
    │   └── test_application_api.py
    ├── e2e/                  # End-to-end workflows
    │   ├── __init__.py
    │   └── test_application_flow.py
    └── fixtures/             # Test data
        ├── sample_resume.pdf
        ├── sample_job.json
        └── mock_responses.json
```

#### Dependencies

```toml
# pyproject.toml
[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
pytest-mock = "^3.11.1"
httpx = "^0.24.1"           # For testing FastAPI endpoints
faker = "^19.0.0"           # Generate fake test data
factory-boy = "^3.3.0"      # Model factories
freezegun = "^1.2.2"        # Mock datetime
```

#### Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--cov=app",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
    "--cov-fail-under=80"
]
asyncio_mode = "auto"
markers = [
    "unit: Unit tests (fast, no external dependencies)",
    "integration: Integration tests (database, API calls)",
    "e2e: End-to-end tests (full workflows)",
    "slow: Slow running tests",
]
```

#### Sample Tests

**Unit Test Example: `tests/unit/test_resume_parser.py`**

```python
"""Unit tests for resume parser."""
import pytest
from app.services.resume_parser import ResumeParser
from app.schemas.resume import Resume

@pytest.mark.unit
class TestResumeParser:
    """Test resume parsing functionality."""
    
    def test_parse_pdf_resume(self, sample_pdf_path):
        """Test parsing a PDF resume."""
        parser = ResumeParser()
        result = parser.parse(sample_pdf_path)
        
        assert isinstance(result, Resume)
        assert result.full_name
        assert result.email
        assert len(result.work_experiences) > 0
    
    def test_parse_docx_resume(self, sample_docx_path):
        """Test parsing a DOCX resume."""
        parser = ResumeParser()
        result = parser.parse(sample_docx_path)
        
        assert isinstance(result, Resume)
        assert result.full_name
    
    def test_extract_email_from_text(self):
        """Test email extraction from text."""
        parser = ResumeParser()
        text = "Contact me at john.doe@example.com for more info"
        
        email = parser.extract_email(text)
        
        assert email == "john.doe@example.com"
    
    @pytest.mark.parametrize("text,expected", [
        ("2020-2023", (2020, 2023)),
        ("Jan 2020 - Dec 2023", (2020, 2023)),
        ("2020 - Present", (2020, None)),
    ])
    def test_extract_date_range(self, text, expected):
        """Test date range extraction."""
        parser = ResumeParser()
        result = parser.extract_date_range(text)
        assert result == expected
```

**Integration Test Example: `tests/integration/test_resume_api.py`**

```python
"""Integration tests for resume API endpoints."""
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.integration
class TestResumeAPI:
    """Test resume API endpoints."""
    
    @pytest.mark.asyncio
    async def test_upload_resume(self, client: AsyncClient, auth_headers):
        """Test uploading a resume."""
        files = {"file": ("resume.pdf", open("tests/fixtures/sample_resume.pdf", "rb"))}
        
        response = await client.post(
            "/api/v1/resumes/upload",
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["id"]
        assert data["original_filename"] == "resume.pdf"
    
    @pytest.mark.asyncio
    async def test_get_master_resume(self, client: AsyncClient, auth_headers, test_resume):
        """Test fetching master resume."""
        response = await client.get(
            f"/api/v1/resumes/{test_resume.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == test_resume.full_name
    
    @pytest.mark.asyncio
    async def test_tailor_resume(self, client: AsyncClient, auth_headers, test_resume, test_job):
        """Test AI resume tailoring."""
        payload = {
            "job_posting_id": str(test_job.id),
            "prompt_template_id": None  # Use default
        }
        
        response = await client.post(
            f"/api/v1/resumes/{test_resume.id}/tailor",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["version_name"]
        assert data["modifications"]
```

#### Shared Fixtures: `tests/conftest.py`

```python
"""Shared test fixtures."""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.core.security import get_password_hash

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    """Create test database session."""
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session

@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """Create test HTTP client."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def test_user(db_session):
    """Create test user."""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpassword"),
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    """Generate auth headers for test user."""
    from app.core.security import create_access_token
    token = create_access_token({"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_pdf_path():
    """Path to sample PDF resume."""
    return "tests/fixtures/sample_resume.pdf"
```

---

## Frontend Testing (React + TypeScript)

### Framework: **Vitest + Testing Library**

#### Directory Structure

```
src/frontend/
├── src/
│   ├── components/
│   │   ├── ResumeEditor.tsx
│   │   └── __tests__/
│   │       └── ResumeEditor.test.tsx
│   ├── hooks/
│   │   ├── useResume.ts
│   │   └── __tests__/
│   │       └── useResume.test.ts
│   ├── utils/
│   │   ├── formatting.ts
│   │   └── __tests__/
│   │       └── formatting.test.ts
│   └── pages/
│       ├── Dashboard.tsx
│       └── __tests__/
│           └── Dashboard.test.tsx
└── tests/
    ├── setup.ts
    └── mocks/
        └── handlers.ts
```

#### Dependencies

```json
{
  "devDependencies": {
    "vitest": "^1.0.0",
    "@vitest/ui": "^1.0.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/user-event": "^14.5.0",
    "@testing-library/jest-dom": "^6.1.0",
    "jsdom": "^23.0.0",
    "msw": "^2.0.0"
  }
}
```

#### Configuration: `vitest.config.ts`

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.test.{ts,tsx}',
        '**/*.config.{ts,js}',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
});
```

#### Sample Tests

**Component Test: `src/components/__tests__/ResumeEditor.test.tsx`**

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ResumeEditor } from '../ResumeEditor';

describe('ResumeEditor', () => {
  it('renders resume editor with work experience section', () => {
    render(<ResumeEditor resumeId="test-id" />);
    
    expect(screen.getByText('Work Experience')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /add experience/i })).toBeInTheDocument();
  });

  it('adds new work experience when button clicked', async () => {
    const user = userEvent.setup();
    render(<ResumeEditor resumeId="test-id" />);
    
    const addButton = screen.getByRole('button', { name: /add experience/i });
    await user.click(addButton);
    
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Company Name')).toBeInTheDocument();
    });
  });

  it('saves resume changes on save button click', async () => {
    const mockSave = vi.fn();
    const user = userEvent.setup();
    
    render(<ResumeEditor resumeId="test-id" onSave={mockSave} />);
    
    const saveButton = screen.getByRole('button', { name: /save/i });
    await user.click(saveButton);
    
    await waitFor(() => {
      expect(mockSave).toHaveBeenCalledOnce();
    });
  });
});
```

**Hook Test: `src/hooks/__tests__/useResume.test.ts`**

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useResume } from '../useResume';

describe('useResume', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('fetches resume data successfully', async () => {
    const { result } = renderHook(() => useResume('test-id'), { wrapper });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toBeDefined();
    expect(result.current.data?.id).toBe('test-id');
  });

  it('handles loading state', () => {
    const { result } = renderHook(() => useResume('test-id'), { wrapper });

    expect(result.current.isLoading).toBe(true);
  });
});
```

---

## Browser Extension Testing

### Framework: **Jest + Puppeteer**

#### Directory Structure

```
src/extension/
├── src/
│   ├── content/
│   ├── background/
│   └── popup/
└── tests/
    ├── unit/
    │   └── test_ats_detection.ts
    ├── integration/
    │   └── test_chrome_api.ts
    └── e2e/
        ├── test_workday_autofill.ts
        └── test_greenhouse_autofill.ts
```

#### Dependencies

```json
{
  "devDependencies": {
    "jest": "^29.7.0",
    "ts-jest": "^29.1.0",
    "puppeteer": "^21.0.0",
    "@types/jest": "^29.5.0",
    "@types/chrome": "^0.0.250",
    "sinon": "^17.0.0"
  }
}
```

#### Sample E2E Test

```typescript
import puppeteer from 'puppeteer';

describe('Workday Autofill', () => {
  let browser: puppeteer.Browser;
  let page: puppeteer.Page;

  beforeAll(async () => {
    browser = await puppeteer.launch({
      headless: false,
      args: [
        `--disable-extensions-except=${extensionPath}`,
        `--load-extension=${extensionPath}`,
      ],
    });
  });

  beforeEach(async () => {
    page = await browser.newPage();
  });

  afterEach(async () => {
    await page.close();
  });

  afterAll(async () => {
    await browser.close();
  });

  it('detects Workday ATS platform', async () => {
    await page.goto('https://example.wd1.myworkdayjobs.com/job-posting');
    
    const detected = await page.evaluate(() => {
      return window.__ATS_DETECTED__;
    });
    
    expect(detected).toBe('workday');
  });

  it('autofills personal information', async () => {
    await page.goto('https://example.wd1.myworkdayjobs.com/job-posting');
    
    // Trigger autofill
    await page.click('[data-automation-id="autofill-trigger"]');
    
    // Check fields are filled
    const firstName = await page.$eval('#firstName', el => (el as HTMLInputElement).value);
    const lastName = await page.$eval('#lastName', el => (el as HTMLInputElement).value);
    
    expect(firstName).toBe('John');
    expect(lastName).toBe('Doe');
  });
});
```

---

## GitHub Issues Integration

### Test Tracking Workflow

#### 1. Manual Testing Phase

When feature is developed:

```markdown
**Issue Title:** Test: Resume Upload Feature

**Labels:** `tested:manual`, `needs-test`

**Description:**
Feature: Resume upload with PDF/DOCX parsing

Manual Testing Completed:
- ✅ Upload PDF resume
- ✅ Upload DOCX resume
- ✅ Parse contact info correctly
- ✅ Extract work experience
- ✅ Handle invalid file types

Automated Test Required:
- [ ] Unit test for parser
- [ ] Integration test for upload endpoint
- [ ] E2E test for full flow
```

#### 2. Automated Test Creation

Create PR with automated test:

```markdown
**PR Title:** Add automated tests for resume upload

**Closes:** #123

**Changes:**
- Added unit tests for ResumeParser
- Added integration tests for /api/v1/resumes/upload
- Added E2E test for upload flow
- Coverage increased to 85%

**Test Results:**
```
✓ tests/unit/test_resume_parser.py (12 tests)
✓ tests/integration/test_resume_api.py (5 tests)
✓ tests/e2e/test_upload_flow.py (3 tests)
Coverage: 85% (+5%)
```
```

#### 3. GitHub Labels

Use these labels for test tracking:

- `tested:manual` - Feature manually verified
- `needs-test` - Automated test required
- `test:unit` - Unit test needed
- `test:integration` - Integration test needed
- `test:e2e` - E2E test needed
- `test:passing` - All tests passing
- `test:failing` - Tests failing (block merge)

---

## CI/CD Integration (GitHub Actions)

### Workflow: `.github/workflows/test.yml`

```yaml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: testpassword
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd src/backend
          pip install poetry
          poetry install
      
      - name: Run tests
        run: |
          cd src/backend
          poetry run pytest --cov --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:testpassword@localhost:5432/test_db
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./src/backend/coverage.xml
          flags: backend

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd src/frontend
          npm install
      
      - name: Run tests
        run: |
          cd src/frontend
          npm run test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./src/frontend/coverage/lcov.info
          flags: frontend

  extension-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd src/extension
          npm install
      
      - name: Run tests
        run: |
          cd src/extension
          npm test

  coverage-gate:
    needs: [backend-tests, frontend-tests, extension-tests]
    runs-on: ubuntu-latest
    
    steps:
      - name: Check coverage threshold
        run: echo "Coverage checks passed"
```

---

## Running Tests Locally

### Backend

```bash
cd src/backend

# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_resume_parser.py

# Run tests by marker
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only

# Run with coverage
pytest --cov --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Frontend

```bash
cd src/frontend

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- ResumeEditor.test.tsx

# Open UI test runner
npm run test:ui
```

### Extension

```bash
cd src/extension

# Run all tests
npm test

# Run E2E tests only
npm run test:e2e
```

---

## Test Data Management

### Fixtures

Store test data in `tests/fixtures/`:

```
tests/fixtures/
├── sample_resume.pdf
├── sample_resume.docx
├── sample_job.json
├── mock_openai_response.json
└── mock_gmail_messages.json
```

### Factories (Backend)

```python
# tests/factories.py
import factory
from app.models.user import User
from app.models.resume import MasterResume

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    email = factory.Faker('email')
    full_name = factory.Faker('name')
    password_hash = '$2b$12$...'  # bcrypt hash

class ResumeFactory(factory.Factory):
    class Meta:
        model = MasterResume
    
    user = factory.SubFactory(UserFactory)
    full_name = factory.Faker('name')
    email = factory.Faker('email')
```

---

## Best Practices

1. **Test Naming**: Use descriptive names that explain what's being tested
2. **AAA Pattern**: Arrange → Act → Assert
3. **One Assertion Per Test**: Keep tests focused
4. **Mock External Services**: Don't call real AI APIs or email services in tests
5. **Fast Tests**: Unit tests should run in milliseconds
6. **Isolated Tests**: Each test should be independent
7. **Coverage ≠ Quality**: Aim for meaningful tests, not just high coverage

---

## Next Steps

1. ✅ Review testing strategy
2. ⏳ Set up pytest and vitest configurations
3. ⏳ Create initial test fixtures
4. ⏳ Write first test suite for resume parser
5. ⏳ Configure GitHub Actions CI/CD
6. ⏳ Set up code coverage tracking
7. ⏳ Create test tracking GitHub issue template
