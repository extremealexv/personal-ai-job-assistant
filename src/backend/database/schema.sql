-- Personal AI Job Assistant Database Schema
-- PostgreSQL 15+
-- Created: 2025-12-26

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- ============================================================================
-- ENUMS
-- ============================================================================

CREATE TYPE experience_type AS ENUM ('full_time', 'contract', 'freelance', 'internship');

CREATE TYPE degree_type AS ENUM (
    'high_school', 'associate', 'bachelor', 'master', 
    'doctorate', 'professional', 'certificate', 'bootcamp'
);

CREATE TYPE skill_category AS ENUM (
    'programming_language', 'framework', 'tool', 
    'soft_skill', 'certification', 'other'
);

CREATE TYPE job_status AS ENUM (
    'saved', 'prepared', 'applied', 'interviewing', 
    'rejected', 'offer', 'closed'
);

CREATE TYPE job_source AS ENUM ('manual', 'extension', 'api');

CREATE TYPE application_status AS ENUM (
    'draft', 'submitted', 'viewed', 'phone_screen', 'technical',
    'onsite', 'offer', 'accepted', 'rejected', 'withdrawn'
);

CREATE TYPE prompt_task AS ENUM (
    'resume_tailor', 'cover_letter', 'form_answers', 'email_classification'
);

CREATE TYPE email_classification AS ENUM (
    'confirmation', 'interview', 'rejection', 'offer', 'other'
);

CREATE TYPE interview_type AS ENUM (
    'phone_screen', 'technical_screen', 'coding_challenge',
    'onsite', 'behavioral', 'final_round', 'other'
);

-- ============================================================================
-- TABLES
-- ============================================================================

-- Users table (single user system, but designed for potential expansion)
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
    webauthn_credentials JSONB,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- Master resumes (canonical resume data)
CREATE TABLE master_resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Original file
    original_filename VARCHAR(500),
    file_path VARCHAR(1000),
    file_size_bytes INT,
    mime_type VARCHAR(100),
    raw_text TEXT,
    
    -- Personal info
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

-- Work experience
CREATE TABLE work_experiences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    master_resume_id UUID NOT NULL REFERENCES master_resumes(id) ON DELETE CASCADE,
    
    company_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    employment_type experience_type,
    location VARCHAR(255),
    
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    
    description TEXT,
    achievements TEXT[],
    technologies TEXT[],
    
    display_order INT DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_date_range CHECK (end_date IS NULL OR end_date >= start_date)
);

-- Education
CREATE TABLE education (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    master_resume_id UUID NOT NULL REFERENCES master_resumes(id) ON DELETE CASCADE,
    
    institution VARCHAR(255) NOT NULL,
    degree_type degree_type,
    field_of_study VARCHAR(255),
    location VARCHAR(255),
    
    start_date DATE,
    end_date DATE,
    gpa DECIMAL(3, 2),
    
    honors TEXT[],
    activities TEXT[],
    
    display_order INT DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_gpa CHECK (gpa IS NULL OR (gpa >= 0 AND gpa <= 5.0))
);

-- Skills
CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    master_resume_id UUID NOT NULL REFERENCES master_resumes(id) ON DELETE CASCADE,
    
    skill_name VARCHAR(255) NOT NULL,
    category skill_category,
    proficiency_level VARCHAR(50),
    years_of_experience INT,
    
    display_order INT DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_experience_years CHECK (years_of_experience IS NULL OR years_of_experience >= 0)
);

-- Certifications
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
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_cert_dates CHECK (expiration_date IS NULL OR expiration_date >= issue_date)
);

-- Job postings
CREATE TABLE job_postings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    company_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    job_url TEXT NOT NULL,
    source job_source DEFAULT 'manual',
    
    location VARCHAR(255),
    salary_range VARCHAR(100),
    employment_type VARCHAR(50),
    remote_policy VARCHAR(50),
    
    job_description TEXT,
    requirements TEXT,
    nice_to_have TEXT,
    
    ats_platform VARCHAR(100),
    ats_detected_at TIMESTAMPTZ,
    
    status job_status DEFAULT 'saved',
    status_updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    extracted_keywords TEXT[],
    interest_level INT CHECK (interest_level BETWEEN 1 AND 5),
    notes TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Resume versions (tailored resumes)
CREATE TABLE resume_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    master_resume_id UUID NOT NULL REFERENCES master_resumes(id) ON DELETE CASCADE,
    job_posting_id UUID REFERENCES job_postings(id) ON DELETE SET NULL,
    
    version_name VARCHAR(255) NOT NULL,
    target_role VARCHAR(255),
    target_company VARCHAR(255),
    
    modifications JSONB,
    
    prompt_template_id UUID,  -- FK added later after prompt_templates created
    ai_model_used VARCHAR(100),
    generation_timestamp TIMESTAMPTZ,
    
    pdf_file_path VARCHAR(1000),
    docx_file_path VARCHAR(1000),
    
    times_used INT DEFAULT 0,
    applications_count INT DEFAULT 0,
    response_rate DECIMAL(5, 2),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Prompt templates
CREATE TABLE prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    task_type prompt_task NOT NULL,
    role_type VARCHAR(100),
    
    name VARCHAR(255) NOT NULL,
    prompt_text TEXT NOT NULL,
    
    is_system_prompt BOOLEAN DEFAULT FALSE,
    
    version INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    parent_template_id UUID REFERENCES prompt_templates(id),
    
    times_used INT DEFAULT 0,
    avg_satisfaction_score DECIMAL(3, 2),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_satisfaction CHECK (avg_satisfaction_score IS NULL OR 
        (avg_satisfaction_score >= 0 AND avg_satisfaction_score <= 5))
);

-- Add FK to resume_versions now that prompt_templates exists
ALTER TABLE resume_versions 
    ADD CONSTRAINT fk_resume_version_prompt 
    FOREIGN KEY (prompt_template_id) 
    REFERENCES prompt_templates(id) ON DELETE SET NULL;

-- Applications
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_posting_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    resume_version_id UUID NOT NULL REFERENCES resume_versions(id) ON DELETE RESTRICT,
    
    submitted_at TIMESTAMPTZ,
    submission_method VARCHAR(50),
    
    status application_status DEFAULT 'draft',
    status_updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    demographics_data JSONB,
    
    last_follow_up_date DATE,
    next_follow_up_date DATE,
    follow_up_notes TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cover letters
CREATE TABLE cover_letters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    
    content TEXT NOT NULL,
    
    prompt_template_id UUID REFERENCES prompt_templates(id),
    ai_model_used VARCHAR(100),
    generation_timestamp TIMESTAMPTZ,
    
    version_number INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    
    pdf_file_path VARCHAR(1000),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Credentials (encrypted)
CREATE TABLE credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    platform VARCHAR(100) NOT NULL,
    username VARCHAR(255),
    password_encrypted BYTEA NOT NULL,
    
    additional_data JSONB,
    
    last_used TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_platform_per_user UNIQUE (user_id, platform)
);

-- Email threads
CREATE TABLE email_threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    application_id UUID REFERENCES applications(id) ON DELETE SET NULL,
    
    gmail_message_id VARCHAR(255) UNIQUE,
    gmail_thread_id VARCHAR(255),
    
    subject VARCHAR(500),
    sender_email VARCHAR(255),
    sender_name VARCHAR(255),
    received_at TIMESTAMPTZ NOT NULL,
    
    classification email_classification,
    classification_confidence DECIMAL(3, 2),
    classified_at TIMESTAMPTZ,
    
    body_text TEXT,
    body_html TEXT,
    
    has_attachments BOOLEAN DEFAULT FALSE,
    attachment_names TEXT[],
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Interview events
CREATE TABLE interview_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    
    interview_type interview_type NOT NULL,
    scheduled_at TIMESTAMPTZ NOT NULL,
    duration_minutes INT DEFAULT 60,
    
    location VARCHAR(500),
    meeting_link VARCHAR(500),
    
    interviewer_names TEXT[],
    interviewer_emails TEXT[],
    
    google_calendar_event_id VARCHAR(255),
    synced_to_calendar BOOLEAN DEFAULT FALSE,
    
    preparation_notes TEXT,
    post_interview_notes TEXT,
    feedback_rating INT CHECK (feedback_rating BETWEEN 1 AND 5),
    
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analytics snapshots
CREATE TABLE analytics_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    snapshot_date DATE NOT NULL,
    
    total_applications INT DEFAULT 0,
    applications_this_week INT DEFAULT 0,
    applications_this_month INT DEFAULT 0,
    
    total_responses INT DEFAULT 0,
    response_rate DECIMAL(5, 2),
    
    total_interviews INT DEFAULT 0,
    interview_rate DECIMAL(5, 2),
    
    total_offers INT DEFAULT 0,
    offer_rate DECIMAL(5, 2),
    
    avg_response_time_days DECIMAL(5, 1),
    avg_time_to_interview_days DECIMAL(5, 1),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_snapshot_per_day UNIQUE (user_id, snapshot_date)
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Users
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_active ON users(is_active) WHERE deleted_at IS NULL;

-- Master resumes
CREATE INDEX idx_master_resumes_user ON master_resumes(user_id) WHERE deleted_at IS NULL;

-- Work experiences
CREATE INDEX idx_work_exp_resume ON work_experiences(master_resume_id);
CREATE INDEX idx_work_exp_order ON work_experiences(master_resume_id, display_order);

-- Education
CREATE INDEX idx_education_resume ON education(master_resume_id);

-- Skills
CREATE INDEX idx_skills_resume ON skills(master_resume_id);
CREATE INDEX idx_skills_category ON skills(category);

-- Certifications
CREATE INDEX idx_certifications_resume ON certifications(master_resume_id);

-- Job postings
CREATE INDEX idx_jobs_user ON job_postings(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_jobs_status ON job_postings(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_jobs_company ON job_postings(company_name) WHERE deleted_at IS NULL;
CREATE INDEX idx_jobs_status_created ON job_postings(status, created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_jobs_description_fts ON job_postings 
    USING gin(to_tsvector('english', job_description)) WHERE deleted_at IS NULL;

-- Resume versions
CREATE INDEX idx_resume_versions_master ON resume_versions(master_resume_id);
CREATE INDEX idx_resume_versions_job ON resume_versions(job_posting_id);
CREATE INDEX idx_resume_versions_stats ON resume_versions(applications_count, response_rate);

-- Prompt templates
CREATE INDEX idx_prompts_user ON prompt_templates(user_id);
CREATE INDEX idx_prompts_task_role ON prompt_templates(task_type, role_type) WHERE is_active;
CREATE INDEX idx_prompts_active ON prompt_templates(is_active);

-- Applications
CREATE INDEX idx_applications_user ON applications(user_id);
CREATE INDEX idx_applications_job ON applications(job_posting_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_submitted ON applications(submitted_at);
CREATE INDEX idx_applications_user_submitted ON applications(user_id, submitted_at DESC);

-- Cover letters
CREATE INDEX idx_cover_letters_application ON cover_letters(application_id);
CREATE INDEX idx_cover_letters_active ON cover_letters(application_id, is_active);

-- Credentials
CREATE INDEX idx_credentials_user ON credentials(user_id);
CREATE INDEX idx_credentials_platform ON credentials(platform);

-- Email threads
CREATE INDEX idx_emails_user ON email_threads(user_id);
CREATE INDEX idx_emails_application ON email_threads(application_id);
CREATE INDEX idx_emails_classification ON email_threads(classification);
CREATE INDEX idx_emails_received ON email_threads(received_at);
CREATE INDEX idx_emails_gmail ON email_threads(gmail_thread_id);
CREATE INDEX idx_emails_sender_received ON email_threads(sender_email, received_at DESC);

-- Interview events
CREATE INDEX idx_interviews_application ON interview_events(application_id);
CREATE INDEX idx_interviews_scheduled ON interview_events(scheduled_at);
CREATE INDEX idx_interviews_upcoming ON interview_events(scheduled_at) WHERE NOT completed;

-- Analytics snapshots
CREATE INDEX idx_analytics_user_date ON analytics_snapshots(user_id, snapshot_date);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at column
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_master_resumes_updated_at
    BEFORE UPDATE ON master_resumes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_work_experiences_updated_at
    BEFORE UPDATE ON work_experiences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_education_updated_at
    BEFORE UPDATE ON education
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_job_postings_updated_at
    BEFORE UPDATE ON job_postings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resume_versions_updated_at
    BEFORE UPDATE ON resume_versions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prompt_templates_updated_at
    BEFORE UPDATE ON prompt_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_applications_updated_at
    BEFORE UPDATE ON applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cover_letters_updated_at
    BEFORE UPDATE ON cover_letters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_credentials_updated_at
    BEFORE UPDATE ON credentials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_interview_events_updated_at
    BEFORE UPDATE ON interview_events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Update job posting status when application submitted
CREATE OR REPLACE FUNCTION update_job_status_on_application()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.submitted_at IS NOT NULL AND NEW.status = 'submitted' THEN
        UPDATE job_postings
        SET status = 'applied', status_updated_at = NOW()
        WHERE id = NEW.job_posting_id AND status IN ('saved', 'prepared');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_job_status
    AFTER INSERT OR UPDATE ON applications
    FOR EACH ROW EXECUTE FUNCTION update_job_status_on_application();

-- Increment resume version usage stats
CREATE OR REPLACE FUNCTION increment_resume_version_usage()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE resume_versions
    SET 
        times_used = times_used + 1,
        applications_count = applications_count + 1
    WHERE id = NEW.resume_version_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_increment_resume_usage
    AFTER INSERT ON applications
    FOR EACH ROW EXECUTE FUNCTION increment_resume_version_usage();

-- Increment prompt template usage
CREATE OR REPLACE FUNCTION increment_prompt_usage()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.prompt_template_id IS NOT NULL THEN
        UPDATE prompt_templates
        SET times_used = times_used + 1
        WHERE id = NEW.prompt_template_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_increment_prompt_usage_resume
    AFTER INSERT ON resume_versions
    FOR EACH ROW EXECUTE FUNCTION increment_prompt_usage();

CREATE TRIGGER trigger_increment_prompt_usage_cover_letter
    AFTER INSERT ON cover_letters
    FOR EACH ROW EXECUTE FUNCTION increment_prompt_usage();

-- ============================================================================
-- COMMENTS (Documentation)
-- ============================================================================

COMMENT ON TABLE users IS 'Single user authentication and profile';
COMMENT ON TABLE master_resumes IS 'Canonical parsed resume data (one per user)';
COMMENT ON TABLE work_experiences IS 'Work history from master resume';
COMMENT ON TABLE education IS 'Education history from master resume';
COMMENT ON TABLE skills IS 'Skills extracted from master resume';
COMMENT ON TABLE certifications IS 'Professional certifications';
COMMENT ON TABLE job_postings IS 'Saved job opportunities';
COMMENT ON TABLE resume_versions IS 'Tailored resume variants for specific jobs';
COMMENT ON TABLE prompt_templates IS 'Versioned AI prompts for different tasks';
COMMENT ON TABLE applications IS 'Application submission records';
COMMENT ON TABLE cover_letters IS 'Generated cover letters per application';
COMMENT ON TABLE credentials IS 'Encrypted job board credentials';
COMMENT ON TABLE email_threads IS 'Email tracking for application follow-ups';
COMMENT ON TABLE interview_events IS 'Interview scheduling and tracking';
COMMENT ON TABLE analytics_snapshots IS 'Daily aggregated metrics';

COMMENT ON COLUMN credentials.password_encrypted IS 'Encrypted using pgcrypto or application-level encryption';
COMMENT ON COLUMN resume_versions.modifications IS 'JSONB diff from master resume';
COMMENT ON COLUMN job_postings.extracted_keywords IS 'Keywords extracted for matching';
