# Changelog

All notable changes to the Personal AI Job Assistant project will be documented in this file.
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### AI Resume Tailoring System (AI Integration - Phase 1) 🤖
- **AI-Powered Resume Optimization**
  - Automatic resume tailoring for specific job postings
  - Keyword extraction and relevance matching from job descriptions
  - Executive-level positioning with quantifiable impact statements
  - ATS optimization for applicant tracking systems
  - Resume version creation with tracked modifications
- **Multi-Provider AI Support**
  - Google Gemini integration (free tier: gemini-2.5-flash)
  - OpenAI GPT integration (gpt-4, gpt-3.5-turbo)
  - Flexible provider abstraction for future expansion
  - Configurable model parameters (temperature, max tokens)
- **Prompt Template Management**
  - Customizable prompt templates per role type
  - Version tracking for prompts
  - Default prompts with role-specific optimization
  - Support for user-defined custom prompts
- **Advanced JSON Parsing**
  - Flexible markdown code block extraction
  - Multiple regex patterns for AI response parsing
  - Fallback mechanisms for plain JSON
  - Comprehensive error handling and logging
- **API Endpoints**
  - POST /api/v1/ai/resume/tailor - Generate tailored resume
  - GET /api/v1/ai/resume/versions - List resume versions
  - GET /api/v1/ai/resume/versions/{id} - Get version by ID
  - PUT /api/v1/ai/resume/versions/{id} - Update version
  - DELETE /api/v1/ai/resume/versions/{id} - Delete version
- **Testing**
  - 30+ unit tests for service layer
  - 15+ integration tests for API endpoints
  - Mock AI provider for deterministic testing
  - Edge case coverage (invalid JSON, API failures)
- **Performance**
  - ~8-10 second generation time
  - Zero-cost operation with Gemini free tier
  - Retry logic with exponential backoff
  - Rate limiting support

#### AI Cover Letter Generation System (AI Integration - Phase 2) 🤖
- **AI-Generated Cover Letters**
  - Personalized cover letter generation per application
  - Company and role-specific customization
  - Resume summary integration with job requirements
  - Executive-level persuasive writing
  - Quantifiable impact storytelling
- **Tone Customization**
  - Professional tone (default)
  - Enthusiastic tone (high energy)
  - Formal tone (traditional business)
  - Creative tone (innovative industries)
- **Version Management**
  - Multiple cover letter versions per application
  - Auto-incrementing version numbers
  - Version activation/deactivation control
  - Content validation (100-10,000 characters)
- **Content Extraction**
  - Flexible markdown code block handling
  - Plain text extraction from AI responses
  - Automatic whitespace trimming
  - Content validation and sanitization
- **API Endpoints**
  - POST /api/v1/ai/cover-letter/generate - Generate cover letter
  - GET /api/v1/ai/cover-letter/list - List all versions for application
  - GET /api/v1/ai/cover-letter/{id} - Get cover letter by ID
  - PUT /api/v1/ai/cover-letter/{id} - Update cover letter
  - PATCH /api/v1/ai/cover-letter/{id}/activate - Activate version
  - DELETE /api/v1/ai/cover-letter/{id} - Delete cover letter
- **Testing**
  - 25+ unit tests for service layer
  - 20+ integration tests for API endpoints
  - Mock AI provider for consistent test results
  - Version management test coverage
- **Performance**
  - ~8-10 second generation time
  - Zero-cost operation with Gemini free tier
  - Efficient resume summary creation

#### Google Gemini Provider Implementation
- **Core Integration**
  - Full Google Generative AI SDK integration
  - Support for Gemini 1.5 and 2.0/2.5 models
  - Free tier models (gemini-2.0-flash, gemini-2.5-flash)
  - Paid models (gemini-1.5-pro, gemini-1.5-flash)
- **Features**
  - Async API calls with asyncio.to_thread
  - Usage tracking and cost calculation
  - Token counting (prompt, completion, total)
  - Content filtering and safety settings
  - Retry logic with exponential backoff
- **Error Handling**
  - Rate limit detection and retry
  - Invalid API key detection
  - Model not found handling
  - Token limit exceeded handling
  - Content filtering detection
- **Cost Tracking**
  - Per-model pricing configuration
  - Usage statistics by user
  - Request/token/cost aggregation
  - Free tier model identification

#### Bug Fixes and Improvements
- **JSON Parsing Enhancement**
  - Fixed regex pattern from `\n(.*?)\n` to `\s*(.*?)\s*`
  - Added fallback pattern `\{.*\}` for plain JSON
  - Comprehensive logging for debugging
  - Fixed missing return statement in extraction method
- **Async Database Session Handling**
  - Added `await db.refresh(application, ["job_posting"])` for eager loading
  - Fixed MissingGreenlet error in applications endpoint
  - Proper relationship loading before session close
- **Import Path Corrections**
  - Fixed `app.api.v1.dependencies` → `app.api.deps`
  - Consistent import structure across endpoints
- **Authentication Field Alignment**
  - Documented login endpoint expects "email" not "username"
  - Updated test fixtures and documentation

### Changed
- AI provider abstraction supports multiple backends
- Resume tailoring now creates resume_version records
- Cover letter generation integrates with application workflow
- Improved error messages for AI API failures

### Fixed
- JSON parsing now handles Gemini markdown code blocks
- Async session properly refreshes relationships before access
- Cover letter test content meets validation requirements
- Import paths consistent across all AI endpoints

#### Job Management System (Issue #56 - Phase 1)
- **Job Posting Management**
  - Create, read, update, delete job postings
  - URL validation and job source tracking (manual/extension/API)
  - ATS platform detection (Workday, Greenhouse, etc.)
  - Job lifecycle states: saved → prepared → applied → interviewing → rejected/offer/closed
  - Interest level scoring (1-5)
  - Keyword extraction from job descriptions
  - Full-text search across job descriptions
- **8 REST API Endpoints**
  - POST /api/v1/jobs - Create job posting
  - GET /api/v1/jobs - List jobs with pagination/filters
  - GET /api/v1/jobs/{id} - Get job by ID
  - PUT /api/v1/jobs/{id} - Update job
  - PATCH /api/v1/jobs/{id}/status - Update job status
  - DELETE /api/v1/jobs/{id} - Delete job
  - GET /api/v1/jobs/search - Search jobs by keyword
  - GET /api/v1/jobs/stats - Get job statistics
- **47 Tests** (23 unit + 24 integration, 100% pass rate)
- **Coverage**: 98.13% service layer, 86.05% API layer

#### Application Tracking System (Issue #56 - Phase 2)
- **Application Management**
  - Create applications linked to jobs and resume versions
  - Track submission details (date, method)
  - Application lifecycle states: draft → submitted → viewed → phone_screen → technical → onsite → offer → accepted/rejected/withdrawn
  - Auto-sync job status when application is submitted
  - Demographics data storage (JSONB)
  - Follow-up tracking (last/next dates, notes)
- **7 REST API Endpoints**
  - POST /api/v1/applications - Create application
  - GET /api/v1/applications - List applications with pagination/filters
  - GET /api/v1/applications/{id} - Get application by ID
  - PUT /api/v1/applications/{id} - Update application
  - PATCH /api/v1/applications/{id}/status - Update application status
  - DELETE /api/v1/applications/{id} - Delete application
  - GET /api/v1/applications/stats - Get application statistics
- **39 Tests** (20 unit + 19 integration, 100% pass rate)
- **Coverage**: 94.35% service layer, 46.15% API layer

#### Cover Letter Management System (Issue #56 - Phase 3)
- **Cover Letter Versioning**
  - Create multiple cover letter versions per application
  - Auto-incrementing version numbers (1, 2, 3...)
  - First version automatically set as active
  - Only one active version per application
  - Content validation (100-10,000 characters)
  - Tone selection (professional/enthusiastic/formal/creative)
  - AI generation metadata (model, prompt template tracking)
- **Version Management**
  - Get all versions for an application
  - Activate specific version (auto-deactivates others)
  - Update cover letter content and metadata
  - Delete versions with authorization checks
- **7 REST API Endpoints**
  - POST /api/v1/cover-letters - Create cover letter
  - GET /api/v1/cover-letters - List cover letters with pagination/filters
  - GET /api/v1/cover-letters/application/{id} - Get all versions
  - GET /api/v1/cover-letters/{id} - Get cover letter by ID
  - PUT /api/v1/cover-letters/{id} - Update cover letter
  - PATCH /api/v1/cover-letters/application/{id}/activate/{version} - Activate version
  - DELETE /api/v1/cover-letters/{id} - Delete cover letter
- **36 Tests** (18 unit + 18 integration, 100% pass rate)
- **Coverage**: 95.74% service layer, 89.74% API layer

#### Resume Management System (Issue #54)
- Master resume upload with PDF/DOCX parsing (PyPDF2, python-docx)
- Text extraction and structured data storage
- Work experience CRUD operations (create, read, update, delete)
- Education history management
- Skills tracking with categorization
- Professional certifications management
- Resume version management with job-specific modifications
- Advanced features: search across resume data, statistics dashboard, version duplication
- 33 REST API endpoints for complete resume lifecycle
- 26 pytest unit tests (100% pass rate)
- 74 bash integration tests (98.7% pass rate)
- Test coverage: 77% overall

### Changed
- Updated async_client fixture to follow redirects (fixes 307 redirect issues in tests)
- Improved test fixtures for cover letters to meet validation requirements

### Fixed
- Cover letter test content now meets 100-character minimum validation
- Cover letter fixtures properly configured with valid content
- Test authentication expectations aligned (403 instead of 401 for consistency)

### Security
- User-scoped authorization on all job, application, and cover letter operations
- Prevents cross-user data access
- SQL injection protection via SQLAlchemy parameterized queries

## [0.1.0] - TBD

### Added
- Project initialization
- Basic repository structure

---

## How to Update This Changelog

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities

When releasing a new version:
1. Move items from [Unreleased] to a new version section
2. Update the version number and date
3. Add a link to the version comparison at the bottom

[Unreleased]: https://github.com/extremealexv/personal-ai-job-assistant/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/extremealexv/personal-ai-job-assistant/releases/tag/v0.1.0
## [0.1.0] - 2025-12-26

### Added
- Project initialization
- Repository setup
- Basic documentation structure

---

## Version Guidelines

### Version Format: MAJOR.MINOR.PATCH

- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible functionality additions
- **PATCH**: Backward-compatible bug fixes

### Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes

### Example Entry

```markdown
## [1.2.3] - 2025-01-15

### Added
- Resume parsing for PDF format (#45)
- Workday ATS support in browser extension (#52)

### Changed
- Improved AI prompt for cover letter generation (#48)
- Updated authentication flow (#50)

### Fixed
- Resume parser encoding issue (#47)
- Extension manifest v3 compatibility (#51)

### Security
- Updated dependencies with security patches (#49)
```
