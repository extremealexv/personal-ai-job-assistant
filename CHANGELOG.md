# Changelog

All notable changes to the Personal AI Job Assistant project will be documented in this file.
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
