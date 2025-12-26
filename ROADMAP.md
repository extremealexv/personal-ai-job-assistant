# Implementation Roadmap & Quick Start

**Project:** Personal AI Job Assistant  
**Date:** December 26, 2025  
**Status:** Phase 1 - Foundation Ready to Begin

---

## 📚 Documentation Overview

All architectural decisions and technical specifications have been documented:

1. **[TECH_STACK.md](./docs/architecture/TECH_STACK.md)** - Complete technology stack recommendations with rationale
2. **[DATABASE_SCHEMA.md](./docs/architecture/DATABASE_SCHEMA.md)** - Full database schema with 15 tables, triggers, and examples
3. **[TESTING_STRATEGY.md](./docs/architecture/TESTING_STRATEGY.md)** - Testing framework setup and GitHub issue workflow
4. **[CODE_STYLE.md](./docs/architecture/CODE_STYLE.md)** - Code quality standards and configurations
5. **[.github/copilot-instructions.md](./.github/copilot-instructions.md)** - AI coding assistant guidance

---

## 🎯 Phase 1: Foundation (Next 4-6 Weeks)

### Week 1-2: Backend Setup

**Tasks:**
- [ ] Set up FastAPI project structure
- [ ] Configure SQLAlchemy 2.0 with async support
- [ ] Initialize PostgreSQL database
- [ ] Create Alembic migrations from schema
- [ ] Implement authentication (FastAPI-Users)
- [ ] Set up Celery + Redis for background tasks

**Deliverables:**
- Working FastAPI server with async endpoints
- Database with all 15 tables created
- User authentication working (login/logout)
- Basic API documentation (auto-generated via FastAPI)

**Commands to Run:**
```bash
cd src/backend

# Initialize Python environment
poetry init
poetry add fastapi sqlalchemy asyncpg alembic celery redis fastapi-users

# Initialize database
python database/init_db.py --drop --seed

# Run server
uvicorn app.main:app --reload
```

---

### Week 2-3: Resume Parser & Core Models

**Tasks:**
- [ ] Implement PDF parsing (PyPDF2 or pdfplumber)
- [ ] Implement DOCX parsing (python-docx)
- [ ] Create resume text extraction logic
- [ ] Build resume data normalization
- [ ] Create SQLAlchemy models for all tables
- [ ] Implement CRUD operations for resumes

**Deliverables:**
- Upload resume endpoint: `POST /api/v1/resumes/upload`
- Parse resume and store in database
- Retrieve master resume: `GET /api/v1/resumes/{id}`
- Unit tests for parser (80%+ coverage)

**Sample API:**
```python
# POST /api/v1/resumes/upload
{
  "file": <binary>,
  "parse_immediately": true
}

# Response
{
  "id": "uuid",
  "full_name": "John Doe",
  "email": "john@example.com",
  "work_experiences": [...],
  "education": [...],
  "skills": [...]
}
```

---

### Week 3-4: Job Management

**Tasks:**
- [ ] Create job posting CRUD endpoints
- [ ] Implement job URL scraping/parsing
- [ ] Add full-text search on job descriptions
- [ ] Build job lifecycle state machine
- [ ] Create application tracking endpoints

**Deliverables:**
- Save job: `POST /api/v1/jobs`
- List jobs: `GET /api/v1/jobs`
- Update job status: `PATCH /api/v1/jobs/{id}/status`
- Create application: `POST /api/v1/applications`

**Sample Workflow:**
```bash
# 1. Save job posting
POST /api/v1/jobs
{
  "company_name": "TechCorp",
  "job_title": "Senior Backend Engineer",
  "job_url": "https://...",
  "job_description": "..."
}

# 2. Tailor resume for job (Week 4-5)
POST /api/v1/resumes/{resume_id}/tailor
{
  "job_posting_id": "uuid",
  "prompt_template_id": "uuid"  // optional
}

# 3. Create application
POST /api/v1/applications
{
  "job_posting_id": "uuid",
  "resume_version_id": "uuid"
}
```

---

### Week 4-5: Frontend Setup

**Tasks:**
- [ ] Initialize Vite + React + TypeScript project
- [ ] Set up Tailwind CSS + shadcn/ui
- [ ] Configure React Query for API state
- [ ] Implement authentication flow
- [ ] Create main layout and navigation
- [ ] Build dashboard page

**Deliverables:**
- Login/logout UI
- Dashboard with job listings
- Resume upload interface
- Basic routing (React Router)

**Tech Setup:**
```bash
cd src/frontend

# Initialize project
npm create vite@latest . -- --template react-ts
npm install

# Add dependencies
npm install @tanstack/react-query zustand react-hook-form zod
npm install -D tailwindcss postcss autoprefixer
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu

# Configure Tailwind
npx tailwindcss init -p
```

---

### Week 5-6: Testing & CI/CD

**Tasks:**
- [ ] Set up pytest with fixtures and factories
- [ ] Write unit tests for resume parser
- [ ] Write integration tests for API endpoints
- [ ] Set up Vitest for frontend
- [ ] Create GitHub Actions workflows
- [ ] Configure pre-commit hooks

**Deliverables:**
- 80%+ test coverage on backend
- 80%+ test coverage on frontend
- CI/CD pipeline running on all PRs
- Pre-commit hooks enforcing code style

**GitHub Actions Workflow:**
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
      - run: pip install poetry && poetry install
      - run: poetry run pytest --cov

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm install && npm test -- --coverage
```

---

## 🚀 Phase 2: AI Integration (Weeks 7-10)

**Key Features:**
- OpenAI API integration
- Resume tailoring engine
- Cover letter generation
- Prompt template management UI

**API Endpoints:**
```
POST /api/v1/ai/tailor-resume
POST /api/v1/ai/generate-cover-letter
GET  /api/v1/prompt-templates
POST /api/v1/prompt-templates
```

---

## 📱 Phase 3: Browser Extension (Weeks 11-15)

**Key Features:**
- ATS platform detection (Workday, Greenhouse, Lever)
- Autofill functionality
- Backend API communication
- Optional submission automation

**Directory Structure:**
```
src/extension/
├── manifest.json
├── background/
│   └── service-worker.ts
├── content/
│   ├── ats-detector.ts
│   └── strategies/
│       ├── workday.ts
│       ├── greenhouse.ts
│       └── lever.ts
└── popup/
    └── popup.html
```

---

## 🔗 Phase 4: Integrations (Weeks 16-19)

**Key Features:**
- Gmail OAuth integration
- Email classification (AI-powered)
- Google Calendar sync
- Interview event creation

---

## 📊 Phase 5: Analytics (Weeks 20-22)

**Key Features:**
- Application metrics dashboard
- Response rate tracking
- Resume version performance comparison
- AI optimization feedback loop

---

## 🛠️ Quick Start Commands

### Initial Setup

```bash
# Clone repository
git clone https://github.com/extremealexv/personal-ai-job-assistant.git
cd personal-ai-job-assistant

# Backend setup
cd src/backend
poetry install
poetry shell
python database/init_db.py --drop --seed

# Frontend setup
cd ../frontend
npm install

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### Development

```bash
# Terminal 1: Backend
cd src/backend
poetry run uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd src/frontend
npm run dev

# Terminal 3: Celery (for background tasks)
cd src/backend
poetry run celery -A app.worker worker --loglevel=info

# Terminal 4: Redis
docker run -p 6379:6379 redis:7-alpine
```

### Testing

```bash
# Backend tests
cd src/backend
pytest                    # All tests
pytest -m unit           # Unit tests only
pytest --cov            # With coverage

# Frontend tests
cd src/frontend
npm test                 # All tests
npm test -- --watch     # Watch mode
npm test -- --coverage  # With coverage
```

### Database Management

```bash
# Create migration
cd src/backend
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1

# Reset database
python database/init_db.py --drop --seed
```

---

## 📝 Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/resume-upload
```

### 2. Implement Feature

- Write code following style guidelines
- Add type hints (Python) / TypeScript types
- Write docstrings/JSDoc

### 3. Manual Testing

Test the feature manually and document:
```markdown
## Manual Testing - Resume Upload

- ✅ Upload PDF resume
- ✅ Upload DOCX resume
- ✅ Parse contact info correctly
- ✅ Extract work experience
- ✅ Handle invalid file types
```

### 4. Create GitHub Issue

```markdown
**Title:** Test: Resume Upload Feature
**Labels:** tested:manual, needs-test

Feature has been manually tested. Automated tests required.
```

### 5. Write Automated Tests

```python
# tests/unit/test_resume_parser.py
def test_parse_pdf_resume(sample_pdf):
    parser = ResumeParser()
    result = parser.parse(sample_pdf)
    assert result.full_name
    assert len(result.work_experiences) > 0
```

### 6. Create Pull Request

```markdown
**Title:** feat(resume): add PDF/DOCX upload and parsing

**Changes:**
- Implemented resume parser
- Added upload endpoint
- Created SQLAlchemy models
- Added unit tests (coverage: 85%)

**Closes:** #42
```

### 7. Code Review & Merge

- CI/CD runs automatically
- Address review feedback
- Merge after approval

---

## 🎓 Learning Resources

### FastAPI
- [Official Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)

### React + TypeScript
- [React Docs](https://react.dev/)
- [TanStack Query](https://tanstack.com/query/latest)

### Testing
- [pytest Documentation](https://docs.pytest.org/)
- [Vitest Guide](https://vitest.dev/guide/)

### Browser Extensions
- [Chrome Extension Docs](https://developer.chrome.com/docs/extensions/)
- [Manifest V3 Migration](https://developer.chrome.com/docs/extensions/mv3/intro/)

---

## 🤝 Getting Help

- **Documentation Issues**: Check docs/ directory first
- **Technical Questions**: Create GitHub Discussion
- **Bugs**: Create GitHub Issue with reproduction steps
- **Feature Requests**: Create GitHub Issue with use case

---

## ✅ Success Criteria

**Phase 1 Complete When:**
- [ ] Backend API running with authentication
- [ ] Database schema created and seeded
- [ ] Resume upload and parsing working
- [ ] Job posting management implemented
- [ ] Frontend dashboard displaying data
- [ ] 80%+ test coverage
- [ ] CI/CD pipeline passing

---

## 📈 Progress Tracking

Track progress using GitHub Projects board:

**Columns:**
1. **Backlog** - Planned features
2. **In Progress** - Currently working on
3. **In Review** - Pull request submitted
4. **Done** - Merged and deployed

**Milestones:**
- Phase 1: Foundation (Week 6)
- Phase 2: AI Integration (Week 10)
- Phase 3: Browser Extension (Week 15)
- Phase 4: Integrations (Week 19)
- Phase 5: Analytics (Week 22)

---

## 🎉 Next Steps

1. ✅ Review all documentation
2. ⏭️ Set up development environment
3. ⏭️ Initialize backend project with FastAPI
4. ⏭️ Create database schema
5. ⏭️ Implement resume parser
6. ⏭️ Build first API endpoints

**Ready to start coding!** 🚀
