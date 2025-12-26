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

### Tech Stack
- **Backend**: Python ≥3.11 (framework TBD), PostgreSQL ≥15
- **Frontend**: Node.js ≥18.x (framework TBD)
- **Extension**: Chrome/Edge Manifest V3

### Running Locally (per README)
```bash
# Backend
cd src/backend
pip install -r requirements.txt
python manage.py runserver

# Frontend
cd src/frontend
npm install
npm run dev

# Extension
# Load unpacked from src/extension in chrome://extensions
```

## Key Patterns & Conventions

### Prompt Management (FR-7)
- Prompts are **versioned editable entities** stored in the database
- Scoped by task (resume, cover letter, form answers) and role type
- Support per-job overrides of default prompts

### Credential Handling (FR-10)
- Job board credentials: encrypted at rest, accessible only to browser extension
- **Critical**: Credentials NEVER exposed to AI components

### ATS Platform Support (FR-18.1)
- Design for extensibility: add new ATS platforms without core rewrites
- Use strategy/adapter pattern for platform-specific logic

### AI Model Flexibility (FR-18.2)
- Abstract AI model interface to allow swapping providers (OpenAI, Anthropic, etc.)
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
