# API Endpoints Documentation

**Personal AI Job Assistant - Backend API**  
**Base URL:** `http://localhost:8000`  
**API Version:** v1  
**OpenAPI Docs:** `/docs` (Swagger UI) | `/redoc` (ReDoc)

---

## Table of Contents

- [Authentication](#authentication)
- [Health Endpoints](#health-endpoints)
- [User Management](#user-management)
- [Resume Management](#resume-management)
- [Job Management](#job-management)
- [Application Management](#application-management)
- [AI Services](#ai-services)
- [Common Response Formats](#common-response-formats)

---

## Authentication

All endpoints except health checks and documentation require authentication.

### Authentication Header

```http
Authorization: Bearer <jwt_token>
```

### Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated",
  "status_code": 401,
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Health Endpoints

### Root Endpoint

**GET** `/`

Returns welcome message and API status.

**Response 200:**
```json
{
  "message": "Personal AI Job Assistant API",
  "version": "1.0.0",
  "status": "healthy"
}
```

**Example:**
```bash
curl http://localhost:8000/
```

---

### Basic Health Check

**GET** `/health`

Quick health status check.

**Response 200:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-27T10:30:00Z"
}
```

**Headers:**
```
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

---

### API Health Check

**GET** `/api/v1/health`

Detailed health check including database status.

**Response 200:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "timestamp": "2025-12-27T10:30:00Z"
}
```

**Response 503 (Service Unavailable):**
```json
{
  "status": "unhealthy",
  "version": "1.0.0",
  "database": "disconnected",
  "timestamp": "2025-12-27T10:30:00Z",
  "error": "Database connection failed"
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/health
```

---

## User Management

### Register User

**POST** `/api/v1/users/register`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

**Response 201:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "email_verified": false,
  "created_at": "2025-12-27T10:30:00Z"
}
```

**Response 400 (Validation Error):**
```json
{
  "detail": "Email already registered",
  "status_code": 400,
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### Login

**POST** `/api/v1/users/login`

Authenticate and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

---

### Get Current User

**GET** `/api/v1/users/me`

Get authenticated user's profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "location": "San Francisco, CA",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "github_url": "https://github.com/johndoe",
  "is_active": true,
  "email_verified": false,
  "created_at": "2025-12-27T10:30:00Z",
  "updated_at": "2025-12-27T10:30:00Z"
}
```

---

### Update User Profile

**PATCH** `/api/v1/users/me`

Update user profile information.

**Request Body:**
```json
{
  "full_name": "John A. Doe",
  "phone": "+1234567890",
  "location": "San Francisco, CA",
  "linkedin_url": "https://linkedin.com/in/johndoe"
}
```

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John A. Doe",
  "phone": "+1234567890",
  "location": "San Francisco, CA",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "updated_at": "2025-12-27T11:00:00Z"
}
```

---

## Resume Management

### Upload Master Resume

**POST** `/api/v1/resumes/upload`

Upload and parse a resume file (PDF/DOCX).

**Content-Type:** `multipart/form-data`

**Form Data:**
- `file`: Resume file (PDF or DOCX, max 10MB)

**Response 201:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "original_filename": "resume.pdf",
  "file_size_bytes": 245760,
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "summary": "Experienced software engineer...",
  "created_at": "2025-12-27T10:30:00Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/resumes/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@resume.pdf"
```

---

### Get Master Resume

**GET** `/api/v1/resumes/master`

Get the master resume with all sections.

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "location": "San Francisco, CA",
  "summary": "Experienced software engineer with 8 years...",
  "work_experiences": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "company_name": "Tech Corp",
      "job_title": "Senior Software Engineer",
      "employment_type": "FULL_TIME",
      "location": "San Francisco, CA",
      "start_date": "2020-01-15",
      "end_date": null,
      "is_current": true,
      "description": "Lead backend development team...",
      "achievements": [
        "Improved API performance by 40%",
        "Mentored 5 junior engineers"
      ],
      "technologies": ["Python", "FastAPI", "PostgreSQL"]
    }
  ],
  "education": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "institution": "University of California",
      "degree_type": "BACHELOR",
      "field_of_study": "Computer Science",
      "start_date": "2012-09-01",
      "end_date": "2016-05-15",
      "gpa": 3.75
    }
  ],
  "skills": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440004",
      "skill_name": "Python",
      "category": "PROGRAMMING_LANGUAGE",
      "proficiency_level": "Expert",
      "years_of_experience": 8
    }
  ],
  "certifications": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440005",
      "certification_name": "AWS Certified Solutions Architect",
      "issuing_organization": "Amazon Web Services",
      "issue_date": "2023-06-15",
      "expiration_date": "2026-06-15"
    }
  ],
  "created_at": "2025-12-27T10:30:00Z",
  "updated_at": "2025-12-27T10:30:00Z"
}
```

---

### Create Resume Version

**POST** `/api/v1/resumes/versions`

Create a tailored resume version for a specific job.

**Request Body:**
```json
{
  "job_posting_id": "550e8400-e29b-41d4-a716-446655440010",
  "version_name": "Senior Backend Engineer - TechCorp",
  "target_role": "Senior Backend Engineer",
  "target_company": "TechCorp",
  "prompt_template_id": "550e8400-e29b-41d4-a716-446655440020"
}
```

**Response 201:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440006",
  "master_resume_id": "550e8400-e29b-41d4-a716-446655440001",
  "job_posting_id": "550e8400-e29b-41d4-a716-446655440010",
  "version_name": "Senior Backend Engineer - TechCorp",
  "target_role": "Senior Backend Engineer",
  "target_company": "TechCorp",
  "modifications": {
    "summary": "Optimized for backend engineering role",
    "work_experiences": [...]
  },
  "pdf_file_path": "/resumes/versions/550e8400.pdf",
  "created_at": "2025-12-27T10:30:00Z"
}
```

---

### List Resume Versions

**GET** `/api/v1/resumes/versions`

Get all resume versions.

**Query Parameters:**
- `job_posting_id` (optional): Filter by job posting
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Page size (default: 50, max: 100)

**Response 200:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440006",
      "version_name": "Senior Backend Engineer - TechCorp",
      "target_role": "Senior Backend Engineer",
      "target_company": "TechCorp",
      "times_used": 1,
      "applications_count": 1,
      "response_rate": 0.0,
      "created_at": "2025-12-27T10:30:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

---

## Job Management

### Create Job Posting

**POST** `/api/v1/jobs`

Save a job posting.

**Request Body:**
```json
{
  "company_name": "TechCorp",
  "job_title": "Senior Backend Engineer",
  "job_url": "https://techcorp.com/careers/123",
  "location": "San Francisco, CA",
  "job_description": "We are looking for...",
  "requirements": "5+ years of Python experience...",
  "interest_level": 5,
  "notes": "Great company culture"
}
```

**Response 201:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "company_name": "TechCorp",
  "job_title": "Senior Backend Engineer",
  "job_url": "https://techcorp.com/careers/123",
  "location": "San Francisco, CA",
  "status": "SAVED",
  "interest_level": 5,
  "extracted_keywords": ["Python", "FastAPI", "PostgreSQL", "AWS"],
  "created_at": "2025-12-27T10:30:00Z"
}
```

---

### List Job Postings

**GET** `/api/v1/jobs`

Get all saved job postings.

**Query Parameters:**
- `status` (optional): Filter by status (SAVED, PREPARED, APPLIED, etc.)
- `company_name` (optional): Filter by company
- `skip` (optional): Pagination offset
- `limit` (optional): Page size (max: 100)

**Response 200:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440010",
      "company_name": "TechCorp",
      "job_title": "Senior Backend Engineer",
      "location": "San Francisco, CA",
      "status": "SAVED",
      "interest_level": 5,
      "created_at": "2025-12-27T10:30:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

---

### Get Job Posting

**GET** `/api/v1/jobs/{job_id}`

Get a specific job posting by ID.

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "company_name": "TechCorp",
  "job_title": "Senior Backend Engineer",
  "job_url": "https://techcorp.com/careers/123",
  "location": "San Francisco, CA",
  "salary_range": "$150k-$200k",
  "employment_type": "Full-time",
  "remote_policy": "Hybrid",
  "job_description": "We are looking for...",
  "requirements": "5+ years of Python experience...",
  "status": "SAVED",
  "interest_level": 5,
  "notes": "Great company culture",
  "extracted_keywords": ["Python", "FastAPI", "PostgreSQL"],
  "created_at": "2025-12-27T10:30:00Z",
  "updated_at": "2025-12-27T10:30:00Z"
}
```

---

### Update Job Posting

**PATCH** `/api/v1/jobs/{job_id}`

Update job posting information or status.

**Request Body:**
```json
{
  "status": "PREPARED",
  "interest_level": 4,
  "notes": "Updated notes after research"
}
```

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "status": "PREPARED",
  "interest_level": 4,
  "notes": "Updated notes after research",
  "status_updated_at": "2025-12-27T11:00:00Z",
  "updated_at": "2025-12-27T11:00:00Z"
}
```

---

## Application Management

### Create Application

**POST** `/api/v1/applications`

Create an application for a job posting.

**Request Body:**
```json
{
  "job_posting_id": "550e8400-e29b-41d4-a716-446655440010",
  "resume_version_id": "550e8400-e29b-41d4-a716-446655440006",
  "cover_letter": "Dear Hiring Manager...",
  "demographics_data": {
    "gender": "Prefer not to say",
    "veteran_status": "Not applicable"
  }
}
```

**Response 201:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440015",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_posting_id": "550e8400-e29b-41d4-a716-446655440010",
  "resume_version_id": "550e8400-e29b-41d4-a716-446655440006",
  "status": "DRAFT",
  "created_at": "2025-12-27T10:30:00Z"
}
```

---

### Submit Application

**POST** `/api/v1/applications/{application_id}/submit`

Mark application as submitted.

**Request Body:**
```json
{
  "submission_method": "extension",
  "submitted_at": "2025-12-27T11:00:00Z"
}
```

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440015",
  "status": "SUBMITTED",
  "submitted_at": "2025-12-27T11:00:00Z",
  "submission_method": "extension"
}
```

---

### List Applications

**GET** `/api/v1/applications`

Get all applications.

**Query Parameters:**
- `status` (optional): Filter by status
- `job_posting_id` (optional): Filter by job
- `skip` (optional): Pagination offset
- `limit` (optional): Page size

**Response 200:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440015",
      "job_posting": {
        "company_name": "TechCorp",
        "job_title": "Senior Backend Engineer"
      },
      "status": "SUBMITTED",
      "submitted_at": "2025-12-27T11:00:00Z",
      "created_at": "2025-12-27T10:30:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

---

## AI Services

### Generate Cover Letter

**POST** `/api/v1/ai/cover-letter`

Generate an AI-powered cover letter.

**Request Body:**
```json
{
  "job_posting_id": "550e8400-e29b-41d4-a716-446655440010",
  "resume_version_id": "550e8400-e29b-41d4-a716-446655440006",
  "prompt_template_id": "550e8400-e29b-41d4-a716-446655440020",
  "tone": "professional"
}
```

**Response 200:**
```json
{
  "cover_letter": "Dear Hiring Manager,\n\nI am writing to express...",
  "word_count": 350,
  "generated_at": "2025-12-27T10:30:00Z",
  "model_used": "gpt-4"
}
```

---

### Tailor Resume

**POST** `/api/v1/ai/tailor-resume`

Use AI to optimize resume for a job posting.

**Request Body:**
```json
{
  "master_resume_id": "550e8400-e29b-41d4-a716-446655440001",
  "job_posting_id": "550e8400-e29b-41d4-a716-446655440010",
  "prompt_template_id": "550e8400-e29b-41d4-a716-446655440020"
}
```

**Response 200:**
```json
{
  "resume_version_id": "550e8400-e29b-41d4-a716-446655440006",
  "modifications": {
    "summary": "Optimized summary...",
    "keywords_added": ["Python", "FastAPI", "PostgreSQL"],
    "sections_reordered": true
  },
  "generated_at": "2025-12-27T10:30:00Z"
}
```

---

## Common Response Formats

### Success Response

```json
{
  "data": { ... },
  "message": "Operation successful",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Error Response

```json
{
  "detail": "Error message",
  "status_code": 400,
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

### Pagination Response

```json
{
  "items": [...],
  "total": 100,
  "skip": 0,
  "limit": 50,
  "has_more": true
}
```

---

## HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Request successful, no content returned
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., duplicate email)
- `422 Unprocessable Entity` - Validation errors
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

---

## Rate Limiting

API requests are rate limited to prevent abuse:

- **Authenticated requests:** 1000 requests/hour
- **Unauthenticated requests:** 100 requests/hour

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640606400
```

---

## Interactive Documentation

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

These provide interactive API documentation where you can:
- Browse all endpoints
- Test API calls directly
- View request/response schemas
- Generate code snippets

---

## Need Help?

- **Issues:** [GitHub Issues](https://github.com/extremealexv/personal-ai-job-assistant/issues)
- **Discussions:** [GitHub Discussions](https://github.com/extremealexv/personal-ai-job-assistant/discussions)
- **Documentation:** [Project README](../../../README.md)
