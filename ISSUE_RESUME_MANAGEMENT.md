# Issue: Resume Management System

**Labels:** `enhancement`, `backend`, `core-feature`, `high-priority`  
**Milestone:** Phase 1 - Foundation  
**Related Requirements:** FR-3 (Resume Management), FR-3.1-FR-3.4

---

## 📋 Overview

Implement comprehensive resume management functionality including:
- Master resume upload and parsing (PDF/DOCX)
- Structured data extraction and storage
- Resume versioning for job-specific customization
- Diff tracking between versions
- CRUD operations for resume components

This is a **foundational feature** - required before AI tailoring, applications, and other core functionality.

---

## 🎯 Objectives

1. **Enable users to upload their master resume** (PDF or DOCX)
2. **Parse resume into structured data** (work experience, education, skills, certifications)
3. **Store and manage resume data** using existing database schema
4. **Support resume versioning** for job-specific variants
5. **Track changes between versions** (diff tracking)
6. **Provide full CRUD operations** for all resume components

---

## 📚 Functional Requirements

### FR-3.1 — Master Resume Ingestion
- System SHALL accept PDF and DOCX file uploads
- System SHALL parse resume into structured fields:
  - Personal information (name, contact, location)
  - Work experience (company, title, dates, description, achievements)
  - Education (institution, degree, field, dates, GPA, honors)
  - Skills (categorized, with proficiency levels)
  - Certifications (name, issuer, dates, credential)

### FR-3.2 — Resume Normalization
- System SHALL normalize parsed data into canonical schema
- System SHALL preserve original wording and structure
- System SHALL handle various resume formats

### FR-3.3 — Resume Versioning
- System SHALL allow creation of resume versions from master
- Each version SHALL track:
  - Target job (optional)
  - Target role title
  - Modifications from master
  - Prompt configuration used (for AI-generated versions)

### FR-3.4 — Resume Editing
- System SHALL allow manual editing of any resume component
- System SHALL track changes between versions (JSON diff)
- System SHALL support viewing side-by-side comparisons

---

## 🏗️ Technical Architecture

### Database Tables (Already Defined)

**Primary Tables:**
1. `master_resumes` - Master resume record
2. `work_experiences` - Job history entries
3. `education` - Education history
4. `skills` - Skills inventory
5. `certifications` - Professional certifications
6. `resume_versions` - Derived resume variants

**Relationships:**
```
users (1) ──→ (1) master_resumes
              ↓
              ├──→ (many) work_experiences
              ├──→ (many) education
              ├──→ (many) skills
              └──→ (many) certifications
              
master_resumes (1) ──→ (many) resume_versions
```

### Technology Stack

**Resume Parsing:**
- **PDF**: PyPDF2 or pdfplumber (text extraction)
- **DOCX**: python-docx (text extraction)
- **Text Processing**: spaCy or regex patterns (structure extraction)
- **File Storage**: Local filesystem or S3-compatible (original files)

**API Framework:**
- FastAPI with async/await
- Multipart form data for file uploads
- Pydantic models for validation

**Testing:**
- pytest with sample resume files
- Factory pattern for test data
- Integration tests for file upload

---

## 🔧 Implementation Plan

### Phase 1: Basic Upload & Storage (3-4 hours)

**Goals:**
- Accept file uploads
- Store files and metadata
- Basic text extraction

**Tasks:**
1. Create file upload endpoint (`POST /api/v1/resumes/upload`)
2. Implement file validation (type, size)
3. Store files in filesystem
4. Extract raw text from PDF/DOCX
5. Create master resume record
6. Add basic error handling

**Deliverables:**
- Upload endpoint with validation
- File storage utility
- Basic text extraction
- Unit tests for validators

### Phase 2: Structured Data Extraction (5-6 hours)

**Goals:**
- Parse resume structure
- Extract entities (companies, dates, etc.)
- Store in normalized schema

**Tasks:**
1. Implement work experience parser
2. Implement education parser
3. Implement skills parser
4. Implement certifications parser
5. Create CRUD endpoints for each entity
6. Add validation for parsed data

**Deliverables:**
- Parsing utilities for each section
- CRUD endpoints for resume components
- Data validation and normalization
- Integration tests with sample resumes

### Phase 3: Resume Versioning (4-5 hours)

**Goals:**
- Create resume versions
- Track modifications
- Compare versions

**Tasks:**
1. Implement version creation endpoint
2. Store modifications as JSON diff
3. Implement version retrieval
4. Add version comparison endpoint
5. Support exporting versions (JSON)
6. Add version deletion

**Deliverables:**
- Versioning endpoints
- Diff tracking utility
- Comparison functionality
- Tests for version management

### Phase 4: Advanced Features (3-4 hours)

**Goals:**
- Search and filter
- Bulk operations
- Export capabilities

**Tasks:**
1. Add resume search/filter endpoint
2. Implement resume duplication
3. Add PDF/DOCX export (future)
4. Add resume statistics endpoint
5. Performance optimization

**Deliverables:**
- Search and filter functionality
- Export utilities
- Performance benchmarks
- Documentation updates

---

## 🔌 API Endpoints to Implement

### Master Resume Management

#### 1. Upload Master Resume
```http
POST /api/v1/resumes/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

Request Body:
- file: <binary> (PDF or DOCX, max 10MB)

Response 201:
{
  "id": "uuid",
  "filename": "john_doe_resume.pdf",
  "file_size": 245632,
  "status": "processing",
  "created_at": "2025-12-28T10:00:00Z"
}

Errors:
- 400: Invalid file type or size
- 413: File too large
- 401: Not authenticated
```

#### 2. Get Master Resume
```http
GET /api/v1/resumes/master
Authorization: Bearer <token>

Response 200:
{
  "id": "uuid",
  "user_id": "uuid",
  "original_filename": "resume.pdf",
  "file_path": "/uploads/...",
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "location": "New York, NY",
  "summary": "Experienced software engineer...",
  "created_at": "2025-12-28T10:00:00Z",
  "updated_at": "2025-12-28T10:00:00Z"
}
```

#### 3. Update Master Resume Metadata
```http
PUT /api/v1/resumes/master
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "location": "New York, NY",
  "summary": "Updated summary..."
}

Response 200: Updated resume object
```

#### 4. Delete Master Resume
```http
DELETE /api/v1/resumes/master
Authorization: Bearer <token>

Response 204: No Content
```

---

### Work Experience Management

#### 5. List Work Experiences
```http
GET /api/v1/resumes/work-experiences
Authorization: Bearer <token>

Response 200:
{
  "items": [
    {
      "id": "uuid",
      "company_name": "Tech Corp",
      "job_title": "Senior Software Engineer",
      "employment_type": "full_time",
      "start_date": "2020-01-01",
      "end_date": null,
      "is_current": true,
      "description": "Led development of...",
      "achievements": ["Increased performance by 40%"],
      "technologies": ["Python", "FastAPI", "PostgreSQL"],
      "display_order": 0
    }
  ],
  "total": 3
}
```

#### 6. Create Work Experience
```http
POST /api/v1/resumes/work-experiences
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_name": "Tech Corp",
  "job_title": "Senior Software Engineer",
  "employment_type": "full_time",
  "location": "Remote",
  "start_date": "2020-01-01",
  "end_date": null,
  "is_current": true,
  "description": "Led development...",
  "achievements": ["Achievement 1", "Achievement 2"],
  "technologies": ["Python", "FastAPI"]
}

Response 201: Created work experience object
```

#### 7. Update Work Experience
```http
PUT /api/v1/resumes/work-experiences/{id}
Authorization: Bearer <token>

Response 200: Updated work experience
```

#### 8. Delete Work Experience
```http
DELETE /api/v1/resumes/work-experiences/{id}
Authorization: Bearer <token>

Response 204: No Content
```

---

### Education Management

#### 9. List Education
```http
GET /api/v1/resumes/education
Authorization: Bearer <token>

Response 200:
{
  "items": [
    {
      "id": "uuid",
      "institution": "University Name",
      "degree_type": "bachelor",
      "field_of_study": "Computer Science",
      "start_date": "2015-09-01",
      "end_date": "2019-05-01",
      "gpa": 3.85,
      "honors": ["Dean's List", "Summa Cum Laude"],
      "display_order": 0
    }
  ],
  "total": 2
}
```

#### 10-12. Create, Update, Delete Education
Similar patterns to work experience endpoints.

---

### Skills Management

#### 13. List Skills
```http
GET /api/v1/resumes/skills
Authorization: Bearer <token>

Response 200:
{
  "items": [
    {
      "id": "uuid",
      "skill_name": "Python",
      "category": "programming_language",
      "proficiency_level": "Expert",
      "years_of_experience": 8,
      "display_order": 0
    }
  ],
  "total": 25
}
```

#### 14-16. Create, Update, Delete Skills
Similar CRUD patterns.

---

### Certifications Management

#### 17. List Certifications
```http
GET /api/v1/resumes/certifications
Authorization: Bearer <token>

Response 200:
{
  "items": [
    {
      "id": "uuid",
      "certification_name": "AWS Solutions Architect",
      "issuing_organization": "Amazon Web Services",
      "issue_date": "2023-06-01",
      "expiration_date": "2026-06-01",
      "credential_id": "AWS-12345",
      "credential_url": "https://..."
    }
  ],
  "total": 3
}
```

#### 18-20. Create, Update, Delete Certifications
Similar CRUD patterns.

---

### Resume Versioning

#### 21. List Resume Versions
```http
GET /api/v1/resumes/versions
Authorization: Bearer <token>

Response 200:
{
  "items": [
    {
      "id": "uuid",
      "version_name": "Senior Backend Engineer - TechCorp",
      "target_role": "Senior Backend Engineer",
      "target_company": "TechCorp",
      "job_posting_id": "uuid",
      "times_used": 5,
      "applications_count": 3,
      "created_at": "2025-12-28T10:00:00Z"
    }
  ],
  "total": 10
}
```

#### 22. Create Resume Version
```http
POST /api/v1/resumes/versions
Authorization: Bearer <token>
Content-Type: application/json

{
  "version_name": "Backend Engineer - StartupXYZ",
  "target_role": "Backend Engineer",
  "target_company": "StartupXYZ",
  "job_posting_id": "uuid",
  "modifications": {
    "summary": "Tailored summary...",
    "work_experiences": {
      "uuid": { "description": "Modified description..." }
    }
  }
}

Response 201: Created version
```

#### 23. Get Resume Version
```http
GET /api/v1/resumes/versions/{id}
Authorization: Bearer <token>

Response 200: Full resume version with all components
```

#### 24. Compare Resume Versions
```http
GET /api/v1/resumes/versions/{id}/diff?compare_to={other_id}
Authorization: Bearer <token>

Response 200:
{
  "added": {...},
  "removed": {...},
  "modified": {...}
}
```

#### 25. Delete Resume Version
```http
DELETE /api/v1/resumes/versions/{id}
Authorization: Bearer <token>

Response 204: No Content
```

---

## 🧪 Testing Strategy

### Unit Tests (pytest)

**Files to create:**
- `tests/test_resume_parser.py` - Resume parsing logic
- `tests/test_resume_validation.py` - Data validation
- `tests/test_resume_diff.py` - Version comparison

**Coverage targets:**
- Resume parsing utilities: 90%+
- Validation logic: 95%+
- CRUD operations: 85%+

**Test cases:**
```python
class TestResumeParser:
    def test_parse_pdf_resume()
    def test_parse_docx_resume()
    def test_extract_work_experience()
    def test_extract_education()
    def test_extract_skills()
    def test_extract_contact_info()
    def test_handle_malformed_resume()
    def test_handle_empty_resume()

class TestResumeValidation:
    def test_validate_work_dates()
    def test_validate_education_dates()
    def test_validate_email_format()
    def test_validate_phone_format()
    def test_reject_invalid_file_type()
    def test_reject_oversized_file()

class TestResumeDiff:
    def test_detect_added_content()
    def test_detect_removed_content()
    def test_detect_modified_content()
    def test_generate_diff_summary()
```

### Integration Tests (pytest + AsyncClient)

**Files to create:**
- `tests/test_resume_endpoints.py` - API endpoint tests

**Test cases:**
```python
class TestResumeUpload:
    async def test_upload_pdf_success()
    async def test_upload_docx_success()
    async def test_upload_invalid_type()
    async def test_upload_too_large()
    async def test_upload_requires_auth()

class TestWorkExperienceEndpoints:
    async def test_create_work_experience()
    async def test_list_work_experiences()
    async def test_update_work_experience()
    async def test_delete_work_experience()
    async def test_reorder_work_experiences()

class TestResumeVersioning:
    async def test_create_version()
    async def test_list_versions()
    async def test_get_version_details()
    async def test_compare_versions()
    async def test_delete_version()
```

### Manual Testing

**Test data needed:**
- 3-5 sample resume PDFs (different formats)
- 3-5 sample resume DOCX files
- Edge cases: multi-column layouts, images, tables

**Manual test script:** `scripts/test_resume.sh`
```bash
# Upload resume
# Get master resume
# Create work experience
# Update work experience
# Create resume version
# Compare versions
# Export version
```

---

## 📝 Documentation Requirements

### 1. API Documentation

**Update:** `docs/API_ENDPOINTS.md`

Add comprehensive section for Resume Management:
- All 25 endpoints with examples
- Request/response schemas
- Error codes and handling
- File upload guidelines
- Versioning workflow

### 2. User Guide

**Create:** `docs/RESUME_MANAGEMENT.md`

Content:
- How to upload a resume
- Understanding resume structure
- Creating resume versions
- Comparing versions
- Best practices for resume data

### 3. Developer Documentation

**Update:** `docs/DEVELOPMENT.md`

Add sections:
- Resume parsing implementation
- File storage configuration
- Adding new resume parsers
- Extending version diff logic

### 4. Testing Documentation

**Update:** `README_TESTING.md`

Add:
- Resume testing instructions
- Sample resume files location
- Test data generation
- Coverage requirements

### 5. Code Documentation

**Requirements:**
- Docstrings for all public functions (Google style)
- Type hints for all functions
- Comments for complex parsing logic
- README in parsing utilities folder

---

## ✅ Acceptance Criteria

### Phase 1 Completion:
- [ ] User can upload PDF resume successfully
- [ ] User can upload DOCX resume successfully
- [ ] File validation prevents invalid uploads
- [ ] Master resume record created in database
- [ ] Raw text extracted and stored
- [ ] API returns proper error messages
- [ ] Unit tests pass (80%+ coverage)

### Phase 2 Completion:
- [ ] Work experiences parsed and stored correctly
- [ ] Education parsed and stored correctly
- [ ] Skills parsed and stored correctly
- [ ] Certifications parsed and stored correctly
- [ ] CRUD endpoints work for all components
- [ ] Data validation prevents invalid entries
- [ ] Integration tests pass with sample resumes

### Phase 3 Completion:
- [ ] Resume versions can be created from master
- [ ] Modifications tracked as JSON diff
- [ ] Version comparison shows differences
- [ ] Version retrieval includes all components
- [ ] Version deletion works correctly
- [ ] Tests cover version management

### Phase 4 Completion:
- [ ] Search and filter functionality working
- [ ] Resume statistics endpoint functional
- [ ] Performance meets requirements (<2s response times)
- [ ] All documentation updated
- [ ] Manual testing script passes

### Overall Completion:
- [ ] All 25 API endpoints implemented and tested
- [ ] Test coverage ≥ 85% for resume module
- [ ] All integration tests passing
- [ ] Manual testing complete with real resumes
- [ ] API documentation complete
- [ ] Code reviewed and merged

---

## 🔗 Dependencies

### Required Before Starting:
- [x] Issue #52 - Authentication system (completed)
- [x] Database schema for resume tables (defined)
- [x] User model and authentication (completed)

### Python Packages to Add:
```toml
# pyproject.toml
[tool.poetry.dependencies]
PyPDF2 = "^3.0.0"              # PDF text extraction
python-docx = "^1.1.0"         # DOCX text extraction
python-magic = "^0.4.27"       # File type detection
Pillow = "^10.1.0"             # Image handling (if needed)
aiofiles = "^23.2.1"           # Async file operations
```

### Optional (Future):
- spaCy - Advanced NLP parsing
- pdfplumber - Better PDF parsing
- textract - Universal document extraction

---

## 📊 Estimated Effort

**Total Time:** 15-19 hours over 2-3 days

**Breakdown:**
- Phase 1 (Upload & Storage): 3-4 hours
- Phase 2 (Structured Parsing): 5-6 hours
- Phase 3 (Versioning): 4-5 hours
- Phase 4 (Advanced Features): 3-4 hours

**Complexity:** Medium
- File handling: Straightforward
- Resume parsing: Moderate challenge
- Versioning: Well-defined schema
- Testing: Requires sample resumes

---

## 🚧 Known Challenges

### 1. Resume Format Variability
**Challenge:** Resumes come in many formats
**Mitigation:** 
- Start with common patterns
- Use regex and NLP for extraction
- Allow manual editing of parsed data
- Iterate based on parsing accuracy

### 2. Text Extraction Quality
**Challenge:** PDFs may have poor text extraction
**Mitigation:**
- Use multiple parsing libraries
- Provide preview before finalizing
- Allow re-upload if parsing fails
- Support manual data entry

### 3. Large File Handling
**Challenge:** Large resumes may slow down processing
**Mitigation:**
- Set 10MB file size limit
- Use async file operations
- Process parsing in background (future: Celery)
- Show progress indicator

### 4. Version Diff Complexity
**Challenge:** Tracking changes between versions
**Mitigation:**
- Store modifications as JSON
- Use simple dict comparison
- Focus on key fields first
- Improve diff algorithm over time

---

## 🎯 Success Metrics

After implementation:
- [ ] Users can upload resumes in <5 seconds
- [ ] Parsing accuracy >80% for common formats
- [ ] All CRUD operations <500ms (p95)
- [ ] Version creation <1 second
- [ ] Zero data loss during operations
- [ ] Test coverage ≥85%
- [ ] API documentation complete
- [ ] Manual testing passes with 5 different resumes

---

## 🔄 Future Enhancements (Not in Scope)

1. **AI-powered parsing** - Use LLMs for better extraction
2. **Resume templates** - Pre-designed layouts
3. **Export to PDF/DOCX** - Generate formatted resumes
4. **Parsing improvement ML** - Learn from corrections
5. **Batch upload** - Multiple resume versions at once
6. **Resume analytics** - Track which sections perform best
7. **Integration with LinkedIn** - Import profile data
8. **Collaborative editing** - Future multi-user support

---

## 📌 Related Issues

- #52 - JWT Authentication (prerequisite - completed)
- Future: AI Resume Tailoring (depends on this issue)
- Future: Application Management (depends on this issue)

---

## 💡 Notes

- This is a **foundational feature** - critical for project success
- Focus on reliable parsing over perfect parsing
- Manual editing capability is essential fallback
- Version diff tracking enables future AI optimization
- File storage strategy should be production-ready from start

---

**Ready to implement?** Create a new branch `feature/resume-management` and follow the phase-by-phase plan!
