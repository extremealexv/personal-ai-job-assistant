# Prompt Templates API

**Base URL**: `/api/v1/prompt-templates`

Manage AI prompt templates for resume tailoring, cover letter generation, and form answers. Templates are versioned, customizable, and track usage statistics.

---

## Table of Contents

- [Overview](#overview)
- [Endpoints](#endpoints)
  - [Create Prompt Template](#create-prompt-template)
  - [List Prompt Templates](#list-prompt-templates)
  - [Get Prompt Template](#get-prompt-template)
  - [Update Prompt Template](#update-prompt-template)
  - [Delete Prompt Template](#delete-prompt-template)
  - [Duplicate Prompt Template](#duplicate-prompt-template)
  - [Get Usage Statistics](#get-usage-statistics)
- [Data Models](#data-models)
- [Example Prompts](#example-prompts)
- [Best Practices](#best-practices)

---

## Overview

Prompt templates are the foundation of AI-powered resume tailoring and cover letter generation. They:

- Define how AI processes and optimizes content
- Support different task types (resume, cover letter, form answers)
- Can be customized per role type (backend engineer, data scientist, etc.)
- Track usage and satisfaction scores
- Support versioning and cloning

**Key Concepts:**

- **Task Type**: What the prompt does (resume_tailor, cover_letter, form_answers)
- **Role Type**: Target job role (optional, for role-specific prompts)
- **System Prompt**: Base-level prompts vs user-editable prompts
- **Parent Template**: Track prompt lineage when cloning/versioning

---

## Endpoints

### Create Prompt Template

Create a new prompt template.

**Endpoint**: `POST /api/v1/prompt-templates`

**Authentication**: Required

**Request Body**:

```json
{
  "task_type": "resume_tailor",
  "role_type": "backend_engineer",
  "name": "Backend Engineer Resume Optimizer",
  "prompt_text": "You are an expert resume writer specializing in backend engineering roles...",
  "is_system_prompt": false
}
```

**Response** (201 Created):

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "task_type": "resume_tailor",
  "role_type": "backend_engineer",
  "name": "Backend Engineer Resume Optimizer",
  "prompt_text": "You are an expert resume writer specializing in backend engineering roles...",
  "is_system_prompt": false,
  "version": 1,
  "is_active": true,
  "parent_template_id": null,
  "times_used": 0,
  "avg_satisfaction_score": null,
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z"
}
```

**Task Types**:
- `resume_tailor` - Resume optimization
- `cover_letter` - Cover letter generation
- `form_answers` - Job application form responses
- `email_classification` - Email categorization

---

### List Prompt Templates

List all prompt templates with optional filtering and pagination.

**Endpoint**: `GET /api/v1/prompt-templates`

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `task_type` | string | Filter by task type | `resume_tailor` |
| `role_type` | string | Filter by role type | `backend_engineer` |
| `is_active` | boolean | Filter by active status | `true` |
| `skip` | integer | Number of records to skip | `0` |
| `limit` | integer | Max records to return (max 100) | `20` |

**Request**:

```http
GET /api/v1/prompt-templates?task_type=resume_tailor&is_active=true&limit=10
```

**Response** (200 OK):

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "task_type": "resume_tailor",
    "role_type": "backend_engineer",
    "name": "Backend Engineer Resume Optimizer",
    "prompt_text": "...",
    "is_active": true,
    "times_used": 15,
    "avg_satisfaction_score": 4.5,
    "created_at": "2026-01-01T12:00:00Z",
    "updated_at": "2026-01-05T14:30:00Z"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "task_type": "resume_tailor",
    "role_type": "fullstack_engineer",
    "name": "Full Stack Engineer Resume Template",
    "prompt_text": "...",
    "is_active": true,
    "times_used": 8,
    "avg_satisfaction_score": 4.2,
    "created_at": "2026-01-02T09:15:00Z",
    "updated_at": "2026-01-02T09:15:00Z"
  }
]
```

---

### Get Prompt Template

Retrieve a specific prompt template by ID.

**Endpoint**: `GET /api/v1/prompt-templates/{id}`

**Authentication**: Required

**Response** (200 OK):

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "task_type": "resume_tailor",
  "role_type": "backend_engineer",
  "name": "Backend Engineer Resume Optimizer",
  "prompt_text": "You are an expert resume writer...",
  "is_system_prompt": false,
  "version": 1,
  "is_active": true,
  "parent_template_id": null,
  "times_used": 15,
  "avg_satisfaction_score": 4.5,
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-05T14:30:00Z"
}
```

**Error Responses**:

- `404 Not Found` - Template doesn't exist
- `403 Forbidden` - Template belongs to another user

---

### Update Prompt Template

Update an existing prompt template.

**Endpoint**: `PUT /api/v1/prompt-templates/{id}`

**Authentication**: Required

**Request Body** (all fields optional):

```json
{
  "name": "Senior Backend Engineer Resume Optimizer",
  "prompt_text": "Updated prompt text...",
  "is_active": false,
  "role_type": "senior_backend_engineer"
}
```

**Response** (200 OK):

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Senior Backend Engineer Resume Optimizer",
  "prompt_text": "Updated prompt text...",
  "is_active": false,
  "role_type": "senior_backend_engineer",
  "updated_at": "2026-01-06T10:00:00Z"
}
```

---

### Delete Prompt Template

Delete a prompt template.

**Endpoint**: `DELETE /api/v1/prompt-templates/{id}`

**Authentication**: Required

**Response**: `204 No Content`

**Notes**:
- Deletes permanently (not soft delete)
- Cannot be undone
- Referenced by resume versions or cover letters will have `prompt_template_id` set to NULL

---

### Duplicate Prompt Template

Clone an existing template with modifications.

**Endpoint**: `POST /api/v1/prompt-templates/{id}/duplicate`

**Authentication**: Required

**Request Body**:

```json
{
  "name": "Cloned Backend Engineer Template",
  "prompt_text": "Modified prompt text for experimentation...",
  "role_type": "senior_backend_engineer"
}
```

**Response** (201 Created):

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "task_type": "resume_tailor",
  "role_type": "senior_backend_engineer",
  "name": "Cloned Backend Engineer Template",
  "prompt_text": "Modified prompt text for experimentation...",
  "is_system_prompt": false,
  "version": 1,
  "is_active": true,
  "parent_template_id": "550e8400-e29b-41d4-a716-446655440000",
  "times_used": 0,
  "avg_satisfaction_score": null,
  "created_at": "2026-01-06T11:00:00Z",
  "updated_at": "2026-01-06T11:00:00Z"
}
```

**Use Cases**:
- A/B testing different prompt variations
- Creating role-specific versions
- Experimenting with prompt improvements

---

### Get Usage Statistics

Get usage statistics for a prompt template.

**Endpoint**: `GET /api/v1/prompt-templates/{id}/stats`

**Authentication**: Required

**Response** (200 OK):

```json
{
  "prompt_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Backend Engineer Resume Optimizer",
  "times_used": 15,
  "avg_satisfaction_score": 4.5,
  "is_active": true,
  "created_at": "2026-01-01T12:00:00Z",
  "last_used_at": "2026-01-05T14:30:00Z"
}
```

---

## Data Models

### PromptTemplate

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier |
| `user_id` | UUID | Owner user ID |
| `task_type` | enum | Task type (resume_tailor, cover_letter, form_answers, email_classification) |
| `role_type` | string | Optional role type (e.g., "backend_engineer") |
| `name` | string | Template name (max 255 chars) |
| `prompt_text` | text | Full prompt content |
| `is_system_prompt` | boolean | Whether it's a system-level prompt |
| `version` | integer | Version number (starts at 1) |
| `is_active` | boolean | Whether template is currently active |
| `parent_template_id` | UUID | ID of parent template if cloned |
| `times_used` | integer | Number of times used |
| `avg_satisfaction_score` | decimal | Average satisfaction score (0-5) |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

---

## Example Prompts

### Backend Engineer Resume Tailoring

```text
You are an expert resume writer specializing in backend engineering positions at top tech companies. Your goal is to optimize the candidate's resume for a specific job posting while maintaining authenticity.

ROLE CONTEXT:
- Target Role: Backend Engineer / Senior Backend Engineer
- Key Technologies: {extracted from job description}
- Company Type: {startup, mid-size, enterprise}

OPTIMIZATION GUIDELINES:

1. **Impact & Metrics**: Quantify achievements with specific numbers
   - Scale (users, requests, data volume)
   - Performance improvements (latency, throughput, cost savings)
   - Team impact (collaboration, mentorship, cross-functional)

2. **Technical Skills Alignment**:
   - Match job requirements with candidate experience
   - Highlight relevant technologies and frameworks
   - Emphasize system design and architecture experience
   - Showcase distributed systems, scalability, performance work

3. **Executive Positioning**:
   - Use action verbs (Architected, Scaled, Optimized, Led)
   - Focus on business impact and technical leadership
   - Demonstrate problem-solving and decision-making
   - Show progression and increasing responsibility

4. **ATS Optimization**:
   - Include exact keyword matches from job description
   - Use standard section headers (Experience, Education, Skills)
   - Maintain consistent formatting and structure
   - Include technical certifications if relevant

5. **Content Adjustments**:
   - Reorder bullet points by relevance to target role
   - Expand relevant experience, condense less relevant
   - Add context for lesser-known companies or projects
   - Remove outdated technologies unless directly relevant

OUTPUT FORMAT:
Return optimized resume sections in JSON format with explanations for major changes.

IMPORTANT:
- Maintain factual accuracy - never fabricate experience
- Preserve original dates and company names
- Keep tone professional and confident, not boastful
- Ensure all claims are defensible in interviews
```

### Data Scientist Resume Tailoring

```text
You are an expert resume writer specializing in data science and machine learning positions. Your goal is to optimize the candidate's resume for maximum impact in the competitive data science job market.

ROLE CONTEXT:
- Target Role: Data Scientist / ML Engineer / Research Scientist
- Key Skills: {extracted from job description}
- Industry Focus: {tech, finance, healthcare, etc.}

OPTIMIZATION GUIDELINES:

1. **Quantifiable Impact**:
   - Model performance improvements (accuracy, precision, recall, F1)
   - Business metrics (revenue impact, cost savings, efficiency gains)
   - Scale of data and systems (dataset sizes, processing throughput)
   - Research contributions (publications, citations, patents)

2. **Technical Skills Showcase**:
   - ML frameworks and libraries (TensorFlow, PyTorch, scikit-learn)
   - Programming languages (Python, R, SQL, Scala)
   - Data engineering tools (Spark, Airflow, Kafka)
   - Cloud platforms (AWS, GCP, Azure ML)
   - Specializations (NLP, Computer Vision, Time Series, Recommender Systems)

3. **Executive Positioning**:
   - Emphasize end-to-end ML lifecycle experience
   - Highlight cross-functional collaboration (engineering, product, business)
   - Showcase ability to translate business problems to technical solutions
   - Demonstrate deployment and productionization experience

4. **Academic & Research Credentials**:
   - Educational background (MS, PhD) with relevant coursework
   - Research publications and conferences
   - Kaggle competitions or open-source contributions
   - Patents or technical blog posts

5. **Content Strategy**:
   - Lead with most impressive ML projects
   - Balance theory and practical application
   - Include both model development and deployment experience
   - Show progression from analysis to ML engineering to leadership

OUTPUT FORMAT:
Return optimized resume sections with emphasis on data-driven achievements.

IMPORTANT:
- Never exaggerate model performance metrics
- Clearly distinguish personal vs team contributions
- Maintain technical accuracy in methodology descriptions
- Ensure reproducibility claims are accurate
```

### Cover Letter Generation

```text
You are an expert cover letter writer specializing in executive-level persuasive communication for technical roles. Your goal is to craft a compelling, personalized cover letter that demonstrates genuine interest and strong fit.

INPUT CONTEXT:
- Candidate Background: {resume summary}
- Target Company: {company name and description}
- Target Role: {job title and key requirements}
- Job Description: {full job posting}

COVER LETTER STRUCTURE:

**Opening (2-3 sentences)**:
- Strong hook that shows genuine interest in company/mission
- Brief statement of relevant background
- Clear intent to apply for specific role

**Body Paragraph 1 - Relevant Experience**:
- 1-2 most impressive achievements directly relevant to role
- Specific examples with quantifiable results
- Technical skills alignment with job requirements
- Show understanding of role's challenges

**Body Paragraph 2 - Company Alignment**:
- Demonstrate research into company culture, products, mission
- Connect personal values/interests to company's work
- Explain why this opportunity specifically appeals
- Show authentic enthusiasm (not generic praise)

**Body Paragraph 3 - Unique Value**:
- What candidate uniquely brings to the table
- Cross-functional skills or unique perspective
- Leadership or collaboration strengths
- Forward-looking vision for impact in role

**Closing**:
- Confident expression of interest in next steps
- Thank you for consideration
- Professional sign-off

WRITING GUIDELINES:

1. **Tone**: Professional, confident, enthusiastic but not desperate
2. **Length**: 3-4 paragraphs, 300-400 words
3. **Specificity**: Use company name, role title, specific projects/products
4. **Authenticity**: Avoid generic phrases, make it personal
5. **Action-Oriented**: Use strong verbs, emphasize results
6. **Grammar**: Flawless grammar, varied sentence structure

AVOID:
- Clichés ("I am writing to express interest...")
- Restating entire resume
- Generic praise that could apply to any company
- Desperate or apologetic language
- Humor or overly casual tone
- Typos or formatting errors

OUTPUT FORMAT:
Full cover letter text ready for submission, with proper business letter formatting.
```

---

## Best Practices

### Prompt Engineering Tips

1. **Be Specific**: Clearly define the task, input context, and expected output format
2. **Provide Examples**: Include example inputs and outputs when possible
3. **Set Constraints**: Define what NOT to do (e.g., "never fabricate experience")
4. **Structure Well**: Use clear sections, bullet points, and formatting
5. **Iterate**: Clone templates to test variations and track performance

### Template Organization

1. **Naming Convention**: Use descriptive names like "Backend Engineer - Senior Level - Tech Startups"
2. **Version Control**: Clone templates before major changes to preserve working versions
3. **Active Management**: Deactivate outdated templates rather than deleting
4. **Role Specificity**: Create role-specific templates for best results

### Usage Tracking

1. **Satisfaction Scores**: Rate generated content to improve template selection
2. **Monitor Stats**: Check `times_used` and `avg_satisfaction_score` regularly
3. **A/B Testing**: Create variations and compare performance
4. **Iterate**: Update prompts based on real-world results

### Security & Privacy

1. **User Isolation**: Templates are private to each user
2. **No Sharing**: Cannot access or copy other users' templates
3. **Data Privacy**: Prompt text is stored securely, not exposed in logs
4. **Deletion**: Permanent deletion ensures no data retention

---

## Common Workflows

### Creating Your First Template

```bash
# 1. Create a basic template
POST /api/v1/prompt-templates
{
  "task_type": "resume_tailor",
  "role_type": "backend_engineer",
  "name": "My Backend Resume Template",
  "prompt_text": "..."
}

# 2. Test it with a resume (future endpoint)
POST /api/v1/resumes/{resume_id}/tailor
{
  "job_id": "...",
  "prompt_template_id": "..."
}

# 3. Rate the result
PATCH /api/v1/prompt-templates/{id}/usage
{
  "satisfaction_score": 4.5
}

# 4. Clone for experimentation
POST /api/v1/prompt-templates/{id}/duplicate
{
  "name": "Backend Resume - Experimental V2",
  "prompt_text": "... modified prompt ..."
}
```

### Managing Multiple Templates

```bash
# List all active resume templates
GET /api/v1/prompt-templates?task_type=resume_tailor&is_active=true

# Find best performing template
GET /api/v1/prompt-templates?task_type=resume_tailor
# Sort by avg_satisfaction_score in application code

# Deactivate old template
PUT /api/v1/prompt-templates/{id}
{
  "is_active": false
}
```

---

## Roadmap

**Phase 1** (Current): Template CRUD, versioning, usage tracking
**Phase 2** (Next): OpenAI integration, actual resume tailoring
**Phase 3**: Cover letter generation API
**Phase 4**: Form answer generation
**Phase 5**: Template marketplace (optional future feature)

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/extremealexv/personal-ai-job-assistant/issues
- Documentation: See main README.md

Last Updated: January 1, 2026
