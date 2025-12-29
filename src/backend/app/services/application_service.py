"""Application service layer - business logic for application management."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.job import Application, ApplicationStatus, JobPosting, JobStatus
from app.schemas.application import (
    ApplicationCreate,
    ApplicationSearchParams,
    ApplicationStatsResponse,
    ApplicationUpdate,
)


async def create_application(
    db: AsyncSession, user_id: UUID, data: ApplicationCreate
) -> Application:
    """
    Create a new application.

    Args:
        db: Database session
        user_id: ID of the user creating the application
        data: Application creation data

    Returns:
        Created application

    Raises:
        NotFoundError: If job posting or resume version not found
        ForbiddenError: If job posting or resume version belongs to another user
    """
    # Verify job posting exists and belongs to user
    job_result = await db.execute(
        select(JobPosting).where(
            and_(JobPosting.id == data.job_posting_id, JobPosting.deleted_at.is_(None))
        )
    )
    job_posting = job_result.scalar_one_or_none()

    if not job_posting:
        raise NotFoundError(f"Job posting {data.job_posting_id} not found")

    if job_posting.user_id != user_id:
        raise ForbiddenError("Cannot create application for another user's job posting")

    # Create application
    application = Application(
        user_id=user_id,
        job_posting_id=data.job_posting_id,
        resume_version_id=data.resume_version_id,
        submitted_at=data.submitted_at,
        submission_method=data.submission_method,
        status=data.status or ApplicationStatus.DRAFT,
        status_updated_at=datetime.utcnow(),
        demographics_data=data.demographics_data,
        last_follow_up_date=data.last_follow_up_date,
        next_follow_up_date=data.next_follow_up_date,
        follow_up_notes=data.follow_up_notes,
    )

    db.add(application)
    await db.flush()

    # If status is SUBMITTED and job is still in SAVED/PREPARED, update to APPLIED
    if application.status == ApplicationStatus.SUBMITTED:
        if job_posting.status in (JobStatus.SAVED, JobStatus.PREPARED):
            job_posting.status = JobStatus.APPLIED
            job_posting.status_updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(application)

    return application


async def get_application(
    db: AsyncSession, application_id: UUID, user_id: UUID
) -> Application:
    """
    Get application by ID with authorization check.

    Args:
        db: Database session
        application_id: Application ID
        user_id: ID of the requesting user

    Returns:
        Application object

    Raises:
        NotFoundError: If application not found
        ForbiddenError: If application belongs to another user
    """
    result = await db.execute(
        select(Application)
        .options(joinedload(Application.job_posting))
        .where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise NotFoundError(f"Application {application_id} not found")

    if application.user_id != user_id:
        raise ForbiddenError("Cannot access another user's application")

    return application


async def get_user_applications(
    db: AsyncSession, user_id: UUID, params: ApplicationSearchParams
) -> tuple[list[Application], int]:
    """
    Get user's applications with filters, pagination, and sorting.

    Args:
        db: Database session
        user_id: User ID
        params: Search and filter parameters

    Returns:
        Tuple of (applications list, total count)
    """
    # Base query
    query = (
        select(Application)
        .options(joinedload(Application.job_posting))
        .where(Application.user_id == user_id)
    )

    # Apply filters
    if params.job_posting_id:
        query = query.where(Application.job_posting_id == params.job_posting_id)

    if params.status:
        query = query.where(Application.status == params.status)

    if params.submitted_after:
        query = query.where(Application.submitted_at >= params.submitted_after)

    if params.submitted_before:
        query = query.where(Application.submitted_at <= params.submitted_before)

    # Count total before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply sorting
    sort_column = getattr(Application, params.sort_by)
    if params.sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    offset = (params.page - 1) * params.page_size
    query = query.offset(offset).limit(params.page_size)

    # Execute query
    result = await db.execute(query)
    applications = list(result.scalars().all())

    return applications, total


async def update_application(
    db: AsyncSession, application_id: UUID, user_id: UUID, data: ApplicationUpdate
) -> Application:
    """
    Update an existing application.

    Args:
        db: Database session
        application_id: Application ID
        user_id: ID of the requesting user
        data: Update data

    Returns:
        Updated application

    Raises:
        NotFoundError: If application not found
        ForbiddenError: If application belongs to another user
    """
    application = await get_application(db, application_id, user_id)

    # Update fields if provided
    if data.resume_version_id is not None:
        application.resume_version_id = data.resume_version_id

    if data.submitted_at is not None:
        application.submitted_at = data.submitted_at

    if data.submission_method is not None:
        application.submission_method = data.submission_method

    if data.demographics_data is not None:
        application.demographics_data = data.demographics_data

    if data.last_follow_up_date is not None:
        application.last_follow_up_date = data.last_follow_up_date

    if data.next_follow_up_date is not None:
        application.next_follow_up_date = data.next_follow_up_date

    if data.follow_up_notes is not None:
        application.follow_up_notes = data.follow_up_notes

    await db.commit()
    await db.refresh(application)

    return application


async def update_application_status(
    db: AsyncSession, application_id: UUID, user_id: UUID, new_status: ApplicationStatus
) -> Application:
    """
    Update application status.

    Args:
        db: Database session
        application_id: Application ID
        user_id: ID of the requesting user
        new_status: New status

    Returns:
        Updated application

    Raises:
        NotFoundError: If application not found
        ForbiddenError: If application belongs to another user
    """
    application = await get_application(db, application_id, user_id)

    application.status = new_status
    application.status_updated_at = datetime.utcnow()

    # If status changes to SUBMITTED, update job status if needed
    if new_status == ApplicationStatus.SUBMITTED:
        job_result = await db.execute(
            select(JobPosting).where(JobPosting.id == application.job_posting_id)
        )
        job_posting = job_result.scalar_one()

        if job_posting.status in (JobStatus.SAVED, JobStatus.PREPARED):
            job_posting.status = JobStatus.APPLIED
            job_posting.status_updated_at = datetime.utcnow()

    # Update job status based on application status
    if new_status in (
        ApplicationStatus.PHONE_SCREEN,
        ApplicationStatus.TECHNICAL,
        ApplicationStatus.ONSITE,
    ):
        job_result = await db.execute(
            select(JobPosting).where(JobPosting.id == application.job_posting_id)
        )
        job_posting = job_result.scalar_one()

        if job_posting.status != JobStatus.INTERVIEWING:
            job_posting.status = JobStatus.INTERVIEWING
            job_posting.status_updated_at = datetime.utcnow()

    elif new_status == ApplicationStatus.OFFER:
        job_result = await db.execute(
            select(JobPosting).where(JobPosting.id == application.job_posting_id)
        )
        job_posting = job_result.scalar_one()

        if job_posting.status != JobStatus.OFFER:
            job_posting.status = JobStatus.OFFER
            job_posting.status_updated_at = datetime.utcnow()

    elif new_status == ApplicationStatus.REJECTED:
        job_result = await db.execute(
            select(JobPosting).where(JobPosting.id == application.job_posting_id)
        )
        job_posting = job_result.scalar_one()

        if job_posting.status != JobStatus.REJECTED:
            job_posting.status = JobStatus.REJECTED
            job_posting.status_updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(application)

    return application


async def delete_application(
    db: AsyncSession, application_id: UUID, user_id: UUID
) -> None:
    """
    Delete an application (hard delete).

    Args:
        db: Database session
        application_id: Application ID
        user_id: ID of the requesting user

    Raises:
        NotFoundError: If application not found
        ForbiddenError: If application belongs to another user
    """
    application = await get_application(db, application_id, user_id)

    await db.delete(application)
    await db.commit()


async def get_application_stats(
    db: AsyncSession, user_id: UUID
) -> ApplicationStatsResponse:
    """
    Get application statistics for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Application statistics
    """
    # Total applications
    total_result = await db.execute(
        select(func.count(Application.id)).where(Application.user_id == user_id)
    )
    total_applications = total_result.scalar_one()

    # Count by status
    status_result = await db.execute(
        select(Application.status, func.count(Application.id))
        .where(Application.user_id == user_id)
        .group_by(Application.status)
    )
    by_status = {str(status): count for status, count in status_result.all()}

    # Submitted and draft counts
    submitted_count = sum(
        count
        for status, count in by_status.items()
        if status != str(ApplicationStatus.DRAFT)
    )
    draft_count = by_status.get(str(ApplicationStatus.DRAFT), 0)

    # Response rate (applications with non-draft, non-submitted status)
    response_count = sum(
        count
        for status, count in by_status.items()
        if status
        not in (str(ApplicationStatus.DRAFT), str(ApplicationStatus.SUBMITTED))
    )
    response_rate = (
        (response_count / submitted_count * 100) if submitted_count > 0 else None
    )

    # Average days to response (simplified - would need email tracking in full implementation)
    avg_days_to_response = None

    # Recent applications (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_result = await db.execute(
        select(func.count(Application.id))
        .where(Application.user_id == user_id)
        .where(Application.created_at >= thirty_days_ago)
    )
    recent_applications_count = recent_result.scalar_one()

    return ApplicationStatsResponse(
        total_applications=total_applications,
        by_status=by_status,
        submitted_count=submitted_count,
        draft_count=draft_count,
        response_rate=response_rate,
        avg_days_to_response=avg_days_to_response,
        recent_applications_count=recent_applications_count,
    )
