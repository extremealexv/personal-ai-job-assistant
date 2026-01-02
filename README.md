# Personal AI Job Search Assistant

> An intelligent job application management system with AI-powered resume tailoring and browser automation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: In Development](https://img.shields.io/badge/Status-In%20Development-blue)]()

## 📋 Overview

The Personal AI Job Search Assistant is a comprehensive system designed to streamline the job application process for software engineers. It combines AI-powered content generation with browser automation to help you:

- **Manage** job postings and applications in one place
- **Optimize** resumes and cover letters for specific roles
- **Automate** form filling and application submission
- **Track** application status and interview scheduling
- **Analyze** performance metrics to improve success rates

## 🎯 Key Features

### ✅ Implemented

#### Resume Management System (Issue #54)
- Master resume upload (PDF/DOCX)
- Structured data extraction (work experience, education, skills, certifications)
- Resume versioning with job-specific modifications
- Advanced search and statistics
- **33 REST API endpoints**
- **100 tests** (26 unit + 74 integration)
- **77% test coverage**

#### Job Management System (Issue #56 - Phase 1) ✨ NEW
- Create and manage job postings
- Job lifecycle tracking (saved → prepared → applied → interviewing → offer/rejected/closed)
- Keyword extraction from job descriptions
- Full-text search across jobs
- Interest level scoring (1-5)
- ATS platform detection
- **8 REST API endpoints**
- **47 tests** (23 unit + 24 integration, 100% pass rate)
- **98% service coverage, 86% API coverage**

#### Application Tracking System (Issue #56 - Phase 2) ✨ NEW
- Create applications linked to jobs and resume versions
- Application status tracking (draft → submitted → interviewing → offer/rejected)
- Auto-sync job status when application submitted
- Follow-up date tracking
- Demographics data storage
- Application statistics
- **7 REST API endpoints**
- **39 tests** (20 unit + 19 integration, 100% pass rate)
- **94% service coverage**

#### Cover Letter Management (Issue #56 - Phase 3) ✨ NEW
- Multiple cover letter versions per application
- Version management (auto-incrementing, activation control)
- Content validation (100-10,000 characters)
- Tone selection (professional/enthusiastic/formal/creative)
- AI generation metadata tracking
- **7 REST API endpoints**
- **36 tests** (18 unit + 18 integration, 100% pass rate)
- **96% service coverage, 90% API coverage**

#### AI Resume Tailoring (AI Integration - Phase 1) 🤖 **NEW**
- AI-powered resume optimization for specific job postings
- Automatic keyword extraction and relevance matching
- Executive-level positioning and quantifiable impact
- Resume version creation with tracked modifications
- Support for multiple AI providers (OpenAI, Google Gemini)
- Customizable prompt templates per role type
- JSON parsing with flexible markdown code block handling
- **2 REST API endpoints** (`/api/v1/ai/resume/tailor`, `/api/v1/ai/resume/versions`)
- **30+ unit tests, 15+ integration tests**
- **Zero-cost operation with Gemini free tier**
- **~8-10 second generation time**

#### AI Cover Letter Generation (AI Integration - Phase 2) 🤖 **NEW**
- AI-generated personalized cover letters per application
- Multiple tone options (professional/enthusiastic/formal/creative)
- Executive-level persuasive writing
- Company and role-specific customization
- Version management with activation control
- Resume summary integration
- Customizable prompt templates
- **3 REST API endpoints** (`/api/v1/ai/cover-letter/generate`, `/list`, `/{id}`)
- **25+ unit tests, 20+ integration tests**
- **Zero-cost operation with Gemini free tier**
- **~8-10 second generation time**

**Total Implementation Status:**
- ✅ **240+ tests passing** (120+ unit + 120+ integration)
- ✅ **85-98% coverage** on all core modules
- ✅ **65+ REST API endpoints** fully functional
- ✅ **AI features operational** with Google Gemini at $0 cost

### 🚧 Planned
- **Browser Extension** - Autofill and submit applications on major ATS platforms
- **Email Integration** - Automatic tracking via Gmail integration
- **Calendar Sync** - Interview scheduling with Google Calendar
- **Analytics Dashboard** - Advanced metrics and performance tracking
- **Search & Analytics** - Global search across all data, trend analysis

## 🏗️ Architecture

This project consists of three main components:

1. **Backend API** - Core business logic, AI integration, data management
2. **Web Application** - Desktop interface for job and application management
3. **Browser Extension** - Chrome/Edge extension for ATS integration

## 🤖 AI Features

### AI Resume Tailoring

Automatically optimize your resume for specific job postings using AI:

- **Smart Keyword Matching**: Extracts keywords from job descriptions and tailors resume content
- **Executive Positioning**: Rewrites experience with executive-level impact statements
- **Quantifiable Achievements**: Emphasizes metrics and measurable results
- **ATS Optimization**: Ensures resume passes Applicant Tracking Systems
- **Version Tracking**: Creates new resume versions with modification history

**How it works:**
1. Upload your master resume (PDF/DOCX)
2. Save a job posting (URL or paste description)
3. Click "Tailor Resume" - AI generates optimized version
4. Review, edit, and download tailored resume

**Technical Details:**
- Uses Google Gemini (free tier) or OpenAI GPT-4
- Customizable prompt templates per role type
- Handles markdown-wrapped JSON responses
- ~8-10 second generation time
- $0.00 cost with Gemini free tier

### AI Cover Letter Generation

Generate personalized, executive-level cover letters for each application:

- **Company-Specific**: Researched and personalized to company mission
- **Role-Aligned**: Highlights relevant experience for specific position
- **Persuasive Tone**: Professional, executive-level writing style
- **Quantifiable Impact**: Includes metrics from your experience
- **Multiple Versions**: Generate and compare different approaches

**How it works:**
1. Create an application (links job + tailored resume)
2. Select tone (professional/enthusiastic/formal/creative)
3. Click "Generate Cover Letter" - AI creates personalized letter
4. Review multiple versions and activate preferred one

**Technical Details:**
- Integrates resume summary with job requirements
- Configurable tone and style preferences
- Version management with activation control
- ~8-10 second generation time
- $0.00 cost with Gemini free tier

### AI Provider Configuration

Supported providers:
- **Google Gemini** (default, free tier available)
  - Models: `gemini-2.5-flash` (free), `gemini-1.5-pro`, `gemini-1.5-flash`
  - Best for: Cost-free usage, fast responses
- **OpenAI** (requires API key)
  - Models: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
  - Best for: Maximum quality, advanced reasoning

Configure in `.env`:
```env
# For Gemini (Free Tier)
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash

# For OpenAI (Paid)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4
```

## 📚 Documentation

- **[Functional Requirements](./FUNCTIONAL_REQUIREMENTS.md)** - Detailed system specifications (FR-1 through FR-18)
- **[Non-Functional Requirements](./NON_FUNCTIONAL_REQUIREMENTS.md)** - Performance, security, and quality requirements
- [Architecture Documentation](./docs/architecture/) - System design and diagrams
- [API Documentation](./docs/api/) - API endpoints and integration guides
- [Contributing Guidelines](./CONTRIBUTING.md) - How to contribute to the project

## 🚀 Getting Started

### Prerequisites

- Node.js >= 18.x
- Python >= 3.11
- PostgreSQL >= 15
### Prerequisites

- Python >= 3.11
- PostgreSQL >= 15
- Poetry (Python package manager)
- Node.js >= 18.x (for future frontend/extension)

### Backend Installation

```bash
# Clone the repository
git clone https://github.com/extremealexv/personal-ai-job-assistant.git
cd personal-ai-job-assistant/src/backend

# Install dependencies with Poetry
poetry install

# Activate virtual environment
poetry shell

# Set up database
python database/init_db.py --drop --seed

# Run migrations (if needed)
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### Configuration

Create a `.env` file in `src/backend/`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_job_assistant
DATABASE_ASYNC_URL=postgresql+asyncpg://user:password@localhost:5432/ai_job_assistant

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# AI Configuration - Google Gemini (Free Tier)
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.5-flash  # Free tier model
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=4000
GEMINI_MAX_RETRIES=3

# AI Configuration - OpenAI (Optional, Paid)
# OPENAI_API_KEY=your-openai-api-key
# OPENAI_MODEL=gpt-4
# OPENAI_TEMPERATURE=0.7
# OPENAI_MAX_TOKENS=4000

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=10
```

**Getting AI API Keys:**
- **Gemini (Free)**: Get key at [Google AI Studio](https://makersuite.google.com/app/apikey)
- **OpenAI (Paid)**: Get key at [OpenAI Platform](https://platform.openai.com/api-keys)

### Running Locally

```bash
# Start backend API
cd src/backend
poetry shell
uvicorn app.main:app --reload

# API will be available at:
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
# - Health check: http://localhost:8000/api/v1/health
```

## 🧪 Testing

### Running Tests

```bash
cd src/backend
poetry shell

# Run all tests with coverage
pytest --cov=app/services --cov=app/api/v1/endpoints --cov-report=term-missing

# Run specific test suites
pytest tests/unit/test_job_service.py -v              # Job management unit tests
pytest tests/integration/test_jobs_api.py -v          # Job management API tests
pytest tests/unit/test_application_service.py -v      # Application tracking unit tests
pytest tests/integration/test_applications_api.py -v  # Application tracking API tests
pytest tests/unit/test_cover_letter_service.py -v     # Cover letter unit tests
pytest tests/integration/test_cover_letters_api.py -v # Cover letter API tests

# Run all Issue #56 tests (Phases 1-3)
pytest tests/unit/test_job_service.py tests/integration/test_jobs_api.py \
       tests/unit/test_application_service.py tests/integration/test_applications_api.py \
       tests/unit/test_cover_letter_service.py tests/integration/test_cover_letters_api.py \
       -v --cov=app/services --cov=app/api/v1/endpoints

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v
```

### Test Results (Current)

**Total: 122 tests, 100% passing** ✅

| Module | Unit Tests | Integration Tests | Service Coverage | API Coverage |
|--------|-----------|------------------|------------------|--------------|
| Job Management | 23 | 24 | 98.13% | 86.05% |
| Application Tracking | 20 | 19 | 94.35% | 46.15% |
| Cover Letter Management | 18 | 18 | 95.74% | 89.74% |
| **Total** | **61** | **61** | **96.07% avg** | **73.98% avg** |

### Test Coverage

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html  # View in browser
```

**Current Coverage:**
- Core Services: 85-98%
- API Endpoints: 46-90%
- Overall Target: 80% (exceeded on all Issue #56 modules)

## 🗺️ Roadmap

See our [Project Board](../../projects) for current development status.

### Phase 1: Foundation ✅ (Completed)
- [x] Core backend API (FastAPI)
- [x] Database schema (PostgreSQL + SQLAlchemy)
- [x] Authentication system (JWT, bcrypt)
- [x] Resume Management System (Issue #54)
  - [x] Master resume upload and storage (PDF/DOCX)
  - [x] Structured data CRUD operations
  - [x] Resume versioning system
  - [x] Search and statistics features
  - [x] 33 REST API endpoints
  - [x] 100 tests (26 unit + 74 integration)

### Phase 2: Job & Application Management ✅ (Completed - Issue #56)
- [x] **Job Management System (Phase 1)**
  - [x] Job posting CRUD operations
  - [x] Job lifecycle tracking (saved → applied → interviewing → offer/rejected)
  - [x] Keyword extraction from descriptions
  - [x] Full-text search across jobs
  - [x] Interest level scoring and ATS detection
  - [x] 8 REST API endpoints
  - [x] 47 tests (23 unit + 24 integration)
- [x] **Application Tracking (Phase 2)**
  - [x] Application CRUD operations
  - [x] Application status tracking (draft → submitted → offer/rejected)
  - [x] Auto-sync job status on submission
  - [x] Follow-up date tracking
  - [x] Application statistics
  - [x] 7 REST API endpoints
  - [x] 39 tests (20 unit + 19 integration)
- [x] **Cover Letter Management (Phase 3)**
  - [x] Multiple versions per application
  - [x] Version activation control
  - [x] Content validation and tone selection
  - [x] AI metadata tracking
  - [x] 7 REST API endpoints
  - [x] 36 tests (18 unit + 18 integration)

### Phase 3: AI Integration (Next)
- [ ] Resume tailoring engine with prompt templates
- [ ] AI-powered cover letter generation
- [ ] Prompt management and versioning
- [ ] A/B testing for resume variations

### Phase 4: Browser Extension
- [ ] ATS platform detection (Workday, Greenhouse, Lever, etc.)
- [ ] Form autofill automation
- [ ] Submission automation (optional)

### Phase 5: Integrations
- [ ] Gmail integration for email tracking
- [ ] Google Calendar sync for interviews
- [ ] Analytics dashboard with metrics

## 📖 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
All endpoints (except health check) require JWT authentication:
```http
Authorization: Bearer <your_jwt_token>
```

### Job Management Endpoints

#### Create Job Posting
```http
POST /jobs
Content-Type: application/json

{
  "company_name": "TechCorp",
  "job_title": "Senior Backend Engineer",
  "job_url": "https://techcorp.com/jobs/123",
  "job_description": "We are looking for a senior backend engineer...",
  "location": "San Francisco, CA",
  "salary_range": "$150k-$200k",
  "interest_level": 5
}
```

#### List Jobs
```http
GET /jobs?page=1&page_size=10&status=saved&company=TechCorp&interest_level=5&sort_by=interest_level&sort_order=desc
```

#### Get Job by ID
```http
GET /jobs/{job_id}
```

#### Update Job
```http
PUT /jobs/{job_id}
Content-Type: application/json

{
  "job_title": "Updated Title",
  "notes": "Very interesting role"
}
```

#### Update Job Status
```http
PATCH /jobs/{job_id}/status
Content-Type: application/json

{
  "status": "applied"
}
```

#### Search Jobs
```http
GET /jobs/search?q=python+backend
```

#### Get Job Statistics
```http
GET /jobs/stats
```

Response:
```json
{
  "total_jobs": 25,
  "by_status": {
    "saved": 10,
    "applied": 8,
    "interviewing": 5,
    "offer": 2
  },
  "avg_interest_level": 3.8
}
```

### Application Management Endpoints

#### Create Application
```http
POST /applications
Content-Type: application/json

{
  "job_posting_id": "uuid-here",
  "resume_version_id": "uuid-here",
  "status": "draft",
  "demographics_data": {
    "veteran_status": "not_applicable",
    "disability_status": "no"
  }
}
```

#### List Applications
```http
GET /applications?page=1&page_size=10&status=submitted&job_posting_id=uuid-here&sort_by=submitted_at&sort_order=desc
```

#### Get Application by ID
```http
GET /applications/{application_id}
```

#### Update Application
```http
PUT /applications/{application_id}
Content-Type: application/json

{
  "status": "interviewing",
  "follow_up_notes": "Phone screen scheduled for next week"
}
```

#### Update Application Status
```http
PATCH /applications/{application_id}/status
Content-Type: application/json

{
  "status": "offer"
}
```

#### Get Application Statistics
```http
GET /applications/stats
```

Response:
```json
{
  "total_applications": 15,
  "by_status": {
    "submitted": 8,
    "interviewing": 5,
    "offer": 2
  },
  "response_rate": 53.3,
  "interview_rate": 33.3,
  "offer_rate": 13.3
}
```

### Cover Letter Management Endpoints

#### Create Cover Letter
```http
POST /cover-letters
Content-Type: application/json

{
  "application_id": "uuid-here",
  "content": "Dear Hiring Manager,\n\nI am excited to apply for this position...",
  "tone": "professional",
  "is_active": true
}
```

#### List Cover Letters
```http
GET /cover-letters?page=1&page_size=10&application_id=uuid-here&is_active=true&sort_by=version_number&sort_order=desc
```

#### Get All Versions for Application
```http
GET /cover-letters/application/{application_id}
```

Response:
```json
{
  "total": 3,
  "versions": [
    {
      "id": "uuid-3",
      "version_number": 3,
      "is_active": true,
      "content": "Latest version...",
      "created_at": "2025-12-28T10:00:00Z"
    },
    {
      "id": "uuid-2",
      "version_number": 2,
      "is_active": false,
      "content": "Second version...",
      "created_at": "2025-12-27T15:00:00Z"
    },
    {
      "id": "uuid-1",
      "version_number": 1,
      "is_active": false,
      "content": "First version...",
      "created_at": "2025-12-26T12:00:00Z"
    }
  ]
}
```

#### Get Cover Letter by ID
```http
GET /cover-letters/{cover_letter_id}
```

#### Update Cover Letter
```http
PUT /cover-letters/{cover_letter_id}
Content-Type: application/json

{
  "content": "Updated cover letter content...",
  "is_active": true
}
```

#### Activate Specific Version
```http
PATCH /cover-letters/application/{application_id}/activate/{version_number}
```

#### Delete Cover Letter
```http
DELETE /cover-letters/{cover_letter_id}
```

### Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message here"
}
```

Status codes:
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (no access to resource)
- `404` - Not Found
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

### Interactive API Documentation

FastAPI provides interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- [ ] Email classification

### Phase 5: Analytics & Optimization
- [ ] Performance metrics
- [ ] AI learning feedback loop
- [ ] Resume version optimization

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](./CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🔒 Security

This application handles sensitive personal information. Please review our [Security Policy](./SECURITY.md) before contributing or deploying.

For security concerns, please email: security@example.com

## 📞 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)

## 🙏 Acknowledgments

- Built with modern AI technologies
- Inspired by the need for efficient job search tools
- Community-driven development

---

**Note**: This is a single-user system designed for personal use. It is not intended as a multi-tenant SaaS platform.
#   T e s t 
 
 #   T e s t 
 
 