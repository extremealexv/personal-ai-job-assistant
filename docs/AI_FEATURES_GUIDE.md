# AI Features Usage Guide

**Last Updated:** January 2, 2026  
**Status:** ✅ Fully Operational

---

## Table of Contents

1. [Overview](#overview)
2. [Setup & Configuration](#setup--configuration)
3. [AI Resume Tailoring](#ai-resume-tailoring)
4. [AI Cover Letter Generation](#ai-cover-letter-generation)
5. [Prompt Templates](#prompt-templates)
6. [API Reference](#api-reference)
7. [Cost & Performance](#cost--performance)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## Overview

The Personal AI Job Assistant includes two AI-powered features that help optimize your job application materials:

### ✨ **AI Resume Tailoring**
Automatically optimizes your resume for specific job postings by:
- Extracting keywords from job descriptions
- Rewriting experience with executive-level impact
- Emphasizing quantifiable achievements
- Ensuring ATS (Applicant Tracking System) compatibility
- Tracking modifications for easy review

### ✨ **AI Cover Letter Generation**
Creates personalized, executive-level cover letters that:
- Align with company mission and values
- Highlight relevant experience for the role
- Use persuasive, professional tone
- Include quantifiable metrics
- Support multiple writing styles

---

## Setup & Configuration

### Prerequisites

1. **Python 3.11+** installed
2. **Backend server running** (`uvicorn app.main:app --reload --port 8000`)
3. **AI API key** (Gemini or OpenAI)

### Get AI API Keys

#### Option 1: Google Gemini (Recommended - Free Tier)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Get API key"
4. Copy your API key

**Benefits:**
- ✅ Free tier available (gemini-2.5-flash, gemini-2.0-flash)
- ✅ Fast response times (~8-10 seconds)
- ✅ No credit card required
- ✅ 60 requests per minute limit

#### Option 2: OpenAI (Paid)

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create account
3. Navigate to API Keys
4. Create new secret key
5. Copy your API key

**Benefits:**
- ✅ Highest quality output (GPT-4)
- ✅ More consistent formatting
- ✅ Better reasoning for complex scenarios

**Costs:**
- GPT-4: $0.03/1K prompt tokens, $0.06/1K completion tokens
- GPT-3.5-turbo: $0.001/1K tokens (both directions)

### Configure Environment

Edit `src/backend/.env`:

```env
# For Google Gemini (Free Tier)
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=4000
GEMINI_MAX_RETRIES=3

# For OpenAI (Optional)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=4000

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=10
```

### Verify Setup

Test your configuration:

```bash
# From src/backend directory
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Should return JWT token
```

---

## AI Resume Tailoring

### Workflow

```
Master Resume → Job Posting → AI Tailoring → Review → Download
```

### Step 1: Upload Master Resume

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/v1/resumes/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/resume.pdf" \
  -F "full_name=John Doe" \
  -F "email=john.doe@example.com"
```

**Response:**
```json
{
  "id": "77e0aab1-4b80-4d99-ad05-2c71c8865f52",
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "summary": "Experienced backend engineer...",
  "created_at": "2026-01-02T00:00:00Z"
}
```

### Step 2: Save Job Posting

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "TechCorp Inc.",
    "job_title": "Senior Backend Engineer",
    "job_url": "https://techcorp.com/careers/123",
    "job_description": "We are seeking a Senior Backend Engineer with 5+ years Python experience, expertise in FastAPI and microservices...",
    "location": "Remote",
    "employment_type": "Full-time"
  }'
```

**Response:**
```json
{
  "id": "33176128-a18c-4675-95fd-607e1f7b6e5d",
  "company_name": "TechCorp Inc.",
  "job_title": "Senior Backend Engineer",
  "status": "saved",
  "extracted_keywords": ["Python", "FastAPI", "microservices"],
  "created_at": "2026-01-02T00:10:00Z"
}
```

### Step 3: Generate Tailored Resume

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/resume/tailor" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "master_resume_id": "77e0aab1-4b80-4d99-ad05-2c71c8865f52",
    "job_posting_id": "33176128-a18c-4675-95fd-607e1f7b6e5d",
    "version_name": "TechCorp - Senior Backend Engineer",
    "target_role": "Senior Backend Engineer",
    "target_company": "TechCorp Inc."
  }'
```

**Response (after ~8-10 seconds):**
```json
{
  "id": "822d44e8-c8e1-4b10-a3ca-b41a2bd7715a",
  "master_resume_id": "77e0aab1-4b80-4d99-ad05-2c71c8865f52",
  "job_posting_id": "33176128-a18c-4675-95fd-607e1f7b6e5d",
  "version_name": "TechCorp - Senior Backend Engineer",
  "target_role": "Senior Backend Engineer",
  "target_company": "TechCorp Inc.",
  "modifications": {
    "summary": "Results-driven Senior Backend Engineer with 10+ years building scalable microservices architectures. Expert in Python, FastAPI, and distributed systems design. Proven track record of reducing latency by 40% and improving system reliability to 99.99%.",
    "work_experience": [
      {
        "company": "Previous Company",
        "title": "Backend Engineer",
        "achievements": [
          "Architected microservices platform handling 100M+ daily requests",
          "Implemented FastAPI-based REST APIs reducing response time by 40%",
          "Led migration to containerized infrastructure (Docker, Kubernetes)"
        ]
      }
    ],
    "skills": ["Python", "FastAPI", "Microservices", "Docker", "Kubernetes"]
  },
  "ai_model_used": "gemini-2.5-flash",
  "generation_timestamp": "2026-01-02T00:15:00Z",
  "created_at": "2026-01-02T00:15:00Z"
}
```

### Step 4: Review and Download

**Get Resume Version:**
```bash
curl -X GET "http://localhost:8000/api/v1/ai/resume/versions/822d44e8-c8e1-4b10-a3ca-b41a2bd7715a" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Download PDF/DOCX:**
```bash
# Generate PDF (implementation pending)
curl -X GET "http://localhost:8000/api/v1/ai/resume/versions/822d44e8-c8e1-4b10-a3ca-b41a2bd7715a/export?format=pdf" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output tailored_resume.pdf
```

### Customization Options

**Use Custom Prompt Template:**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/resume/tailor" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "master_resume_id": "77e0aab1-4b80-4d99-ad05-2c71c8865f52",
    "job_posting_id": "33176128-a18c-4675-95fd-607e1f7b6e5d",
    "version_name": "Custom Tailoring",
    "prompt_template_id": "your-custom-template-id"
  }'
```

---

## AI Cover Letter Generation

### Workflow

```
Application → Resume Version → Job Details → AI Generation → Review → Activate
```

### Step 1: Create Application

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/v1/applications" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_posting_id": "33176128-a18c-4675-95fd-607e1f7b6e5d",
    "resume_version_id": "822d44e8-c8e1-4b10-a3ca-b41a2bd7715a",
    "status": "draft"
  }'
```

**Response:**
```json
{
  "id": "24f17a0e-3bd5-4ed7-bd00-565e74f923d7",
  "job_posting_id": "33176128-a18c-4675-95fd-607e1f7b6e5d",
  "resume_version_id": "822d44e8-c8e1-4b10-a3ca-b41a2bd7715a",
  "job_company_name": "TechCorp Inc.",
  "job_title": "Senior Backend Engineer",
  "status": "draft",
  "created_at": "2026-01-02T00:20:00Z"
}
```

### Step 2: Generate Cover Letter

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/cover-letter/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "24f17a0e-3bd5-4ed7-bd00-565e74f923d7",
    "tone": "professional"
  }'
```

**Tone Options:**
- `professional` - Standard business tone (recommended)
- `enthusiastic` - High energy, passionate tone
- `formal` - Traditional, conservative tone
- `creative` - Innovative, storytelling approach

**Response (after ~8-10 seconds):**
```json
{
  "id": "2b296ded-eebe-463f-ad72-b8953dae166e",
  "application_id": "24f17a0e-3bd5-4ed7-bd00-565e74f923d7",
  "content": "Dear Hiring Manager,\n\nI am writing to express my strong interest in the Senior Backend Engineer position at TechCorp Inc. Your company's commitment to building scalable, high-performance systems aligns perfectly with my 10 years of experience architecting microservices platforms.\n\nAt my previous role, I led the development of a FastAPI-based platform handling 100M+ daily requests, reducing response time by 40% while maintaining 99.99% uptime. This experience has equipped me with the technical depth and leadership skills needed to contribute to TechCorp's mission.\n\nI am particularly drawn to TechCorp's innovative approach to distributed systems and would welcome the opportunity to discuss how my expertise in Python, FastAPI, and cloud infrastructure can drive your team's success.\n\nThank you for considering my application.\n\nBest regards,\nJohn Doe",
  "version_number": 1,
  "is_active": true,
  "ai_model_used": "gemini-2.5-flash",
  "generation_timestamp": "2026-01-02T00:25:00Z",
  "created_at": "2026-01-02T00:25:00Z"
}
```

### Step 3: Review and Iterate

**List All Versions:**
```bash
curl -X GET "http://localhost:8000/api/v1/ai/cover-letter/list?application_id=24f17a0e-3bd5-4ed7-bd00-565e74f923d7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Generate Alternative Version:**
```bash
# Try enthusiastic tone
curl -X POST "http://localhost:8000/api/v1/ai/cover-letter/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "24f17a0e-3bd5-4ed7-bd00-565e74f923d7",
    "tone": "enthusiastic"
  }'
```

**Activate Preferred Version:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/ai/cover-letter/2b296ded-eebe-463f-ad72-b8953dae166e/activate" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Customization Options

**Use Custom Prompt Template:**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/cover-letter/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "24f17a0e-3bd5-4ed7-bd00-565e74f923d7",
    "tone": "professional",
    "prompt_template_id": "your-custom-template-id"
  }'
```

---

## Prompt Templates

### What are Prompt Templates?

Prompt templates are customizable instructions that guide the AI in generating content. They support placeholders like `{master_resume}`, `{job_description}`, `{company_name}`, etc.

### Default Resume Tailoring Prompt

```text
You are an expert resume writer with 20+ years of experience helping candidates land jobs at top tech companies. 

Your task is to tailor this resume for the specific job posting below.

Master Resume (JSON format):
{master_resume}

Job Description:
{job_description}

Company: {company_name}

Instructions:
1. Analyze the job description and extract key requirements, skills, and keywords
2. Rewrite the professional summary to align with the role
3. Prioritize and reorder work experience to highlight relevant achievements
4. Quantify accomplishments with metrics where possible
5. Emphasize technical skills that match the job requirements
6. Use executive-level language and impact-driven storytelling
7. Ensure ATS compatibility by including extracted keywords naturally

Return ONLY valid JSON in this exact format:
{
  "modifications": {
    "summary": "Updated professional summary",
    "work_experience": [...],
    "skills": [...]
  }
}
```

### Default Cover Letter Prompt

```text
You are an expert cover letter writer specializing in executive-level professional communications.

Your task is to create a persuasive, personalized cover letter.

Resume Summary:
{resume_summary}

Job Description:
{job_description}

Company: {company_name}
Position: {job_title}

Instructions:
1. Address hiring manager professionally
2. Express genuine interest in the company and role
3. Highlight 2-3 most relevant achievements from resume
4. Include quantifiable metrics and impact
5. Demonstrate understanding of company mission/values
6. Use professional, executive-level tone
7. Keep to 3-4 paragraphs, ~300-400 words
8. Close with call to action

Return the cover letter as plain text (no JSON).
```

### Creating Custom Prompts

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/v1/prompt-templates/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "resume_tailor",
    "role_type": "data_scientist",
    "name": "Data Scientist Resume Tailoring",
    "prompt_text": "Custom prompt with {master_resume}, {job_description}...",
    "is_active": true
  }'
```

### Managing Prompts

**List All Prompts:**
```bash
curl -X GET "http://localhost:8000/api/v1/prompt-templates/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Update Prompt:**
```bash
curl -X PUT "http://localhost:8000/api/v1/prompt-templates/{prompt_id}" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_text": "Updated prompt text..."
  }'
```

---

## API Reference

### Resume Tailoring Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ai/resume/tailor` | Generate tailored resume |
| GET | `/api/v1/ai/resume/versions` | List all resume versions |
| GET | `/api/v1/ai/resume/versions/{id}` | Get version by ID |
| PUT | `/api/v1/ai/resume/versions/{id}` | Update version |
| DELETE | `/api/v1/ai/resume/versions/{id}` | Delete version |

### Cover Letter Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ai/cover-letter/generate` | Generate cover letter |
| GET | `/api/v1/ai/cover-letter/list` | List all versions |
| GET | `/api/v1/ai/cover-letter/{id}` | Get by ID |
| PUT | `/api/v1/ai/cover-letter/{id}` | Update content |
| PATCH | `/api/v1/ai/cover-letter/{id}/activate` | Activate version |
| DELETE | `/api/v1/ai/cover-letter/{id}` | Delete |

### Authentication

All AI endpoints require JWT authentication:

```bash
# 1. Login
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  | jq -r '.access_token')

# 2. Use token in requests
curl -X POST "http://localhost:8000/api/v1/ai/resume/tailor" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## Cost & Performance

### Google Gemini (Free Tier)

**Models:**
- `gemini-2.5-flash` - Latest, best performance (FREE)
- `gemini-2.0-flash` - Fast, efficient (FREE)
- `gemini-1.5-flash` - $0.000075/1K prompt, $0.0003/1K completion

**Limits:**
- 60 requests per minute
- 1500 requests per day (free tier)

**Performance:**
- Resume tailoring: ~8-10 seconds
- Cover letter generation: ~8-10 seconds
- Cost per request: **$0.00** (free tier)

### OpenAI (Paid)

**Models:**
- `gpt-4` - Highest quality
  - $0.03/1K prompt tokens
  - $0.06/1K completion tokens
  - Average cost: ~$0.10-0.20 per request
  
- `gpt-3.5-turbo` - Cost-effective
  - $0.001/1K tokens (both)
  - Average cost: ~$0.01-0.02 per request

**Performance:**
- Resume tailoring: ~5-8 seconds
- Cover letter generation: ~5-8 seconds

### Cost Tracking

View your AI usage:

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/ai-usage" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "total_requests": 25,
  "total_cost": 0.00,
  "by_provider": {
    "gemini": {
      "requests": 25,
      "cost": 0.00
    }
  },
  "by_task": {
    "resume_tailor": 15,
    "cover_letter": 10
  }
}
```

---

## Troubleshooting

### Common Issues

#### 1. "Invalid API Key" Error

**Symptom:**
```json
{
  "detail": "Invalid Gemini API key"
}
```

**Solution:**
- Verify API key in `.env` file
- Check key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Restart server after updating `.env`

#### 2. "Rate Limit Exceeded" Error

**Symptom:**
```json
{
  "detail": "Gemini API rate limit exceeded"
}
```

**Solution:**
- Wait 1 minute and retry
- Free tier limit: 60 requests/minute
- Consider upgrading to paid tier

#### 3. JSON Parsing Error

**Symptom:**
```json
{
  "detail": "Could not parse AI response as JSON"
}
```

**Solution:**
- Usually auto-handled by fallback patterns
- Check server logs for full response
- Try regenerating with different prompt

#### 4. Slow Response Times

**Symptom:**
Requests taking >15 seconds

**Solution:**
- Normal for complex resumes (10-15 seconds)
- Check internet connection
- Verify server is running (not sleeping)
- Try smaller `max_tokens` value

#### 5. Empty or Invalid Content

**Symptom:**
AI returns generic or off-topic content

**Solution:**
- Ensure job description is detailed
- Check master resume has sufficient content
- Try different tone for cover letters
- Use custom prompt template

### Debug Mode

Enable detailed logging:

```bash
# Edit src/backend/app/config.py
LOG_LEVEL=DEBUG

# Or set environment variable
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload
```

View logs:
```bash
# Check server logs for:
# - Full AI responses
# - JSON parsing attempts
# - API call details
# - Error tracebacks
```

### Test API Connection

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test AI endpoint without auth (should return 401)
curl -X POST "http://localhost:8000/api/v1/ai/resume/tailor"

# Test with auth
curl -X POST "http://localhost:8000/api/v1/ai/resume/tailor" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## Best Practices

### Resume Tailoring

1. **Use Detailed Job Descriptions**
   - Include full job description, not just bullet points
   - Better input = better output

2. **Review Before Using**
   - Always review AI-generated content
   - Verify all facts and dates are accurate
   - Ensure tone matches your voice

3. **Iterate with Feedback**
   - Generate multiple versions
   - Compare results
   - Refine prompts based on output

4. **Maintain Master Resume**
   - Keep master resume up-to-date
   - Include all achievements
   - Use quantifiable metrics

### Cover Letter Generation

1. **Choose Appropriate Tone**
   - `professional` - Most corporate roles
   - `enthusiastic` - Startups, mission-driven companies
   - `formal` - Government, finance, legal
   - `creative` - Design, marketing, creative agencies

2. **Generate Multiple Versions**
   - Try different tones
   - Compare effectiveness
   - A/B test if possible

3. **Personalize Further**
   - Add specific company research
   - Mention recent news/achievements
   - Reference specific team members (if appropriate)

4. **Keep It Concise**
   - AI generates ~300-400 words
   - Edit down if needed
   - Focus on top 2-3 achievements

### General AI Tips

1. **Start with Free Tier**
   - Gemini free tier is excellent
   - Upgrade to paid only if needed

2. **Track Performance**
   - Monitor which versions get responses
   - Note which prompts work best
   - Iterate based on results

3. **Maintain Context**
   - Link resumes → jobs → applications
   - Keep data organized
   - Use version control

4. **Stay Authentic**
   - AI enhances, doesn't replace you
   - Ensure content reflects your experience
   - Use your voice and personality

---

## Support & Feedback

### Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/extremealexv/personal-ai-job-assistant/issues)
- **Documentation**: [Full project docs](https://github.com/extremealexv/personal-ai-job-assistant)
- **API Reference**: [OpenAPI docs](http://localhost:8000/docs)

### Contributing

We welcome contributions! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

### License

MIT License - See [LICENSE](../LICENSE) for details.

---

**Happy Job Hunting!** 🚀
