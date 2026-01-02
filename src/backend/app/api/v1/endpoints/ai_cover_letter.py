"""API endpoints for AI-powered cover letter generation."""
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user_id, get_db
from app.core.ai_exceptions import AIProviderError
from app.schemas.cover_letter import CoverLetterResponse
from app.services.ai_cover_letter_service import ai_cover_letter_service

logger = logging.getLogger(__name__)

router = APIRouter()


class GenerateCoverLetterRequest(BaseModel):
    """Request model for AI cover letter generation."""

    application_id: UUID = Field(..., description="Application to generate cover letter for")
    prompt_template_id: Optional[UUID] = Field(
        None, description="Optional custom prompt template ID"
    )


@router.post(
    "/generate",
    response_model=CoverLetterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate AI-powered cover letter",
    response_description="Generated cover letter",
)
async def generate_cover_letter(
    request: GenerateCoverLetterRequest,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """
    Generate an AI-powered cover letter for an application.

    This endpoint uses the configured AI provider (OpenAI or Gemini) to generate
    a personalized, executive-level cover letter based on:
    - The tailored resume used in the application
    - The job posting details
    - A customizable prompt template

    **Required:**
    - Application must exist and belong to the user
    - Application must have an associated resume version and job posting
    - At least one active cover letter prompt template must exist

    **Process:**
    1. Fetches application, job, and resume data
    2. Creates resume summary from tailored resume
    3. Generates cover letter using AI provider
    4. Saves as new version with auto-incrementing version number
    5. First version is automatically set as active

    **Response:**
    - Returns the generated cover letter with metadata
    - Includes AI model used and generation timestamp
    - Content is plain text, ready for use or editing

    **Notes:**
    - Uses prompt template from request or default if not specified
    - Costs $0 when using free-tier AI models (Gemini)
    - Response time typically 5-15 seconds
    """
    try:
        cover_letter = await ai_cover_letter_service.generate_cover_letter(
            db=db,
            application_id=request.application_id,
            user_id=user_id,
            prompt_template_id=request.prompt_template_id,
        )
        return CoverLetterResponse.model_validate(cover_letter)

    except ValueError as e:
        logger.warning(f"Invalid cover letter generation request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except AIProviderError as e:
        logger.error(f"AI provider error during cover letter generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable. Please try again later.",
        )

    except Exception as e:
        logger.exception(f"Unexpected error generating cover letter: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating the cover letter",
        )
