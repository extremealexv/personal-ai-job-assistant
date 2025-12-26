# GitHub Copilot Instructions for Personal AI Job Assistant

## Project Overview
This is a **single-user** AI-powered job application management system with three main components:
- **Backend API** (Python) - Core business logic, AI integration, data persistence
- **Web Frontend** (Node.js) - Desktop interface for job/application management  
- **Browser Extension** (Chrome/Edge) - ATS integration for autofill and submission

**Important**: This is NOT a multi-tenant SaaS. All features serve one user managing their personal job search.

## Architecture & Components

### Three-Tier Architecture
```
Browser Extension ←→ Backend API ←→ Database (PostgreSQL)
                       ↓
                  AI Services
```

- **Backend** (`src/backend/`): Python-based API, currently skeleton structure
- **Frontend** (`src/frontend/`): Node.js web application, currently skeleton structure
- **Extension** (`src/extension/`): Browser extension for ATS platforms, currently skeleton structure
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
Currently in **Phase 1 (Foundation)**:
- Setting up core backend API structure
- Defining database schema
- Implementing authentication system
- Building resume parser

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
**Workflow**: Manual test → Create issue (`tested:manual` label) → Write automated test → PR with test → Add to regression suite

**Backend Testing** (pytest):
- `tests/unit/` - Fast, isolated tests (no DB/API calls)
- `tests/integration/` - API endpoint tests with test DB
- `tests/e2e/` - Full workflow tests
- Fixtures in `tests/conftest.py` (test DB session, auth headers, factories)
- **Target**: 80% coverage minimum (enforced in CI/CD)

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

**Test Commands**:
```bash
# Backend
pytest -m unit              # Fast unit tests
pytest -m integration       # API tests
pytest --cov               # With coverage

# Frontend
npm test                   # All tests
npm test -- --watch        # Watch mode
npm test -- --coverage     # With coverage

# Extension
npm test
npm run test:e2e          # E2E tests
```

**GitHub Integration**:
- Use labels: `tested:manual`, `needs-test`, `test:unit`, `test:integration`, `test:e2e`
- Allde Style & Conventions

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

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for full guidelines. Key points:
- Fork from `main` branch
- Follow code style standards (Black/Prettier + ESLint/Ruff)
- Add tests for changes (80% coverage required)
- Update documentation
- Use Conventional Commits format
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

## Testing & Quality

- Add tests for new features (reference `tests/` directory structure when implemented)
- Maintain diff tracking for resume versions (FR-3.4)
- Log all system actions except sensitive content (FR-16.3)

## Security Reminders

1. **Never log sensitive data**: Resume content, passwords, credentials, SSNs
2. **Encrypt at rest**: Job board credentials, sensitive user data (AES-256)
3. **Validate inputs**: Especially from browser extension and uploaded documents
4. **Session management**: 24-hour timeout, invalidate on logout/credential change

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for full guidelines. Key points:
- Fork from `main` branch
- Follow coding standards (TBD as project develops)
- Add tests for changes
- Update documentation

## Common Pitfalls to Avoid

- ❌ Don't design for multi-tenant usage (this is single-user only)
- ❌ Don't mass-apply to jobs without explicit user intent (FR-17)
- ❌ Don't store SSN fragments or government IDs
- ❌ Don't expose credentials to AI components
- ❌ Don't make the system submit applications automatically without user configuration
