# GitHub Copilot Instructions for Personal AI Job Assistant

## Project Overview
This is a **single-user** AI-powered job application management system with three main components:
- **Backend API** (Python/FastAPI) - Core business logic, AI integration, data persistence
- **Web Frontend** (React/TypeScript) - Desktop interface for job/application management  
- **Browser Extension** (Chrome/Edge) - ATS integration for autofill and submission

**Important**: This is NOT a multi-tenant SaaS. All features serve one user managing their personal job search.

**Current Status**: **Issue #56 Complete - Ready for AI Integration Phase**
- ✅ **Backend Core Complete**: 171+ passing tests, 85-98% coverage on core modules
- ✅ **Resume Management (Issue #54)**: 33 endpoints, full CRUD, versioning
- ✅ **Job Management (Issue #56 Phase 1)**: 8 endpoints, lifecycle tracking, keyword extraction
- ✅ **Application Tracking (Issue #56 Phase 2)**: 7 endpoints, status management, job auto-sync
- ✅ **Cover Letter System (Issue #56 Phase 3)**: 7 endpoints, versioning, tone selection
- ✅ **Search & Analytics (Issue #56 Phase 4)**: 5 endpoints, global search, analytics dashboard
- ⏳ **Upcoming**: AI resume tailoring, cover letter generation, browser extension

## Quick Start Commands

### Initial Setup (First Time)
```bash
# Backend setup
cd src/backend
poetry install
poetry shell

# Initialize database (drops existing if --drop flag used)
python database/init_db.py --drop --seed

# Run migrations (when schema changes)
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd src/frontend
npm install
npm run dev  # Starts on http://localhost:5173
```

### Extension Development
```bash
cd src/extension
npm install
npm run build

# Load in browser:
# 1. chrome://extensions (enable Developer Mode)
# 2. "Load unpacked" → select src/extension/dist
```

### Running Tests
```bash
# Backend tests
cd src/backend
pytest                     # Run all tests (171+ tests for Issue #56)
pytest tests/unit/         # Unit tests only (83 tests, fast)
pytest tests/integration/  # Integration tests only (88 tests)
pytest --cov=app/services --cov=app/api/v1/endpoints  # With coverage

# Run specific test files
pytest tests/unit/test_job_service.py -v
pytest tests/integration/test_jobs_api.py -v

# Run tests with debugging
pytest tests/unit/test_job_service.py -v -s --pdb

# Frontend tests (not yet implemented)
cd src/frontend
npm test

# Extension tests (not yet implemented)
cd src/extension
npm test
```

### Code Quality Checks
```bash
# Backend formatting and linting
black .                    # Format Python code
ruff . --fix              # Fix linting issues
mypy app/                 # Type check

# Frontend formatting and linting  
npm run lint:fix          # Fix ESLint issues
npm run format            # Format with Prettier
npm run type-check        # TypeScript type checking

# Run all checks (pre-commit simulation)
pre-commit run --all-files
```

---

## Architecture & Components

### Three-Tier Architecture
```
Browser Extension ←→ Backend API ←→ Database (PostgreSQL)
                       ↓
                  AI Services
```

- **Backend** (`src/backend/`): FastAPI app with SQLAlchemy 2.0, fully functional
  - `app/api/v1/endpoints/`: API route handlers (resumes, jobs, applications, cover_letters, search, analytics, auth, health) - 60+ endpoints
  - `app/services/`: Business logic layer (job_service, application_service, cover_letter_service, search_service, analytics_service)
  - `app/models/`: SQLAlchemy ORM models (15 tables: users, master_resumes, work_experiences, education, skills, certifications, job_postings, resume_versions, applications, cover_letters, etc.)
  - `app/schemas/`: Pydantic models for request/response validation
  - `database/`: Schema SQL + init_db.py script (handles --drop, --seed flags)
  - `tests/`: Unit (83) + Integration (88) tests = 171+ total (Issue #56 complete)
- **Frontend** (`src/frontend/`): React/TypeScript app (skeleton structure, not yet implemented)
- **Extension** (`src/extension/`): Browser extension (skeleton structure, not yet implemented)
- **Shared** (`src/shared/`): Common types, interfaces, utilities

### Key Data Models (Per Requirements)
- **Master Resume**: Canonical parsed resume (PDF/DOCX → structured fields)
- **Resume Versions**: Job-specific tailored variants with diff tracking
- **Job Postings**: Saved via URL or extension, with lifecycle states (Saved → Prepared → Applied → Interviewing → Rejected/Offer/Closed)
- **Application Package**: Bundled resume + cover letter + demographic answers
- **Prompt Templates**: Versioned, editable AI prompts scoped by task and role type

## Functional Requirements Reference

All features are documented in [FUNCTIONAL_REQUIREMENTS.md](../FUNCTIONAL_REQUIREMENTS.md) (FR-1 through FR-18):

- **Resume Management** (FR-3): Upload master resume → parse → normalize → version → tailor → diff tracking
- **AI Resume Tailoring** (FR-5): Optimize for role relevance, executive positioning, ATS keywords; reorder/rewrite/quantify experience
- **Cover Letter Generation** (FR-6): Executive-level persuasive tone, job-specific customization
- **Browser Extension** (FR-9): Detect ATS platforms (Workday, Greenhouse, etc.) → autofill personal info, work history, education, demographics → submit (optional)
- **Email Integration** (FR-12): Gmail OAuth → match emails to applications → classify (confirmation, interview, rejection)
- **Calendar Sync** (FR-13): Detect interview invitations → create Google Calendar events
- **Analytics** (FR-15): Track response rates, interview rates, resume version performance → correlate with prompts/keywords

## Non-Functional Requirements

Key constraints from [NON_FUNCTIONAL_REQUIREMENTS.md](../NON_FUNCTIONAL_REQUIREMENTS.md):

- **Performance**: Resume parsing <5s, AI tailoring <10s, API responses <500ms (95th percentile)
- **Security**: AES-256 encryption at rest, TLS 1.3+ in transit, bcrypt/argon2 for passwords, encrypted credential storage
- **Data Isolation**: Resume data isolated from logs/analytics, no SSN storage
- **Compliance**: GDPR/CCPA compliant with data export/deletion
- **Accessibility**: WCAG 2.1 Level AA, keyboard navigation, proper ARIA labels

## Development Workflow

### Project Status
**Issue #56 Complete** - Ready for AI integration phase:
- ✅ Backend API structure complete
- ✅ Database schema implemented (15 tables)
- ✅ Resume management system (Issue #54)
- ✅ Job posting CRUD (Issue #56 Phase 1)
- ✅ Application tracking (Issue #56 Phase 2)
- ✅ Cover letter management (Issue #56 Phase 3)
- ✅ Search & analytics (Issue #56 Phase 4) - **COMPLETE**
  - Global search across jobs, applications, cover letters
  - Dashboard summary with key metrics
  - Timeline analysis with granularity options
  - Performance metrics (response/interview/offer rates)
  - Conversion funnel analysis
- ⏳ AI resume tailoring (next phase)
- ⏳ AI cover letter generation (next phase)
- ⏳ Browser extension (future phase)

### Tech Stack (Finalized)

**Backend:**
- **Framework**: FastAPI (Python 3.11+) with async/await
- **ORM**: SQLAlchemy 2.0 with Alembic migrations
- **Database**: PostgreSQL 15+ (with pgcrypto, pg_trgm extensions)
- **Task Queue**: Celery + Redis
- **Auth**: FastAPI-Users (bcrypt/argon2, optional WebAuthn)

**Frontend:**
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **UI**: Tailwind CSS + shadcn/ui (accessible components)
- **State**: TanStack Query (React Query) + Zustand
- **Forms**: React Hook Form + Zod validation

**Browser Extension:**
- **Manifest**: V3
- **Core**: Vanilla TypeScript (content scripts)
- **Popup**: Optional React
- **Strategy Pattern**: ATSStrategy interface for platform extensibility

**AI Integration:**
- **Primary**: OpenAI API (GPT-4)
- **Abstraction**: AIProvider interface for model flexibility
- **Fallback**: GPT-3.5-turbo or future Anthropic Claude

**Testing:**
- **Backend**: pytest + pytest-asyncio, httpx, faker, factory-boy
- **Frontend**: Vitest + Testing Library + MSW
- **Extension**: Jest + Puppeteer
- **Coverage**: 80% minimum, enforced in CI/CD

**Code Quality:**
- **Python**: Black (formatter), Ruff (linter), mypy (types), Bandit (security)
- **TypeScript**: Prettier (formatter), ESLint (Airbnb config), tsc --strict
- **Git Hooks**: pre-commit with all formatters/linters

### Running Locally

```bash
# Backend
cd src/backend
poetry install
poetry shell
alembic upgrade head  # Run migrations
uvicorn app.main:app --reload

# Frontend
cd src/frontend
npm install
npm run dev

# Extension
# Load unpacked from src/extension in chrome://extensions

# Run tests
cd src/backend && pytest
cd src/frontend && npm test
cd src/extension && npm test
```

---

## Critical Development Patterns

### Service Layer Architecture
All business logic lives in **service modules**, NOT in API endpoints:
- **Pattern**: Endpoints validate input → call service method → return response
- **Services** (`app/services/`): Pure business logic, database operations, complex queries
- **Endpoints** (`app/api/v1/endpoints/`): HTTP layer only - request/response handling

**Example from job_service.py:**
```python
class JobService:
    @staticmethod
    async def create_job_posting(db: AsyncSession, user_id: UUID, job_data: JobPostingCreate) -> JobPosting:
        """Business logic for creating job posting."""
        # Extract keywords, validate, create model
        extracted_keywords = JobService.extract_keywords(job_data.job_description)
        job = JobPosting(user_id=user_id, extracted_keywords=extracted_keywords, ...)
        db.add(job)
        await db.commit()
        return job
```

**Corresponding endpoint (jobs.py):**
```python
@router.post("/", response_model=JobPostingResponse)
async def create_job(job_data: JobPostingCreate, db: AsyncSession = Depends(get_db), user_id: UUID = Depends(get_current_user_id)):
    return await JobService.create_job_posting(db, user_id, job_data)
```

### Database Initialization Script
`database/init_db.py` is **the single source of truth** for database setup:
- Reads `.env` from **project root** (not `src/backend/`)
- Supports `--drop` flag to recreate schema
- Supports `--seed` flag to add test data
- **Always use this script** instead of manual SQL or Alembic for fresh setup

**Common usage:**
```bash
# Fresh database with seed data
python database/init_db.py --drop --seed

# Add seed data to existing database
python database/init_db.py --seed
```

### Test Fixtures Pattern
Tests use **pytest fixtures** from `tests/conftest.py`:
- `db_session`: Async database session (rolled back after each test)
- `test_user`: Pre-created user for testing
- `sample_job_posting`, `sample_application`, etc.: Pre-created entities

**Always use fixtures instead of creating data manually:**
```python
# ✅ Good
async def test_get_job(db_session, test_user, sample_job_posting):
    job = await JobService.get_job_posting(db_session, sample_job_posting.id, test_user.id)
    assert job.id == sample_job_posting.id

# ❌ Bad - creates duplicate data
async def test_get_job(db_session):
    user = User(email="test@example.com")  # Don't do this
    db_session.add(user)
```

### Environment Configuration
- **`.env` file location**: Project root, NOT `src/backend/`
- **Config loading**: `app/config.py` searches up to project root automatically
- **Test database**: Uses `{dbname}_test` suffix (e.g., `ai_job_assistant_test`)
- **Required vars**: `DATABASE_URL`, `DATABASE_ASYNC_URL`, `SECRET_KEY`

### Error Handling Pattern
Use custom exceptions from `app/core/exceptions.py`:
```python
from app.core.exceptions import NotFoundError, ForbiddenError

# In service layer
if not job:
    raise NotFoundError(f"Job posting {job_id} not found")
if job.user_id != user_id:
    raise ForbiddenError("Cannot access job owned by another user")
```

These are automatically converted to proper HTTP responses by exception handlers in `main.py`.

---

## File Structure Quick Reference

```
personal-ai-job-assistant/
├── .github/
│   └── copilot-instructions.md     # This file
├── docs/
│   ├── architecture/
│   │   ├── DATABASE_SCHEMA.md      # 15 tables, full schema with examples
│   │   ├── TECH_STACK.md           # Technology choices with rationale
│   │   ├── CODE_STYLE.md           # Formatting/linting standards
│   │   └── TESTING_STRATEGY.md     # Test patterns and coverage requirements
│   ├── api/                        # API documentation (TBD)
│   └── deployment/                 # Deployment guides (TBD)
├── src/
│   ├── backend/
│   │   ├── app/                    # FastAPI application (functional)
│   │   │   ├── api/v1/endpoints/   # 8 endpoint modules (55+ routes)
│   │   │   ├── services/           # 5 service modules (business logic)
│   │   │   ├── models/             # SQLAlchemy ORM models
│   │   │   ├── schemas/            # Pydantic validation models
│   │   │   ├── core/               # Exceptions, middleware, logging
│   │   │   └── main.py             # FastAPI app initialization
│   │   ├── database/
│   │   │   ├── schema.sql          # Complete PostgreSQL schema
│   │   │   └── init_db.py          # Database initialization script
│   │   └── tests/                  # 122 tests (61 unit + 61 integration)
│   ├── frontend/                   # React application (TBD)
│   ├── extension/                  # Browser extension (TBD)
│   └── shared/                     # Shared types/utilities (TBD)
├── tests/                          # Test files (organized by component)
├── FUNCTIONAL_REQUIREMENTS.md      # FR-1 through FR-18 specifications
├── NON_FUNCTIONAL_REQUIREMENTS.md  # Performance, security, compliance
├── CONTRIBUTING.md                 # Contribution guidelines
└── README.md                       # Project overview
```

---

## Key Patterns & Conventions

### Database Schema
Full schema in [docs/architecture/DATABASE_SCHEMA.md](../docs/architecture/DATABASE_SCHEMA.md):
- **15 core tables**: users, master_resumes, work_experiences, education, skills, certifications, job_postings, resume_versions, prompt_templates, applications, cover_letters, credentials, email_threads, interview_events, analytics_snapshots
- **UUID primary keys** throughout
- **Soft deletes** via `deleted_at` timestamp
- **JSONB columns** for flexible data (resume diffs, demographics, AI metadata)
- **Triggers**: Auto-update `updated_at`, increment usage stats, cascade job status updates
- **Indexes**: Full-text search on job descriptions, composite indexes for common queries
- **Encryption**: pgcrypto extension for credentials, stored as BYTEA

### Prompt Management (FR-7)
- Prompts are **versioned editable entities** stored in `prompt_templates` table
- Scoped by task (`resume_tailor`, `cover_letter`, `form_answers`) and role type
- Support per-job overrides of default prompts
- Track usage stats (`times_used`, `avg_satisfaction_score`)

### Credential Handling (FR-10)
- Job board credentials: encrypted at rest using pgcrypto or application-level encryption (Fernet)
- Stored in `credentials` table with `password_encrypted` BYTEA column
- Never expose to AI components or logs

### Browser Extension Architecture (FR-9, FR-18.1)
- Use **Strategy Pattern** for ATS platform support:
  ```typescript
  interface ATSStrategy {
    detect(): boolean;
    autofill(data: ApplicationData): Promise<void>;
    submit?(): Promise<void>;
  }
  ```
- Implement per-platform: `WorkdayStrategy`, `GreenhouseStrategy`, `LeverStrategy`
- Design for extensibility: add new platforms without core rewrites

### AI Model Flexibility (FR-18.2)
- Use **Abstract Provider Pattern**:
  ```python
  class AIProvider(ABC):
      @abstractmethod
      async def tailor_resume(...) -> TailoredResume: ...
      @abstractmethod
      async def generate_cover_letter(...) -> str: ...
  ```
- Implementations: `OpenAIProvider`, `AnthropicProvider` (future)
- Business logic must be model-agnostic

---

## Testing & Quality

### Testing Strategy
**Workflow**: Manual test → Create issue (`tested:manual` label) → Write automated test → PR with test → Add to regression suite

**Backend Testing** (pytest):
- `tests/unit/` - Fast, isolated tests (no DB/API calls)
- `tests/integration/` - API endpoint tests with test DB
- `tests/e2e/` - Full workflow tests
- Fixtures in `tests/conftest.py` (test DB session, auth headers, factories)
- **Target**: 80% coverage minimum (enforced in CI/CD)

**Current Status (Issue #56 - All Phases Complete):**
- 171+ tests passing (83 unit + 88 integration)
- 85-98% coverage on services and API endpoints
- Test execution time: ~10-15 seconds for full suite
- Phase 4 adds: 22 search tests + 27 analytics tests = 49 new tests

**Writing Tests - Key Patterns:**

1. **Unit tests** test service methods in isolation:
```python
# tests/unit/test_job_service.py
async def test_create_job_posting(db_session, test_user):
    job_data = JobPostingCreate(company_name="TechCorp", job_title="Engineer", job_url="https://...")
    job = await JobService.create_job_posting(db_session, test_user.id, job_data)
    assert job.company_name == "TechCorp"
    assert job.user_id == test_user.id
```

2. **Integration tests** test full HTTP request/response cycle:
```python
# tests/integration/test_jobs_api.py
async def test_create_job_endpoint(async_client, auth_headers):
    response = await async_client.post(
        "/api/v1/jobs/",
        json={"company_name": "TechCorp", "job_title": "Engineer", "job_url": "https://..."},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["company_name"] == "TechCorp"
```

3. **Use fixtures for common setup:**
- `db_session`: Isolated database transaction
- `test_user`: Authenticated user
- `auth_headers`: Authentication headers for API requests
- `sample_job_posting`, `sample_application`: Pre-created entities

### Test Database Management
- Test DB is automatically created with `_test` suffix
- Each test runs in an isolated transaction (rolled back after test)
- Use `db_session` fixture, never create your own engine
- Seed data available via `--seed` flag in init_db.py

**Frontend Testing** (Vitest + Testing Library):
- Co-located tests: `src/components/__tests__/ComponentName.test.tsx`
- Use `render()`, `screen`, `userEvent` from Testing Library
- Mock API calls with MSW (Mock Service Worker)
- Test hooks with `renderHook()`
- **Target**: 80% coverage minimum

**Extension Testing** (Jest + Puppeteer):
- Unit tests for ATS detection logic
- E2E tests for autofill on real ATS platforms
- Mock Chrome APIs with sinon

### Code Style & Conventions

**Python** (Black, Ruff, mypy):
- Line length: 100 characters
- Use type hints (mypy --strict)
- Google-style docstrings
- Run: `black .`, `ruff . --fix`, `mypy app/`

**TypeScript** (Prettier, ESLint):
- Airbnb style guide + TypeScript rules
- Interfaces prefixed with `I`: `IResume`, `IUser`
- Organize imports (builtin → external → internal → parent → sibling)
- Run: `npm run lint:fix`, `npm run format`, `npm run type-check`

**Git Commits** (Conventional Commits):
```
feat(resume): add PDF parsing support
fix(auth): prevent session timeout during active use
test(backend): add unit tests for resume parser
docs(api): update resume API endpoint documentation
```

**Pre-commit Hooks**:
Install with `pre-commit install` - automatically runs formatters/linters before commit

Full details in [docs/architecture/CODE_STYLE.md](../docs/architecture/CODE_STYLE.md)

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for full guidelines. Key points:
- Fork from `main` branch
- Follow code style standards (Black/Prettier + ESLint/Ruff)
- Add tests for changes (80% coverage required)
- Update documentation
- Maintain diff tracking for resume versions (FR-3.4)
- Log all system actions except sensitive content (FR-16.3)

## Security Reminders

1. **Never log sensitive data**: Resume content, passwords, credentials, SSNs
2. **Encrypt at rest**: Job board credentials, sensitive user data (AES-256)
3. **Validate inputs**: Especially from browser extension and uploaded documents
4. **Session management**: 24-hour timeout, invalidate on logout/credential change

---

## Common Pitfalls to Avoid

- ❌ Don't design for multi-tenant usage (this is single-user only)
- ❌ Don't mass-apply to jobs without explicit user intent (FR-17)
- ❌ Don't store SSN fragments or government IDs
- ❌ Don't expose credentials to AI components
- ❌ Don't make the system submit applications automatically without user configuration

---

## Troubleshooting

### Database Issues
```bash
# Reset database completely
cd src/backend
python database/init_db.py --drop --seed

# Check connection
psql -U postgres -d ai_job_assistant -c "SELECT version();"

# View migrations status
alembic current
alembic history
```

### Python Environment Issues
```bash
# Reset virtual environment
poetry env remove python
poetry install
poetry shell

# Verify Python version
python --version  # Should be 3.11+
```

### Frontend Build Issues
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for type errors
npm run type-check
```

### Extension Not Loading
- Ensure Developer Mode is enabled in chrome://extensions
- Check manifest.json is valid (no syntax errors)
- Check browser console for Content Security Policy (CSP) errors
- Reload extension after code changes

### Test Failures
```bash
# Run specific test file
pytest tests/unit/test_resume_parser.py -v

# Run with debugging
pytest tests/unit/test_resume_parser.py -v -s --pdb

# Clear pytest cache
pytest --cache-clear
```
