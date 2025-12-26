# Tech Stack Recommendations

**Project:** Personal AI Job Search Assistant  
**Date:** December 26, 2025  
**Status:** Proposed

---

## Executive Summary

This document outlines the recommended technology stack for the Personal AI Job Assistant, optimized for:
- Single-user deployment (not multi-tenant)
- AI integration with multiple providers
- Browser automation and ATS integration
- Local or cloud deployment flexibility
- Developer productivity and maintainability

---

## Backend Stack

### Framework: **FastAPI** (Recommended)

**Why FastAPI:**
- ✅ **Async-first** - Essential for AI API calls, email checking, calendar sync
- ✅ **Type Safety** - Python 3.11+ type hints align with project requirements
- ✅ **Auto Documentation** - Built-in OpenAPI/Swagger (NFR-5.2)
- ✅ **Performance** - Faster than Flask/Django for API workloads
- ✅ **Modern Python** - Uses latest async/await patterns
- ✅ **Easy AI Integration** - Great for streaming responses, long-running tasks

**Alternative Considered:** Django (more boilerplate, overkill for single-user)

### ORM: **SQLAlchemy 2.0**

- ✅ Type-safe with Python 3.11+ 
- ✅ Async support via SQLAlchemy async engine
- ✅ Flexible migrations with Alembic
- ✅ Works seamlessly with FastAPI

### Task Queue: **Celery + Redis**

**Use Cases:**
- Resume parsing (background processing)
- AI resume tailoring (can take 5-10s)
- Email polling and classification
- Calendar event creation

**Why:**
- ✅ Proven for async Python tasks
- ✅ Redis provides caching layer (bonus)
- ✅ Monitoring via Flower
- ✅ Retry logic built-in (NFR-4.3)

### Authentication: **FastAPI-Users**

- ✅ Built-in password hashing (bcrypt/argon2)
- ✅ Session management
- ✅ WebAuthn support (optional 2FA - NFR-2.2)
- ✅ OAuth2 flow for Gmail/Calendar integration

---

## Database

### Primary Database: **PostgreSQL 15+**

**Schema Design Principles:**
- Normalized structure for master resume data
- JSONB columns for flexible resume version diffs
- Full-text search for job descriptions (pg_trgm, ts_vector)
- Encrypted columns for credentials (pgcrypto)

**Why PostgreSQL:**
- ✅ JSONB for flexible document storage (resume versions, job data)
- ✅ Full-text search capabilities
- ✅ Row-level encryption support
- ✅ Excellent Python/SQLAlchemy support
- ✅ ACID compliance (NFR-4.2 - data integrity)
- ✅ Point-in-time recovery (PITR) for backups

**Alternative Considered:** 
- MongoDB (less suited for relational job/application tracking)
- SQLite (insufficient for encryption requirements)

### Caching: **Redis**

- Session storage
- Rate limiting
- Task queue backend
- Temporary AI response caching

---

## Frontend Stack

### Framework: **React 18+ with TypeScript**

**Why React:**
- ✅ Largest ecosystem for component libraries
- ✅ Excellent TypeScript support
- ✅ React Query for API state management
- ✅ Rich text editing libraries (for resume/cover letter editing)
- ✅ Drag-and-drop support (for resume reordering)

**Alternative Considered:**
- Vue 3 (smaller ecosystem)
- Svelte (less mature for complex forms)

### Build Tool: **Vite**

- ✅ Fast dev server and HMR
- ✅ TypeScript out of the box
- ✅ Optimized production builds
- ✅ Modern and actively maintained

### UI Framework: **Tailwind CSS + shadcn/ui**

**Why:**
- ✅ Tailwind: Utility-first, highly customizable, small bundle
- ✅ shadcn/ui: Accessible components (WCAG 2.1 AA - NFR-3.2)
- ✅ Copy-paste components (no package bloat)
- ✅ Built on Radix UI primitives (keyboard navigation, ARIA)

**Alternative Considered:**
- Material UI (larger bundle, more opinionated)
- Ant Design (less accessibility focus)

### State Management: **TanStack Query (React Query) + Zustand**

- **React Query**: Server state (API calls, caching, optimistic updates)
- **Zustand**: Client state (UI state, form state)
- ✅ Minimal boilerplate vs Redux
- ✅ Built-in devtools

### Form Handling: **React Hook Form + Zod**

- ✅ Type-safe validation with Zod schemas
- ✅ Excellent performance (uncontrolled inputs)
- ✅ Easy integration with Tailwind forms

---

## Browser Extension

### Architecture: **Manifest V3**

**Technology:**
- **Vanilla TypeScript** (no framework - minimize bundle size)
- **Web Extension Polyfill** (cross-browser compatibility)
- **Content Scripts**: ATS form detection and manipulation
- **Background Service Worker**: API communication, credential management
- **Popup**: React (optional, for settings UI)

**Why Vanilla TS for Content Scripts:**
- ✅ Minimal bundle size (critical for extension performance)
- ✅ No framework overhead in injected scripts
- ✅ Direct DOM manipulation for ATS forms
- ✅ Framework can be used for popup UI if needed

### ATS Detection Strategy:

```typescript
// Strategy pattern for extensibility (FR-18.1)
interface ATSStrategy {
  detect(): boolean;
  autofill(data: ApplicationData): Promise<void>;
  submit?(): Promise<void>;
}

class WorkdayStrategy implements ATSStrategy { ... }
class GreenhouseStrategy implements ATSStrategy { ... }
class LeverStrategy implements ATSStrategy { ... }
```

---

## AI Integration

### Primary Provider: **OpenAI API** (GPT-4)

**Why:**
- ✅ Best-in-class for text generation and reasoning
- ✅ Structured output support (JSON mode)
- ✅ Function calling for tool use
- ✅ Proven for resume optimization tasks

### Provider Abstraction Layer:

```python
# Abstract interface for model flexibility (FR-18.2)
class AIProvider(ABC):
    @abstractmethod
    async def tailor_resume(
        self, 
        master_resume: Resume,
        job_description: str,
        prompt_template: PromptTemplate
    ) -> TailoredResume:
        pass
    
    @abstractmethod
    async def generate_cover_letter(...) -> str:
        pass

class OpenAIProvider(AIProvider): ...
class AnthropicProvider(AIProvider): ...  # Future support
```

### Fallback Strategy:
- Primary: OpenAI GPT-4
- Fallback: OpenAI GPT-3.5-turbo (cheaper, faster)
- Future: Anthropic Claude, local LLMs

---

## Testing Stack

### Backend Testing

**Framework: pytest + pytest-asyncio**

```python
# Test structure
tests/
├── unit/              # Fast, isolated tests
│   ├── test_resume_parser.py
│   ├── test_ai_service.py
│   └── test_models.py
├── integration/       # API endpoint tests
│   ├── test_auth_api.py
│   ├── test_resume_api.py
│   └── test_job_api.py
├── e2e/              # End-to-end workflows
│   └── test_application_flow.py
└── conftest.py       # Shared fixtures
```

**Tools:**
- `pytest`: Test framework
- `pytest-asyncio`: Async test support
- `pytest-cov`: Coverage reporting (target 80%+)
- `httpx`: HTTP client for API testing
- `faker`: Test data generation
- `factory-boy`: Model factories
- `freezegun`: Time mocking

### Frontend Testing

**Framework: Vitest + Testing Library**

```typescript
// Test structure
src/
├── components/
│   ├── ResumeEditor.tsx
│   └── __tests__/
│       └── ResumeEditor.test.tsx
├── hooks/
│   ├── useResume.ts
│   └── __tests__/
│       └── useResume.test.ts
└── utils/
    ├── formatting.ts
    └── __tests__/
        └── formatting.test.ts
```

**Tools:**
- `vitest`: Fast Vite-native test runner
- `@testing-library/react`: Component testing
- `@testing-library/user-event`: User interaction simulation
- `msw` (Mock Service Worker): API mocking
- `@vitest/ui`: Visual test runner

### Extension Testing

**Framework: Jest + Puppeteer**

```typescript
tests/
├── unit/              # Content script logic
├── integration/       # Extension API interactions
└── e2e/              # Full browser automation tests
    ├── test_workday_autofill.ts
    └── test_greenhouse_autofill.ts
```

**Tools:**
- `jest`: Test framework
- `puppeteer`: Browser automation
- `@types/chrome`: TypeScript types for Chrome APIs
- `sinon`: Mocking Chrome APIs

### Test Workflow (GitHub Issues Integration)

**Process:**
1. **Manual Testing** → Create issue with `tested:manual` label
2. **Automated Test Creation** → PR with test, reference issue
3. **Regression Suite** → Test runs on all PRs via GitHub Actions
4. **Coverage Gate** → Block merge if coverage drops below 80%

**GitHub Labels:**
- `tested:manual` - Manually verified
- `needs-test` - Automated test required
- `test:unit` - Unit test needed
- `test:integration` - Integration test needed
- `test:e2e` - E2E test needed

---

## Code Quality & Style

### Python (Backend)

**Tools:**
- **Formatter:** `black` (line length: 100)
- **Linter:** `ruff` (replaces flake8, isort, pylint)
- **Type Checker:** `mypy --strict`
- **Security:** `bandit` (security issue scanner)

**Configuration: `pyproject.toml`**
```toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W", "ANN", "S", "B"]
ignore = ["ANN101", "ANN102"]  # Self/cls annotations

[tool.mypy]
strict = true
python_version = "3.11"
```

### TypeScript/JavaScript (Frontend & Extension)

**Tools:**
- **Formatter:** `prettier`
- **Linter:** `eslint` (Airbnb config + TypeScript rules)
- **Type Checker:** `tsc --noEmit` (strict mode)

**Configuration: `.eslintrc.json`**
```json
{
  "extends": [
    "airbnb",
    "airbnb-typescript",
    "airbnb/hooks",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/recommended-requiring-type-checking",
    "prettier"
  ],
  "rules": {
    "react/react-in-jsx-scope": "off",
    "import/prefer-default-export": "off"
  }
}
```

### Git Hooks: **pre-commit**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    hooks:
      - id: ruff
  - repo: https://github.com/pre-commit/mirrors-prettier
    hooks:
      - id: prettier
        types_or: [javascript, typescript, tsx, json, css]
```

---

## CI/CD Pipeline (GitHub Actions)

### Pipeline Stages

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pytest --cov --cov-report=xml
      - run: mypy src/backend
      - run: bandit -r src/backend
      
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm test -- --coverage
      - run: npm run type-check
      - run: npm run lint
      
  extension-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm test
      
  build:
    needs: [backend-tests, frontend-tests, extension-tests]
    steps:
      - run: docker build -t ai-job-assistant .
      - run: docker-compose up -d
      - run: pytest tests/e2e
```

### Deployment Strategy

**For Personal Use:**
- Docker Compose for local deployment
- Optional: Single DigitalOcean droplet with Docker
- GitHub Actions for automated testing (not deployment)

**Future (if shared):**
- Heroku/Railway/Fly.io for simple deployment
- AWS/GCP/Azure for production

---

## Development Environment

### Recommended Setup

**Backend:**
```bash
# Use pyenv for Python version management
pyenv install 3.11.7
pyenv local 3.11.7

# Use poetry for dependency management
poetry install
poetry shell
```

**Frontend:**
```bash
# Use nvm for Node version management
nvm install 18
nvm use 18

# Use pnpm (faster than npm)
pnpm install
```

### Docker Development

```yaml
# docker-compose.yml (development)
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ai_job_assistant
      POSTGRES_PASSWORD: dev_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    
  backend:
    build: ./src/backend
    depends_on: [postgres, redis]
    environment:
      DATABASE_URL: postgresql://...
      REDIS_URL: redis://...
    volumes:
      - ./src/backend:/app
      
  frontend:
    build: ./src/frontend
    volumes:
      - ./src/frontend:/app
    ports:
      - "3000:3000"
```

---

## Security Considerations

### Secrets Management

**Development:**
- `.env` files (not committed)
- `.env.example` as template

**Production:**
- Environment variables
- Consider: Doppler, AWS Secrets Manager, or 1Password CLI

### Encryption at Rest

**PostgreSQL pgcrypto extension:**
```sql
-- Encrypt job board credentials
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Store encrypted credentials
INSERT INTO credentials (platform, username, password_encrypted)
VALUES (
  'linkedin',
  'user@example.com',
  pgp_sym_encrypt('password123', 'encryption_key')
);
```

**Application-level encryption:**
```python
from cryptography.fernet import Fernet

class CredentialService:
    def __init__(self, encryption_key: str):
        self.cipher = Fernet(encryption_key)
    
    def encrypt_credential(self, value: str) -> bytes:
        return self.cipher.encrypt(value.encode())
    
    def decrypt_credential(self, encrypted: bytes) -> str:
        return self.cipher.decrypt(encrypted).decode()
```

---

## Implementation Phases

### Phase 1: Foundation (4-6 weeks)
- [ ] Set up FastAPI backend with SQLAlchemy
- [ ] Create database schema and migrations
- [ ] Implement authentication system
- [ ] Build resume parser (PDF/DOCX)
- [ ] Set up React frontend with basic routing
- [ ] Configure CI/CD pipeline
- [ ] Set up testing infrastructure

### Phase 2: AI Integration (3-4 weeks)
- [ ] Integrate OpenAI API
- [ ] Implement resume tailoring engine
- [ ] Build cover letter generation
- [ ] Create prompt management system
- [ ] Add Celery for background tasks

### Phase 3: Browser Extension (4-5 weeks)
- [ ] Build extension manifest and structure
- [ ] Implement ATS detection (Workday, Greenhouse)
- [ ] Create autofill logic
- [ ] Add backend API communication
- [ ] Build optional submission automation

### Phase 4: Integrations (3-4 weeks)
- [ ] Gmail OAuth integration
- [ ] Email classification system
- [ ] Google Calendar sync
- [ ] Application status tracking

### Phase 5: Analytics (2-3 weeks)
- [ ] Build analytics dashboard
- [ ] Implement performance tracking
- [ ] Add AI feedback loop
- [ ] Resume version A/B testing

---

## Cost Estimates (Monthly)

**Development (Personal Use):**
- OpenAI API: $20-50 (depending on usage)
- DigitalOcean Droplet: $12 (optional, for cloud hosting)
- Total: ~$30-60/month

**Future (Production):**
- Cloud hosting: $50-200
- Database: $25-100
- AI API: $100-500 (with scale)
- Total: ~$175-800/month

---

## Decision Log

| Decision | Rationale | Date |
|----------|-----------|------|
| FastAPI over Django | Async-first, modern Python, auto docs | 2025-12-26 |
| PostgreSQL over MongoDB | Better for relational data, JSONB flexibility | 2025-12-26 |
| React over Vue/Svelte | Largest ecosystem, best TypeScript support | 2025-12-26 |
| Tailwind + shadcn/ui | Accessibility, customization, no package bloat | 2025-12-26 |
| pytest over unittest | Better async support, fixtures, plugins | 2025-12-26 |
| Vitest over Jest | Native Vite integration, faster | 2025-12-26 |

---

## Next Steps

1. ✅ Review and approve tech stack
2. ⏳ Set up project structure and dependencies
3. ⏳ Create database schema and migrations
4. ⏳ Configure testing framework and CI/CD
5. ⏳ Implement Phase 1 features

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/)
- [React 18 Documentation](https://react.dev/)
- [Manifest V3 Migration Guide](https://developer.chrome.com/docs/extensions/mv3/intro/)
- [OWASP Security Guidelines](https://owasp.org/)
