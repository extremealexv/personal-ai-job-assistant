"""Unit tests for job service layer."""

import pytest
from uuid import uuid4

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.job import JobStatus
from app.schemas.job import (
    JobPostingCreate,
    JobPostingUpdate,
    JobSearchParams,
    JobStatusUpdate,
)
from app.services.job_service import JobService


pytestmark = [pytest.mark.unit, pytest.mark.asyncio, pytest.mark.job_management]


class TestKeywordExtraction:
    """Test keyword extraction functionality."""

    def test_extract_keywords_basic(self):
        """Test basic keyword extraction."""
        text = "Python FastAPI PostgreSQL Redis Docker Kubernetes"
        keywords = JobService.extract_keywords(text)
        
        assert "python" in keywords
        assert "fastapi" in keywords
        assert "postgresql" in keywords

    def test_extract_keywords_with_stop_words(self):
        """Test that stop words are filtered out."""
        text = "The company is looking for a Python developer with experience in FastAPI"
        keywords = JobService.extract_keywords(text)
        
        assert "the" not in keywords
        assert "is" not in keywords
        assert "a" not in keywords
        assert "python" in keywords
        assert "fastapi" in keywords

    def test_extract_keywords_with_repetition(self):
        """Test that repeated words are prioritized."""
        text = "Python Python Python FastAPI Python experience Python skills"
        keywords = JobService.extract_keywords(text)
        
        # Python should be first due to frequency
        assert keywords[0] == "python"

    def test_extract_keywords_empty_text(self):
        """Test keyword extraction with empty text."""
        keywords = JobService.extract_keywords("")
        assert keywords == []

    def test_extract_keywords_max_limit(self):
        """Test keyword extraction respects max limit."""
        text = " ".join([f"word{i}" for i in range(50)])
        keywords = JobService.extract_keywords(text, max_keywords=10)
        
        assert len(keywords) <= 10

    def test_extract_keywords_case_insensitive(self):
        """Test that keywords are lowercase."""
        text = "Python FASTAPI PostgreSQL"
        keywords = JobService.extract_keywords(text)
        
        assert all(k.islower() for k in keywords)


@pytest.mark.asyncio
class TestJobServiceCRUD:
    """Test job service CRUD operations."""

    async def test_create_job_posting(self, db_session, test_user):
        """Test creating a job posting."""
        job_data = JobPostingCreate(
            company_name="TestCorp",
            job_title="Test Engineer",
            job_url="https://testcorp.com/jobs/test-engineer",
            job_description="Test job description with Python and FastAPI",
            requirements="Python experience required"
        )
        
        job = await JobService.create_job_posting(db_session, test_user["id"], job_data)
        
        assert job.id is not None
        assert job.company_name == "TestCorp"
        assert job.job_title == "Test Engineer"
        assert job.status == JobStatus.SAVED
        assert len(job.extracted_keywords) > 0
        assert "python" in job.extracted_keywords
        assert "fastapi" in job.extracted_keywords

    async def test_get_job_posting_success(self, db_session, test_user, sample_job_posting):
        """Test getting a job posting by ID."""
        job = await JobService.get_job_posting(
            db_session,
            sample_job_posting["id"],
            test_user["id"]
        )
        
        assert job.id == sample_job_posting["id"]
        assert job.company_name == sample_job_posting["company_name"]

    async def test_get_job_posting_not_found(self, db_session, test_user):
        """Test getting non-existent job posting raises NotFoundError."""
        with pytest.raises(NotFoundError, match="Job posting not found"):
            await JobService.get_job_posting(db_session, uuid4(), test_user["id"])

    async def test_get_job_posting_wrong_user(self, db_session, sample_job_posting):
        """Test getting job from different user raises ForbiddenError."""
        wrong_user_id = uuid4()
        
        with pytest.raises(ForbiddenError, match="Access denied"):
            await JobService.get_job_posting(
                db_session,
                sample_job_posting["id"],
                wrong_user_id
            )

    async def test_update_job_posting(self, db_session, test_user, sample_job_posting):
        """Test updating a job posting."""
        update_data = JobPostingUpdate(
            company_name="UpdatedCorp",
            interest_level=5,
            notes="Updated notes"
        )
        
        job = await JobService.update_job_posting(
            db_session,
            sample_job_posting["id"],
            test_user["id"],
            update_data
        )
        
        assert job.company_name == "UpdatedCorp"
        assert job.interest_level == 5
        assert job.notes == "Updated notes"
        # Original fields should remain unchanged
        assert job.job_title == sample_job_posting["job_title"]

    async def test_update_job_description_updates_keywords(self, db_session, test_user, sample_job_posting):
        """Test that updating job description updates keywords."""
        update_data = JobPostingUpdate(
            job_description="New description with Kubernetes and GraphQL",
            requirements="Experience with TypeScript"
        )
        
        job = await JobService.update_job_posting(
            db_session,
            sample_job_posting["id"],
            test_user["id"],
            update_data
        )
        
        assert "kubernetes" in job.extracted_keywords
        assert "graphql" in job.extracted_keywords
        assert "typescript" in job.extracted_keywords

    async def test_update_job_status(self, db_session, test_user, sample_job_posting):
        """Test updating job status."""
        status_data = JobStatusUpdate(status=JobStatus.APPLIED)
        
        job = await JobService.update_job_status(
            db_session,
            sample_job_posting["id"],
            test_user["id"],
            status_data
        )
        
        assert job.status == JobStatus.APPLIED
        assert job.status_updated_at is not None

    async def test_delete_job_posting(self, db_session, test_user, sample_job_posting):
        """Test soft deleting a job posting."""
        await JobService.delete_job_posting(
            db_session,
            sample_job_posting["id"],
            test_user["id"]
        )
        
        # Verify job is soft deleted
        with pytest.raises(NotFoundError):
            await JobService.get_job_posting(
                db_session,
                sample_job_posting["id"],
                test_user["id"]
            )


@pytest.mark.asyncio
class TestJobServiceSearch:
    """Test job service search and filtering."""

    async def test_get_user_job_postings_all(self, db_session, test_user, multiple_job_postings):
        """Test getting all user's job postings."""
        search_params = JobSearchParams(page=1, page_size=10)
        
        jobs, total = await JobService.get_user_job_postings(
            db_session,
            test_user["id"],
            search_params
        )
        
        assert len(jobs) == 5
        assert total == 5

    async def test_get_user_job_postings_pagination(self, db_session, test_user, multiple_job_postings):
        """Test pagination of job postings."""
        search_params = JobSearchParams(page=1, page_size=2)
        
        jobs, total = await JobService.get_user_job_postings(
            db_session,
            test_user["id"],
            search_params
        )
        
        assert len(jobs) == 2
        assert total == 5

    async def test_get_user_job_postings_filter_by_company(self, db_session, test_user, multiple_job_postings):
        """Test filtering by company name."""
        search_params = JobSearchParams(company="TechCorp", page=1, page_size=10)
        
        jobs, total = await JobService.get_user_job_postings(
            db_session,
            test_user["id"],
            search_params
        )
        
        assert len(jobs) == 1
        assert total == 1
        assert jobs[0].company_name == "TechCorp"

    async def test_get_user_job_postings_filter_by_status(self, db_session, test_user, multiple_job_postings):
        """Test filtering by status."""
        search_params = JobSearchParams(status=JobStatus.SAVED, page=1, page_size=10)
        
        jobs, total = await JobService.get_user_job_postings(
            db_session,
            test_user["id"],
            search_params
        )
        
        assert len(jobs) == 2
        assert total == 2
        assert all(job.status == JobStatus.SAVED for job in jobs)

    async def test_get_user_job_postings_filter_by_interest(self, db_session, test_user, multiple_job_postings):
        """Test filtering by interest level."""
        search_params = JobSearchParams(interest_level=5, page=1, page_size=10)
        
        jobs, total = await JobService.get_user_job_postings(
            db_session,
            test_user["id"],
            search_params
        )
        
        assert len(jobs) == 1
        assert total == 1
        assert jobs[0].interest_level == 5

    async def test_get_user_job_postings_search_query(self, db_session, test_user, multiple_job_postings):
        """Test search by query."""
        search_params = JobSearchParams(query="Backend", page=1, page_size=10)
        
        jobs, total = await JobService.get_user_job_postings(
            db_session,
            test_user["id"],
            search_params
        )
        
        # Should find jobs with "Backend" in title or description
        assert total >= 2

    async def test_get_user_job_postings_sort_by_interest(self, db_session, test_user, multiple_job_postings):
        """Test sorting by interest level."""
        search_params = JobSearchParams(
            sort_by="interest_level",
            sort_order="desc",
            page=1,
            page_size=10
        )
        
        jobs, total = await JobService.get_user_job_postings(
            db_session,
            test_user["id"],
            search_params
        )
        
        # Jobs should be sorted by interest level descending
        assert jobs[0].interest_level == 5
        assert jobs[-1].interest_level == 1


@pytest.mark.asyncio
class TestJobServiceStats:
    """Test job service statistics."""

    async def test_get_job_stats_empty(self, db_session, test_user):
        """Test stats with no jobs."""
        stats = await JobService.get_job_stats(db_session, test_user["id"])
        
        assert stats.total_jobs == 0
        assert stats.by_status == {}
        assert stats.avg_interest_level is None
        assert stats.total_with_applications == 0
        assert stats.recent_jobs_count == 0

    async def test_get_job_stats_with_data(self, db_session, test_user, multiple_job_postings):
        """Test stats with multiple jobs."""
        stats = await JobService.get_job_stats(db_session, test_user["id"])
        
        assert stats.total_jobs == 5
        assert len(stats.by_status) > 0
        assert stats.by_status.get("saved") == 2
        assert stats.avg_interest_level == 3.0  # (5+4+3+2+1)/5
        assert stats.recent_jobs_count == 5  # All created recently
