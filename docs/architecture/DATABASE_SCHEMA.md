# Database Schema Design

**Project:** Personal AI Job Search Assistant  
**Database:** PostgreSQL 15+  
**Date:** December 26, 2025

---

## Overview

This schema is designed for a **single-user** job application management system with:
- Structured resume data with versioning
- Job posting tracking with lifecycle states
- AI prompt management
- Application tracking with email integration
- Encrypted credential storage

---

## Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│    User     │────────▶│MasterResume  │────────▶│ResumeVersion│
└─────────────┘         └──────────────┘         └─────────────┘
      │                                                   │
      │                                                   │
      ▼                                                   ▼
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│Credentials  │         │ JobPosting   │────────▶│ Application │
└─────────────┘         └──────────────┘         └─────────────┘
                               │                         │
                               │                         ▼
                               │                  ┌─────────────┐
                               │                  │CoverLetter  │
                               │                  └─────────────┘
                               ▼                         │
                        ┌──────────────┐                │
                        │PromptTemplate│◀───────────────┘
                        └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │EmailThread   │
                        └──────────────┘
```

---

## Core Tables

### 1. users

Single user authentication and profile.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(50),
    location VARCHAR(255),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    
    -- Security
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMPTZ,
    failed_login_attempts INT DEFAULT 0,
    locked_until TIMESTAMPTZ,
    
    -- WebAuthn (optional 2FA)
    webauthn_credentials JSONB,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Soft delete
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_active ON users(is_active) WHERE deleted_at IS NULL;
```

---

### 2. master_resumes

Canonical parsed resume data. One per user (single-user system).

```sql
CREATE TYPE experience_type AS ENUM ('full_time', 'contract', 'freelance', 'internship');

CREATE TABLE master_resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Original file
    original_filename VARCHAR(500),
    file_path VARCHAR(1000),  -- Stored file location
    file_size_bytes INT,
    mime_type VARCHAR(100),
    
    -- Parsed text
    raw_text TEXT,
    
    -- Personal info (structured)
    full_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    location VARCHAR(255),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    summary TEXT,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    
    CONSTRAINT one_master_resume_per_user UNIQUE (user_id, deleted_at)
);

CREATE INDEX idx_master_resumes_user ON master_resumes(user_id) WHERE deleted_at IS NULL;
```

---

### 3. work_experiences

Work history from master resume.

```sql
CREATE TABLE work_experiences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    master_resume_id UUID NOT NULL REFERENCES master_resumes(id) ON DELETE CASCADE,
    
    -- Job details
    company_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    employment_type experience_type,
    location VARCHAR(255),
    
    -- Dates
    start_date DATE NOT NULL,
    end_date DATE,  -- NULL = current
    is_current BOOLEAN DEFAULT FALSE,
    
    -- Content
    description TEXT,
    achievements TEXT[],  -- Array of bullet points
    technologies TEXT[],  -- Tech stack used
    
    -- Ordering
    display_order INT DEFAULT 0,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_work_exp_resume ON work_experiences(master_resume_id);
CREATE INDEX idx_work_exp_order ON work_experiences(master_resume_id, display_order);
```

---

### 4. education

Education history from master resume.

```sql
CREATE TYPE degree_type AS ENUM (
    'high_school', 'associate', 'bachelor', 'master', 
    'doctorate', 'professional', 'certificate', 'bootcamp'
);

CREATE TABLE education (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    master_resume_id UUID NOT NULL REFERENCES master_resumes(id) ON DELETE CASCADE,
    
    institution VARCHAR(255) NOT NULL,
    degree_type degree_type,
    field_of_study VARCHAR(255),
    location VARCHAR(255),
    
    start_date DATE,
    end_date DATE,
    gpa DECIMAL(3, 2),  -- e.g., 3.85
    
    honors TEXT[],
    activities TEXT[],
    
    display_order INT DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_education_resume ON education(master_resume_id);
```

---

### 5. skills

Skills from master resume (can be categorized).

```sql
CREATE TYPE skill_category AS ENUM (
    'programming_language', 'framework', 'tool', 
    'soft_skill', 'certification', 'other'
);

CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    master_resume_id UUID NOT NULL REFERENCES master_resumes(id) ON DELETE CASCADE,
    
    skill_name VARCHAR(255) NOT NULL,
    category skill_category,
    proficiency_level VARCHAR(50),  -- e.g., "Expert", "Intermediate"
    years_of_experience INT,
    
    display_order INT DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_skills_resume ON skills(master_resume_id);
CREATE INDEX idx_skills_category ON skills(category);
```

---

### 6. certifications

Professional certifications.

```sql
CREATE TABLE certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    master_resume_id UUID NOT NULL REFERENCES master_resumes(id) ON DELETE CASCADE,
    
    certification_name VARCHAR(255) NOT NULL,
    issuing_organization VARCHAR(255),
    issue_date DATE,
    expiration_date DATE,
    credential_id VARCHAR(255),
    credential_url VARCHAR(500),
    
    display_order INT DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_certifications_resume ON certifications(master_resume_id);
```

---

### 7. resume_versions

Tailored resume variants for specific jobs.

```sql
CREATE TABLE resume_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    master_resume_id UUID NOT NULL REFERENCES master_resumes(id) ON DELETE CASCADE,
    job_posting_id UUID REFERENCES job_postings(id) ON DELETE SET NULL,
    
    version_name VARCHAR(255) NOT NULL,  -- e.g., "Senior Backend Engineer - TechCorp"
    target_role VARCHAR(255),
    target_company VARCHAR(255),
    
    -- Diff from master (stored as JSON for flexibility)
    modifications JSONB,  -- { "work_experiences": [...], "skills": [...] }
    
    -- AI generation metadata
    prompt_template_id UUID REFERENCES prompt_templates(id),
    ai_model_used VARCHAR(100),  -- e.g., "gpt-4-turbo-preview"
    generation_timestamp TIMESTAMPTZ,
    
    -- Files
    pdf_file_path VARCHAR(1000),
    docx_file_path VARCHAR(1000),
    
    -- Stats (for A/B testing)
    times_used INT DEFAULT 0,
    applications_count INT DEFAULT 0,
    response_rate DECIMAL(5, 2),  -- Percentage
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_resume_versions_master ON resume_versions(master_resume_id);
CREATE INDEX idx_resume_versions_job ON resume_versions(job_posting_id);
CREATE INDEX idx_resume_versions_stats ON resume_versions(applications_count, response_rate);
```

---

### 8. job_postings

Saved job opportunities.

```sql
CREATE TYPE job_status AS ENUM (
    'saved',        -- Initially saved
    'prepared',     -- Application package ready
    'applied',      -- Application submitted
    'interviewing', -- Interview scheduled/in progress
    'rejected',     -- Rejected or declined
    'offer',        -- Offer received
    'closed'        -- Job closed/filled
);

CREATE TYPE job_source AS ENUM (
    'manual',       -- Manually entered URL
    'extension',    -- Saved via browser extension
    'api'           -- From job board API
);

CREATE TABLE job_postings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Basic info
    company_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    job_url TEXT NOT NULL,
    source job_source DEFAULT 'manual',
    
    -- Job details
    location VARCHAR(255),
    salary_range VARCHAR(100),  -- e.g., "$120k-$180k"
    employment_type VARCHAR(50),
    remote_policy VARCHAR(50),  -- e.g., "Remote", "Hybrid", "On-site"
    
    -- Description (full text search)
    job_description TEXT,
    requirements TEXT,
    nice_to_have TEXT,
    
    -- ATS detection
    ats_platform VARCHAR(100),  -- e.g., "Workday", "Greenhouse"
    ats_detected_at TIMESTAMPTZ,
    
    -- Status tracking
    status job_status DEFAULT 'saved',
    status_updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Keywords extracted (for matching)
    extracted_keywords TEXT[],
    
    -- Priority/interest
    interest_level INT CHECK (interest_level BETWEEN 1 AND 5),
    notes TEXT,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_jobs_user ON job_postings(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_jobs_status ON job_postings(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_jobs_company ON job_postings(company_name) WHERE deleted_at IS NULL;

-- Full-text search on job description
CREATE INDEX idx_jobs_description_fts ON job_postings 
    USING gin(to_tsvector('english', job_description)) 
    WHERE deleted_at IS NULL;
```

---

### 9. applications

Application submission records.

```sql
CREATE TYPE application_status AS ENUM (
    'draft',            -- Not yet submitted
    'submitted',        -- Application sent
    'viewed',           -- Employer viewed application
    'phone_screen',     -- Phone screen scheduled
    'technical',        -- Technical interview
    'onsite',           -- Onsite/final interview
    'offer',            -- Offer received
    'accepted',         -- Offer accepted
    'rejected',         -- Application rejected
    'withdrawn'         -- Candidate withdrew
);

CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_posting_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    resume_version_id UUID NOT NULL REFERENCES resume_versions(id) ON DELETE RESTRICT,
    
    -- Submission details
    submitted_at TIMESTAMPTZ,
    submission_method VARCHAR(50),  -- e.g., "extension", "manual", "email"
    
    -- Status tracking
    status application_status DEFAULT 'draft',
    status_updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Demographics (if collected)
    demographics_data JSONB,  -- Stored encrypted or as IDs
    
    -- Follow-up
    last_follow_up_date DATE,
    next_follow_up_date DATE,
    follow_up_notes TEXT,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_applications_user ON applications(user_id);
CREATE INDEX idx_applications_job ON applications(job_posting_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_submitted ON applications(submitted_at);
```

---

### 10. cover_letters

Generated cover letters per application.

```sql
CREATE TABLE cover_letters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    
    content TEXT NOT NULL,
    
    -- AI generation metadata
    prompt_template_id UUID REFERENCES prompt_templates(id),
    ai_model_used VARCHAR(100),
    generation_timestamp TIMESTAMPTZ,
    
    -- Versions (allow regeneration)
    version_number INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Files
    pdf_file_path VARCHAR(1000),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_cover_letters_application ON cover_letters(application_id);
CREATE INDEX idx_cover_letters_active ON cover_letters(application_id, is_active);
```

---

### 11. prompt_templates

Versioned AI prompts for different tasks.

```sql
CREATE TYPE prompt_task AS ENUM (
    'resume_tailor',
    'cover_letter',
    'form_answers',
    'email_classification'
);

CREATE TABLE prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    task_type prompt_task NOT NULL,
    role_type VARCHAR(100),  -- e.g., "backend_engineer", "data_scientist"
    
    name VARCHAR(255) NOT NULL,
    prompt_text TEXT NOT NULL,
    
    -- System vs user prompt
    is_system_prompt BOOLEAN DEFAULT FALSE,
    
    -- Versioning
    version INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    parent_template_id UUID REFERENCES prompt_templates(id),  -- For versioning
    
    -- Usage stats
    times_used INT DEFAULT 0,
    avg_satisfaction_score DECIMAL(3, 2),  -- 0-5 rating
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_prompts_user ON prompt_templates(user_id);
CREATE INDEX idx_prompts_task_role ON prompt_templates(task_type, role_type) WHERE is_active;
CREATE INDEX idx_prompts_active ON prompt_templates(is_active);
```

---

### 12. credentials

Encrypted job board credentials for browser extension.

```sql
CREATE TABLE credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    platform VARCHAR(100) NOT NULL,  -- e.g., "linkedin", "indeed"
    username VARCHAR(255),
    
    -- Encrypted password (using pgcrypto or application-level encryption)
    password_encrypted BYTEA NOT NULL,
    
    -- Additional fields (JSON for flexibility)
    additional_data JSONB,
    
    last_used TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_platform_per_user UNIQUE (user_id, platform)
);

CREATE INDEX idx_credentials_user ON credentials(user_id);
CREATE INDEX idx_credentials_platform ON credentials(platform);
```

---

### 13. email_threads

Email tracking for application follow-ups.

```sql
CREATE TYPE email_classification AS ENUM (
    'confirmation',  -- Application received
    'interview',     -- Interview invitation
    'rejection',     -- Rejection notification
    'offer',         -- Offer letter
    'other'          -- Other correspondence
);

CREATE TABLE email_threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    application_id UUID REFERENCES applications(id) ON DELETE SET NULL,
    
    -- Gmail metadata
    gmail_message_id VARCHAR(255) UNIQUE,
    gmail_thread_id VARCHAR(255),
    
    -- Email details
    subject VARCHAR(500),
    sender_email VARCHAR(255),
    sender_name VARCHAR(255),
    received_at TIMESTAMPTZ NOT NULL,
    
    -- Classification
    classification email_classification,
    classification_confidence DECIMAL(3, 2),  -- 0-1 score
    classified_at TIMESTAMPTZ,
    
    -- Body (stored for searching)
    body_text TEXT,
    body_html TEXT,
    
    -- Attachments
    has_attachments BOOLEAN DEFAULT FALSE,
    attachment_names TEXT[],
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_emails_user ON email_threads(user_id);
CREATE INDEX idx_emails_application ON email_threads(application_id);
CREATE INDEX idx_emails_classification ON email_threads(classification);
CREATE INDEX idx_emails_received ON email_threads(received_at);
CREATE INDEX idx_emails_gmail ON email_threads(gmail_thread_id);
```

---

### 14. interview_events

Interview scheduling and tracking.

```sql
CREATE TYPE interview_type AS ENUM (
    'phone_screen',
    'technical_screen',
    'coding_challenge',
    'onsite',
    'behavioral',
    'final_round',
    'other'
);

CREATE TABLE interview_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    
    interview_type interview_type NOT NULL,
    scheduled_at TIMESTAMPTZ NOT NULL,
    duration_minutes INT DEFAULT 60,
    
    -- Location/meeting
    location VARCHAR(500),
    meeting_link VARCHAR(500),
    
    -- Interviewers
    interviewer_names TEXT[],
    interviewer_emails TEXT[],
    
    -- Google Calendar integration
    google_calendar_event_id VARCHAR(255),
    synced_to_calendar BOOLEAN DEFAULT FALSE,
    
    -- Notes & feedback
    preparation_notes TEXT,
    post_interview_notes TEXT,
    feedback_rating INT CHECK (feedback_rating BETWEEN 1 AND 5),
    
    -- Status
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_interviews_application ON interview_events(application_id);
CREATE INDEX idx_interviews_scheduled ON interview_events(scheduled_at);
CREATE INDEX idx_interviews_upcoming ON interview_events(scheduled_at) 
    WHERE NOT completed;
```

---

### 15. analytics_snapshots

Daily aggregated metrics for performance tracking.

```sql
CREATE TABLE analytics_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    snapshot_date DATE NOT NULL,
    
    -- Application metrics
    total_applications INT DEFAULT 0,
    applications_this_week INT DEFAULT 0,
    applications_this_month INT DEFAULT 0,
    
    -- Response metrics
    total_responses INT DEFAULT 0,
    response_rate DECIMAL(5, 2),  -- Percentage
    
    -- Interview metrics
    total_interviews INT DEFAULT 0,
    interview_rate DECIMAL(5, 2),
    
    -- Offer metrics
    total_offers INT DEFAULT 0,
    offer_rate DECIMAL(5, 2),
    
    -- Time metrics
    avg_response_time_days DECIMAL(5, 1),
    avg_time_to_interview_days DECIMAL(5, 1),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_snapshot_per_day UNIQUE (user_id, snapshot_date)
);

CREATE INDEX idx_analytics_user_date ON analytics_snapshots(user_id, snapshot_date);
```

---

## Security Extensions

### Enable pgcrypto for encryption

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

### Example: Encrypted credential storage

```sql
-- Insert encrypted credential
INSERT INTO credentials (user_id, platform, username, password_encrypted)
VALUES (
    'user-uuid-here',
    'linkedin',
    'user@example.com',
    pgp_sym_encrypt('password123', current_setting('app.encryption_key'))
);

-- Decrypt credential
SELECT 
    platform,
    username,
    pgp_sym_decrypt(password_encrypted, current_setting('app.encryption_key')) AS password
FROM credentials
WHERE user_id = 'user-uuid-here';
```

---

## Triggers & Functions

### 1. Update `updated_at` timestamp automatically

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Repeat for other tables...
```

### 2. Update job_postings status when application submitted

```sql
CREATE OR REPLACE FUNCTION update_job_status_on_application()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.submitted_at IS NOT NULL AND NEW.status = 'submitted' THEN
        UPDATE job_postings
        SET status = 'applied', status_updated_at = NOW()
        WHERE id = NEW.job_posting_id AND status = 'prepared';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_job_status
    AFTER INSERT OR UPDATE ON applications
    FOR EACH ROW EXECUTE FUNCTION update_job_status_on_application();
```

### 3. Increment resume version usage stats

```sql
CREATE OR REPLACE FUNCTION increment_resume_version_usage()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE resume_versions
    SET times_used = times_used + 1
    WHERE id = NEW.resume_version_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_increment_resume_usage
    AFTER INSERT ON applications
    FOR EACH ROW EXECUTE FUNCTION increment_resume_version_usage();
```

---

## Indexes for Performance

Key indexes for common queries:

```sql
-- Resume lookup
CREATE INDEX idx_master_resumes_user_active 
    ON master_resumes(user_id) WHERE deleted_at IS NULL;

-- Job search and filtering
CREATE INDEX idx_jobs_status_created 
    ON job_postings(status, created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_jobs_company_title 
    ON job_postings(company_name, job_title) WHERE deleted_at IS NULL;

-- Application timeline
CREATE INDEX idx_applications_user_submitted 
    ON applications(user_id, submitted_at DESC);

-- Email matching
CREATE INDEX idx_emails_sender_received 
    ON email_threads(sender_email, received_at DESC);

-- Interview calendar
CREATE INDEX idx_interviews_upcoming 
    ON interview_events(scheduled_at) WHERE completed = FALSE;
```

---

## Sample Queries

### Get all applications with status for a user

```sql
SELECT 
    j.company_name,
    j.job_title,
    a.status,
    a.submitted_at,
    rv.version_name AS resume_used,
    COUNT(ie.id) AS interview_count
FROM applications a
JOIN job_postings j ON a.job_posting_id = j.id
JOIN resume_versions rv ON a.resume_version_id = rv.id
LEFT JOIN interview_events ie ON a.id = ie.application_id
WHERE a.user_id = 'user-uuid'
GROUP BY j.company_name, j.job_title, a.status, a.submitted_at, rv.version_name
ORDER BY a.submitted_at DESC;
```

### Calculate response rate by resume version

```sql
SELECT 
    rv.version_name,
    rv.target_role,
    COUNT(a.id) AS total_applications,
    COUNT(et.id) FILTER (WHERE et.classification IN ('interview', 'offer')) AS responses,
    ROUND(
        COUNT(et.id) FILTER (WHERE et.classification IN ('interview', 'offer'))::DECIMAL 
        / NULLIF(COUNT(a.id), 0) * 100, 
        2
    ) AS response_rate
FROM resume_versions rv
JOIN applications a ON rv.id = a.resume_version_id
LEFT JOIN email_threads et ON a.id = et.application_id
GROUP BY rv.id, rv.version_name, rv.target_role
ORDER BY response_rate DESC;
```

### Find jobs matching skills

```sql
SELECT 
    jp.company_name,
    jp.job_title,
    COUNT(s.id) AS matching_skills
FROM job_postings jp
CROSS JOIN skills s
WHERE s.master_resume_id = 'resume-uuid'
    AND jp.job_description ILIKE '%' || s.skill_name || '%'
    AND jp.status = 'saved'
GROUP BY jp.id, jp.company_name, jp.job_title
HAVING COUNT(s.id) >= 5
ORDER BY matching_skills DESC;
```

---

## Migration Strategy

### Using Alembic (SQLAlchemy migrations)

```bash
# Initialize Alembic
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Seed Data

```sql
-- Default prompt templates
INSERT INTO prompt_templates (user_id, task_type, role_type, name, prompt_text, is_active)
VALUES 
(
    'user-uuid',
    'resume_tailor',
    'backend_engineer',
    'Backend Engineer Resume Optimization',
    'You are an expert resume writer... [full prompt]',
    TRUE
);
```

---

## Backup & Recovery

### Automated Daily Backups

```bash
# Backup script (run via cron)
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump ai_job_assistant > backups/backup_$TIMESTAMP.sql
gzip backups/backup_$TIMESTAMP.sql

# Keep only last 30 days
find backups/ -name "*.sql.gz" -mtime +30 -delete
```

### Point-in-Time Recovery (PITR)

Enable WAL archiving in `postgresql.conf`:

```conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /path/to/archive/%f'
```

---

## Next Steps

1. ✅ Review schema design
2. ⏳ Generate SQLAlchemy models
3. ⏳ Create Alembic migration scripts
4. ⏳ Set up database initialization scripts
5. ⏳ Implement encryption helpers
6. ⏳ Create seed data scripts

