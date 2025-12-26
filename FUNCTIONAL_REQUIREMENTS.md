# Functional Requirements Specification
**Project:** Personal AI Job Search Assistant  
**Audience:** Software Engineers, AI Coding Assistants  
**Scope:** Single-user system, phased automation

---

## 1. System Overview

### FR-1.1 — System Purpose
The system SHALL assist a single user in managing, optimizing, and submitting job applications using AI-assisted content generation and browser-based automation.

### FR-1.2 — Supported Platforms
- Desktop web application (primary)
- Browser extension (Chrome / Edge)
- Android support via browser (no native app in initial scope)

---

## 2. User Authentication & Access Control

### FR-2.1 — User Account
- The system SHALL support exactly one user.
- The system SHALL require authentication before access to any data.

### FR-2.2 — Authentication Method
- The system SHALL support password-based authentication.
- The system SHOULD support optional strong authentication (e.g., WebAuthn).

### FR-2.3 — Session Management
- The system SHALL maintain authenticated sessions.
- The system SHALL invalidate sessions on logout or credential change.

---

## 3. Resume Management

### FR-3.1 — Master Resume Ingestion
- The system SHALL allow the user to upload a master resume in PDF or DOCX format.
- The system SHALL parse the resume into structured fields:
  - Personal information
  - Work experience
  - Education
  - Skills
  - Certifications

### FR-3.2 — Resume Normalization
- The system SHALL normalize parsed resume data into a canonical internal schema.
- The system SHALL preserve original wording and structure.

### FR-3.3 — Resume Versioning
- The system SHALL allow creation of derived resume versions from the master resume.
- Each resume version SHALL be associated with:
  - Target job
  - Target role title
  - Prompt configuration used

### FR-3.4 — Resume Editing
- The system SHALL allow the user to manually edit any resume version.
- The system SHALL track changes between versions (diff view).

---

## 4. Job Management

### FR-4.1 — Job Saving
- The system SHALL allow saving a job posting via:
  - URL input
  - Browser extension “Save Job” action

### FR-4.2 — Job Parsing
- The system SHALL extract:
  - Company name
  - Job title
  - Job description
  - Location
  - Application platform (if detectable)

### FR-4.3 — Job Lifecycle
Each job SHALL have a lifecycle state:
- Saved
- Prepared
- Applied
- Interviewing
- Rejected
- Offer
- Closed

---

## 5. AI-Assisted Resume Tailoring

### FR-5.1 — Resume Tailoring Trigger
- The system SHALL generate a tailored resume upon explicit user request.

### FR-5.2 — Tailoring Inputs
The AI tailoring process SHALL use:
- Master resume data
- Job description
- Selected role profile
- Active prompt templates

### FR-5.3 — Tailoring Behavior
- The system SHALL optimize resume content for:
  - Role relevance
  - Executive-level positioning
  - ATS keyword alignment
- The system MAY reorder, rewrite, and quantify experience.

### FR-5.4 — Review & Approval
- The system SHALL present the tailored resume for review before use.
- Post-generation review SHALL be optional but available.

---

## 6. Cover Letter Generation

### FR-6.1 — Cover Letter Creation
- The system SHALL generate a cover letter per job application.
- The cover letter SHALL be customized for:
  - Company
  - Role
  - Job description

### FR-6.2 — Cover Letter Tone
- The system SHALL use an executive-level persuasive tone.

### FR-6.3 — Cover Letter Editing
- The system SHALL allow manual editing of generated cover letters.

---

## 7. Prompt Management

### FR-7.1 — Prompt Templates
- The system SHALL store AI prompt templates as editable entities.
- Prompts SHALL be versioned.

### FR-7.2 — Prompt Scope
- Prompts SHALL be configurable per:
  - Task (resume, cover letter, form answers)
  - Role type

### FR-7.3 — Prompt Override
- The system SHALL allow overriding default prompts per job.

---

## 8. Application Preparation

### FR-8.1 — Application Package
- The system SHALL bundle the following per application:
  - Resume version
  - Cover letter
  - Demographic answers

### FR-8.2 — Demographic Answers
- The system SHALL store fixed predefined demographic responses.
- The system SHALL reuse these consistently across all applications.

---

## 9. Browser Extension (Autofill & Submission)

### FR-9.1 — Extension Authentication
- The browser extension SHALL authenticate with the backend API.

### FR-9.2 — ATS Detection
- The extension SHALL detect common ATS platforms (e.g., Workday, Greenhouse).

### FR-9.3 — Field Mapping
- The extension SHALL map resume fields to ATS form fields.

### FR-9.4 — Autofill
- The extension SHALL autofill:
  - Personal information
  - Work history
  - Education
  - Demographic answers

### FR-9.5 — Submission Control
- The extension SHALL support:
  - Autofill only
  - Autofill + submit (when enabled)

### FR-9.6 — Failure Handling
- The extension SHALL report autofill or submission failures to the backend.

---

## 10. Credential Management

### FR-10.1 — Credential Storage
- The system SHALL allow storing job board credentials.
- Credentials SHALL be encrypted at rest.

### FR-10.2 — Credential Usage
- Credentials SHALL be accessible only to the browser extension.
- Credentials SHALL NOT be exposed to AI components.

---

## 11. Application Tracking

### FR-11.1 — Application Record
- The system SHALL create an application record for each submission.

### FR-11.2 — Status Updates
- The system SHALL allow manual status updates.
- The system SHALL auto-update status based on detected emails.

---

## 12. Email Integration (Gmail)

### FR-12.1 — Gmail Connection
- The system SHALL integrate with Gmail via OAuth.

### FR-12.2 — Email Matching
- The system SHALL match incoming emails to applications based on:
  - Company
  - Job title
  - Resume version

### FR-12.3 — Email Classification
- The system SHALL classify emails into:
  - Confirmation
  - Interview
  - Rejection
  - Other

---

## 13. Calendar Integration

### FR-13.1 — Interview Scheduling
- The system SHALL detect interview invitations from email.

### FR-13.2 — Calendar Sync
- The system SHALL create Google Calendar events upon user confirmation.

---

## 14. Interview Feedback & Learning

### FR-14.1 — Feedback Entry
- The system SHALL allow manual entry of post-interview feedback.

### FR-14.2 — Learning Input
- The system SHALL use feedback, outcomes, and response rates as AI learning signals.

---

## 15. Analytics & Insights

### FR-15.1 — Metrics
The system SHALL compute:
- Applications per week
- Response rate
- Interview rate
- Resume version performance

### FR-15.2 — AI Optimization
- The system SHALL correlate outcomes with:
  - Resume versions
  - Prompt templates
  - Keywords used

---

## 16. Security & Privacy

### FR-16.1 — Data Encryption
- The system SHALL encrypt sensitive data at rest.

### FR-16.2 — Data Isolation
- Resume data SHALL be isolated from logs and analytics.

### FR-16.3 — Auditability
- The system SHALL log system actions (excluding sensitive content).

---

## 17. Non-Goals (Explicit)

The system SHALL NOT:
- Mass-apply to jobs without user intent
- Store SSN fragments
- Operate as a multi-user SaaS

---

## 18. Extensibility Requirements

### FR-18.1 — ATS Support Expansion
- The system SHALL support adding new ATS platforms without core rewrites.

### FR-18.2 — Model Replacement
- The system SHALL allow swapping AI models without changing business logic.
