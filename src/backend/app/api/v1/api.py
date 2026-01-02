"""API v1 router and endpoint aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai_cover_letter,
    ai_resume,
    analytics,
    applications,
    auth,
    cover_letters,
    health,
    jobs,
    prompt_templates,
    resumes,
    search,
)

# Create main v1 router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(applications.router, prefix="/applications", tags=["Applications"])
api_router.include_router(cover_letters.router, prefix="/cover-letters", tags=["Cover Letters"])
api_router.include_router(prompt_templates.router, prefix="/prompt-templates", tags=["Prompt Templates"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(ai_resume.router, prefix="/ai/resume", tags=["AI Resume Tailoring"])
api_router.include_router(ai_cover_letter.router, prefix="/ai/cover-letter", tags=["AI Cover Letter"])

# TODO: Add more routers as they are implemented
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
