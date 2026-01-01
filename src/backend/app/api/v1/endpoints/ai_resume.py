"""API endpoints for AI-powered resume tailoring."""
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id, get_db
from app.core.ai_exceptions import AIProviderError, RateLimitError
from app.schemas.resume import ResumeVersionResponse, ResumeTailoringRequest
from app.services.ai_resume_tailoring_service import ai_resume_tailoring_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/tailor", response_model=ResumeVersionResponse, status_code=status.HTTP_201_CREATED)
async def tailor_resume(
    request: ResumeTailoringRequest,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Tailor a master resume for a specific job posting using AI.

    This endpoint:
    1. Fetches the master resume and job posting
    2. Uses an AI model to optimize the resume for the job
    3. Creates a new resume version with modifications tracked
    4. Applies rate limiting and cost tracking

    **Rate Limits:**
    - 10 requests per minute
    - 100 requests per day

    **Cost:**
    - Estimated $0.05-0.15 per request (GPT-4)
    - Monthly budget limit: $100
    """
    try:
        resume_version = await ai_resume_tailoring_service.tailor_resume_for_job(
            db=db,
            user_id=user_id,
            master_resume_id=request.master_resume_id,
            job_posting_id=request.job_posting_id,
            prompt_template_id=request.prompt_template_id,
            version_name=request.version_name,
        )

        return resume_version

    except ValueError as e:
        logger.warning(f"Invalid request: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
            headers={"Retry-After": str(e.retry_after)},
        )

    except AIProviderError as e:
        logger.error(f"AI provider error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service temporarily unavailable: {str(e)}",
        )

    except Exception as e:
        logger.error(f"Unexpected error tailoring resume: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while tailoring the resume",
        )


@router.get("/{resume_version_id}/diff")
async def get_resume_diff(
    resume_version_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get the differences between master resume and tailored version.

    Shows what modifications were made by the AI to optimize the resume
    for the specific job posting.
    """
    try:
        diff = await ai_resume_tailoring_service.get_resume_diff(
            db=db, resume_version_id=resume_version_id, user_id=user_id
        )

        return diff

    except ValueError as e:
        logger.warning(f"Resume version not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        logger.error(f"Error getting resume diff: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
