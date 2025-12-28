"""Job posting API endpoints."""

from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.job import (
    JobPostingCreate,
    JobPostingListResponse,
    JobPostingResponse,
    JobPostingUpdate,
    JobSearchParams,
    JobStatsResponse,
    JobStatusUpdate,
)
from app.services.job_service import JobService

router = APIRouter()


@router.post(
    "",
    response_model=JobPostingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create job posting",
    description="Save a new job posting for the authenticated user"
)
async def create_job_posting(
    job_data: JobPostingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> JobPostingResponse:
    """Create a new job posting."""
    job = await JobService.create_job_posting(db, current_user.id, job_data)
    return JobPostingResponse.model_validate(job)


@router.get(
    "",
    response_model=JobPostingListResponse,
    summary="List job postings",
    description="Get paginated list of job postings with optional filtering"
)
async def list_job_postings(
    query: str = Query(None, description="Search query"),
    company: str = Query(None, description="Filter by company"),
    status: str = Query(None, description="Filter by status"),
    interest_level: int = Query(None, ge=1, le=5, description="Filter by interest level"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> JobPostingListResponse:
    """List job postings with filtering and pagination."""
    # Create search params
    search_params = JobSearchParams(
        query=query,
        company=company,
        status=status,
        interest_level=interest_level,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    jobs, total = await JobService.get_user_job_postings(db, current_user.id, search_params)
    
    total_pages = ceil(total / page_size) if total > 0 else 0
    
    return JobPostingListResponse(
        items=[JobPostingResponse.model_validate(job) for job in jobs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/search",
    response_model=JobPostingListResponse,
    summary="Search job postings",
    description="Search job postings by keywords in description"
)
async def search_job_postings(
    query: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> JobPostingListResponse:
    """Search job postings by keywords."""
    search_params = JobSearchParams(
        query=query,
        page=page,
        page_size=page_size
    )
    
    jobs, total = await JobService.get_user_job_postings(db, current_user.id, search_params)
    
    total_pages = ceil(total / page_size) if total > 0 else 0
    
    return JobPostingListResponse(
        items=[JobPostingResponse.model_validate(job) for job in jobs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/stats",
    response_model=JobStatsResponse,
    summary="Get job statistics",
    description="Get comprehensive job posting statistics"
)
async def get_job_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> JobStatsResponse:
    """Get job posting statistics."""
    return await JobService.get_job_stats(db, current_user.id)


@router.get(
    "/{job_id}",
    response_model=JobPostingResponse,
    summary="Get job posting",
    description="Get a specific job posting by ID"
)
async def get_job_posting(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> JobPostingResponse:
    """Get a job posting by ID."""
    job = await JobService.get_job_posting(db, job_id, current_user.id)
    return JobPostingResponse.model_validate(job)


@router.put(
    "/{job_id}",
    response_model=JobPostingResponse,
    summary="Update job posting",
    description="Update a job posting's information"
)
async def update_job_posting(
    job_id: UUID,
    job_data: JobPostingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> JobPostingResponse:
    """Update a job posting."""
    job = await JobService.update_job_posting(db, job_id, current_user.id, job_data)
    return JobPostingResponse.model_validate(job)


@router.patch(
    "/{job_id}/status",
    response_model=JobPostingResponse,
    summary="Update job status",
    description="Update the status of a job posting"
)
async def update_job_status(
    job_id: UUID,
    status_data: JobStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> JobPostingResponse:
    """Update job posting status."""
    job = await JobService.update_job_status(db, job_id, current_user.id, status_data)
    return JobPostingResponse.model_validate(job)


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete job posting",
    description="Soft delete a job posting"
)
async def delete_job_posting(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """Delete a job posting (soft delete)."""
    await JobService.delete_job_posting(db, job_id, current_user.id)
