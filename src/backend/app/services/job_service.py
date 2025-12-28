"""Job management service layer."""

import re
from collections import Counter
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.job import Application, ApplicationStatus, JobPosting, JobStatus
from app.schemas.job import (
    ApplicationCreate,
    ApplicationStatsResponse,
    ApplicationStatusUpdate,
    ApplicationUpdate,
    JobPostingCreate,
    JobPostingUpdate,
    JobSearchParams,
    JobStatsResponse,
    JobStatusUpdate,
)


class JobService:
    """Service for job posting management."""

    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 15) -> list[str]:
        """Extract relevant keywords from job description.
        
        Args:
            text: Job description or requirements text
            max_keywords: Maximum number of keywords to extract
            
        Returns:
            List of extracted keywords
        """
        if not text:
            return []
        
        # Common stop words to exclude
        stop_words = {
            "the", "and", "or", "is", "in", "to", "of", "for", "with", "on",
            "at", "from", "by", "an", "as", "be", "this", "that", "are", "was",
            "will", "have", "has", "had", "can", "may", "must", "should", "would",
            "a", "it", "we", "you", "they", "our", "your", "their"
        }
        
        # Extract words (letters and hyphens, 3+ chars)
        words = re.findall(r'\b[a-zA-Z][a-zA-Z-]{2,}\b', text.lower())
        
        # Filter stop words and count occurrences
        word_counts = Counter(
            word for word in words
            if word not in stop_words
        )
        
        # Get top keywords
        return [word for word, _ in word_counts.most_common(max_keywords)]

    @staticmethod
    async def create_job_posting(
        db: AsyncSession,
        user_id: UUID,
        job_data: JobPostingCreate
    ) -> JobPosting:
        """Create a new job posting.
        
        Args:
            db: Database session
            user_id: ID of the user creating the job
            job_data: Job posting data
            
        Returns:
            Created job posting
        """
        # Extract keywords from description
        extracted_keywords = JobService.extract_keywords(
            f"{job_data.job_description or ''} {job_data.requirements or ''}"
        )
        
        job = JobPosting(
            user_id=user_id,
            company_name=job_data.company_name,
            job_title=job_data.job_title,
            job_url=str(job_data.job_url),
            source=job_data.source,
            location=job_data.location,
            salary_range=job_data.salary_range,
            employment_type=job_data.employment_type,
            remote_policy=job_data.remote_policy,
            job_description=job_data.job_description,
            requirements=job_data.requirements,
            nice_to_have=job_data.nice_to_have,
            interest_level=job_data.interest_level,
            notes=job_data.notes,
            extracted_keywords=extracted_keywords,
            status=JobStatus.SAVED,
        )
        
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def get_job_posting(
        db: AsyncSession,
        job_id: UUID,
        user_id: UUID
    ) -> JobPosting:
        """Get a job posting by ID.
        
        Args:
            db: Database session
            job_id: Job posting ID
            user_id: User ID for authorization
            
        Returns:
            Job posting
            
        Raises:
            NotFoundError: If job not found or deleted
            ForbiddenError: If job belongs to different user
        """
        result = await db.execute(
            select(JobPosting).where(
                and_(
                    JobPosting.id == job_id,
                    JobPosting.deleted_at.is_(None)
                )
            )
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise NotFoundError("Job posting not found")
        
        if job.user_id != user_id:
            raise ForbiddenError("Access denied to this job posting")
        
        return job

    @staticmethod
    async def get_user_job_postings(
        db: AsyncSession,
        user_id: UUID,
        search_params: JobSearchParams
    ) -> tuple[list[JobPosting], int]:
        """Get paginated list of user's job postings with filtering.
        
        Args:
            db: Database session
            user_id: User ID
            search_params: Search and filter parameters
            
        Returns:
            Tuple of (jobs list, total count)
        """
        # Base query
        query = select(JobPosting).where(
            and_(
                JobPosting.user_id == user_id,
                JobPosting.deleted_at.is_(None)
            )
        )
        
        # Apply filters
        if search_params.company:
            query = query.where(
                JobPosting.company_name.ilike(f"%{search_params.company}%")
            )
        
        if search_params.status:
            query = query.where(JobPosting.status == search_params.status)
        
        if search_params.interest_level:
            query = query.where(JobPosting.interest_level == search_params.interest_level)
        
        # Full-text search on description
        if search_params.query:
            search_pattern = f"%{search_params.query}%"
            query = query.where(
                or_(
                    JobPosting.job_description.ilike(search_pattern),
                    JobPosting.requirements.ilike(search_pattern),
                    JobPosting.job_title.ilike(search_pattern),
                    JobPosting.company_name.ilike(search_pattern)
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply sorting
        sort_column = getattr(JobPosting, search_params.sort_by)
        if search_params.sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        offset = (search_params.page - 1) * search_params.page_size
        query = query.offset(offset).limit(search_params.page_size)
        
        # Execute query
        result = await db.execute(query)
        jobs = list(result.scalars().all())
        
        return jobs, total

    @staticmethod
    async def update_job_posting(
        db: AsyncSession,
        job_id: UUID,
        user_id: UUID,
        job_data: JobPostingUpdate
    ) -> JobPosting:
        """Update a job posting.
        
        Args:
            db: Database session
            job_id: Job posting ID
            user_id: User ID for authorization
            job_data: Updated job data
            
        Returns:
            Updated job posting
            
        Raises:
            NotFoundError: If job not found
            ForbiddenError: If job belongs to different user
        """
        job = await JobService.get_job_posting(db, job_id, user_id)
        
        # Update fields
        update_data = job_data.model_dump(exclude_unset=True)
        
        # Convert HttpUrl to string if present
        if "job_url" in update_data and update_data["job_url"]:
            update_data["job_url"] = str(update_data["job_url"])
        
        # Re-extract keywords if description changed
        if "job_description" in update_data or "requirements" in update_data:
            new_desc = update_data.get("job_description", job.job_description) or ""
            new_req = update_data.get("requirements", job.requirements) or ""
            update_data["extracted_keywords"] = JobService.extract_keywords(
                f"{new_desc} {new_req}"
            )
        
        for field, value in update_data.items():
            setattr(job, field, value)
        
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def update_job_status(
        db: AsyncSession,
        job_id: UUID,
        user_id: UUID,
        status_data: JobStatusUpdate
    ) -> JobPosting:
        """Update job posting status.
        
        Args:
            db: Database session
            job_id: Job posting ID
            user_id: User ID for authorization
            status_data: New status
            
        Returns:
            Updated job posting
            
        Raises:
            NotFoundError: If job not found
            ForbiddenError: If job belongs to different user
        """
        job = await JobService.get_job_posting(db, job_id, user_id)
        
        job.status = status_data.status
        job.status_updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def delete_job_posting(
        db: AsyncSession,
        job_id: UUID,
        user_id: UUID
    ) -> None:
        """Soft delete a job posting.
        
        Args:
            db: Database session
            job_id: Job posting ID
            user_id: User ID for authorization
            
        Raises:
            NotFoundError: If job not found
            ForbiddenError: If job belongs to different user
        """
        job = await JobService.get_job_posting(db, job_id, user_id)
        
        job.deleted_at = datetime.utcnow()
        
        await db.commit()

    @staticmethod
    async def get_job_stats(
        db: AsyncSession,
        user_id: UUID
    ) -> JobStatsResponse:
        """Get job posting statistics.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Job statistics
        """
        # Total jobs
        total_query = select(func.count(JobPosting.id)).where(
            and_(
                JobPosting.user_id == user_id,
                JobPosting.deleted_at.is_(None)
            )
        )
        total_result = await db.execute(total_query)
        total_jobs = total_result.scalar() or 0
        
        # Jobs by status
        status_query = select(
            JobPosting.status,
            func.count(JobPosting.id)
        ).where(
            and_(
                JobPosting.user_id == user_id,
                JobPosting.deleted_at.is_(None)
            )
        ).group_by(JobPosting.status)
        
        status_result = await db.execute(status_query)
        by_status = {str(status): count for status, count in status_result.all()}
        
        # Average interest level
        avg_query = select(func.avg(JobPosting.interest_level)).where(
            and_(
                JobPosting.user_id == user_id,
                JobPosting.deleted_at.is_(None),
                JobPosting.interest_level.is_not(None)
            )
        )
        avg_result = await db.execute(avg_query)
        avg_interest = avg_result.scalar()
        
        # Jobs with applications
        apps_query = select(func.count(func.distinct(JobPosting.id))).select_from(
            JobPosting
        ).join(
            Application, Application.job_posting_id == JobPosting.id
        ).where(
            and_(
                JobPosting.user_id == user_id,
                JobPosting.deleted_at.is_(None)
            )
        )
        apps_result = await db.execute(apps_query)
        total_with_applications = apps_result.scalar() or 0
        
        # Recent jobs (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_query = select(func.count(JobPosting.id)).where(
            and_(
                JobPosting.user_id == user_id,
                JobPosting.deleted_at.is_(None),
                JobPosting.created_at >= thirty_days_ago
            )
        )
        recent_result = await db.execute(recent_query)
        recent_jobs_count = recent_result.scalar() or 0
        
        return JobStatsResponse(
            total_jobs=total_jobs,
            by_status=by_status,
            avg_interest_level=float(avg_interest) if avg_interest else None,
            total_with_applications=total_with_applications,
            recent_jobs_count=recent_jobs_count
        )
