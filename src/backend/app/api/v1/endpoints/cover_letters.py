"""Cover letter API endpoints."""

from math import ceil
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.cover_letter import (
    CoverLetterCreate,
    CoverLetterListResponse,
    CoverLetterResponse,
    CoverLetterSearchParams,
    CoverLetterUpdate,
    CoverLetterVersionsResponse,
)
from app.services import cover_letter_service

router = APIRouter()


@router.post(
    "/",
    response_model=CoverLetterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create cover letter",
    description="Create a new cover letter for an application",
)
async def create_cover_letter(
    data: CoverLetterCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CoverLetterResponse:
    """Create a new cover letter."""
    cover_letter = await cover_letter_service.create_cover_letter(
        db, current_user.id, data
    )
    return CoverLetterResponse.model_validate(cover_letter)


@router.get(
    "/",
    response_model=CoverLetterListResponse,
    summary="List cover letters",
    description="Get paginated list of cover letters with optional filters",
)
async def list_cover_letters(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    application_id: Annotated[UUID | None, Query(description="Filter by application")] = None,
    is_active: Annotated[bool | None, Query(description="Filter by active status")] = None,
    ai_model_used: Annotated[str | None, Query(description="Filter by AI model")] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    sort_by: Annotated[str, Query(description="Sort field")] = "created_at",
    sort_order: Annotated[str, Query(description="Sort order (asc/desc)")] = "desc",
) -> CoverLetterListResponse:
    """Get paginated list of cover letters."""
    params = CoverLetterSearchParams(
        application_id=application_id,
        is_active=is_active,
        ai_model_used=ai_model_used,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    
    cover_letters, total = await cover_letter_service.get_user_cover_letters(
        db, current_user.id, params
    )
    
    return CoverLetterListResponse(
        items=[CoverLetterResponse.model_validate(cl) for cl in cover_letters],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total > 0 else 0,
    )


@router.get(
    "/application/{application_id}",
    response_model=CoverLetterVersionsResponse,
    summary="Get cover letter versions",
    description="Get all versions of cover letters for an application",
)
async def get_cover_letter_versions(
    application_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CoverLetterVersionsResponse:
    """Get all cover letter versions for an application."""
    cover_letters = await cover_letter_service.get_cover_letters_by_application(
        db, application_id, current_user.id
    )
    
    # Find active version
    active_version = next((cl for cl in cover_letters if cl.is_active), None)
    
    return CoverLetterVersionsResponse(
        application_id=application_id,
        versions=[CoverLetterResponse.model_validate(cl) for cl in cover_letters],
        active_version=CoverLetterResponse.model_validate(active_version) if active_version else None,
    )


@router.get(
    "/{cover_letter_id}",
    response_model=CoverLetterResponse,
    summary="Get cover letter",
    description="Get a specific cover letter by ID",
)
async def get_cover_letter(
    cover_letter_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CoverLetterResponse:
    """Get a specific cover letter by ID."""
    cover_letter = await cover_letter_service.get_cover_letter(
        db, cover_letter_id, current_user.id
    )
    return CoverLetterResponse.model_validate(cover_letter)


@router.put(
    "/{cover_letter_id}",
    response_model=CoverLetterResponse,
    summary="Update cover letter",
    description="Update an existing cover letter",
)
async def update_cover_letter(
    cover_letter_id: UUID,
    data: CoverLetterUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CoverLetterResponse:
    """Update an existing cover letter."""
    cover_letter = await cover_letter_service.update_cover_letter(
        db, cover_letter_id, current_user.id, data
    )
    return CoverLetterResponse.model_validate(cover_letter)


@router.patch(
    "/application/{application_id}/activate/{version_number}",
    response_model=CoverLetterResponse,
    summary="Activate cover letter version",
    description="Set a specific version as the active cover letter",
)
async def activate_version(
    application_id: UUID,
    version_number: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CoverLetterResponse:
    """Set a specific version as the active cover letter."""
    cover_letter = await cover_letter_service.set_active_version(
        db, application_id, version_number, current_user.id
    )
    return CoverLetterResponse.model_validate(cover_letter)


@router.delete(
    "/{cover_letter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete cover letter",
    description="Delete a cover letter",
)
async def delete_cover_letter(
    cover_letter_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a cover letter."""
    await cover_letter_service.delete_cover_letter(db, cover_letter_id, current_user.id)
