"""Application management API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.application import Application
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationListResponse,
    ApplicationResponse,
    ApplicationSearchParams,
    ApplicationStatsResponse,
    ApplicationStatusUpdate,
    ApplicationUpdate,
)
from app.services import application_service

router = APIRouter()


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    data: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationResponse:
    """Create a new application."""
    application = await application_service.create_application(db, current_user.id, data)

    # Eagerly load the job_posting relationship to avoid lazy loading issues
    await db.refresh(application, ["job_posting"])

    # Convert to response with job details
    response = ApplicationResponse.model_validate(application)
    response.job_company_name = application.job_posting.company_name
    response.job_title = application.job_posting.job_title

    return response


@router.get("", response_model=ApplicationListResponse)
async def list_applications(
    page: int = 1,
    page_size: int = 20,
    job_posting_id: UUID | None = None,
    status: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationListResponse:
    """Get list of applications with filters and pagination."""
    try:
        search_params = ApplicationSearchParams(
            page=page,
            page_size=page_size,
            job_posting_id=job_posting_id,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    applications, total = await application_service.get_user_applications(
        db, current_user.id, search_params
    )

    # Convert to response models with job details
    items = []
    for app in applications:
        response = ApplicationResponse.model_validate(app)
        response.job_company_name = app.job_posting.company_name
        response.job_title = app.job_posting.job_title
        items.append(response)

    total_pages = (total + page_size - 1) // page_size

    return ApplicationListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/stats", response_model=ApplicationStatsResponse)
async def get_application_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationStatsResponse:
    """Get application statistics."""
    return await application_service.get_application_stats(db, current_user.id)


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationResponse:
    """Get a specific application by ID."""
    try:
        application = await application_service.get_application(
            db, application_id, current_user.id
        )

        # Convert to response with job details
        response = ApplicationResponse.model_validate(application)
        response.job_company_name = application.job_posting.company_name
        response.job_title = application.job_posting.job_title

        return response
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: UUID,
    data: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationResponse:
    """Update an existing application."""
    try:
        application = await application_service.update_application(
            db, application_id, current_user.id, data
        )

        # Convert to response with job details
        response = ApplicationResponse.model_validate(application)
        response.job_company_name = application.job_posting.company_name
        response.job_title = application.job_posting.job_title

        return response
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/{application_id}/status", response_model=ApplicationResponse)
async def update_application_status(
    application_id: UUID,
    data: ApplicationStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApplicationResponse:
    """Update application status."""
    try:
        application = await application_service.update_application_status(
            db, application_id, current_user.id, data.status
        )

        # Convert to response with job details
        response = ApplicationResponse.model_validate(application)
        response.job_company_name = application.job_posting.company_name
        response.job_title = application.job_posting.job_title

        return response
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete an application."""
    try:
        await application_service.delete_application(db, application_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
