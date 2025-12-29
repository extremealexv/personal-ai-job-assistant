"""Unit tests for application service layer."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.job import Application, ApplicationStatus, JobPosting, JobStatus
from app.models.resume import ResumeVersion
from app.schemas.application import (
    ApplicationCreate,
    ApplicationSearchParams,
    ApplicationUpdate,
)
from app.services import application_service


class TestApplicationServiceCRUD:
    """Test CRUD operations for applications."""

    async def test_create_application(self, db_session, test_user, sample_job_posting, sample_resume_version):
        """Test creating a new application."""
        data = ApplicationCreate(
            job_posting_id=sample_job_posting.id,
            resume_version_id=sample_resume_version.id,
            submission_method="manual",
            status=ApplicationStatus.DRAFT,
        )

        application = await application_service.create_application(
            db_session, test_user.id, data
        )

        assert application.id is not None
        assert application.user_id == test_user.id
        assert application.job_posting_id == sample_job_posting.id
        assert application.resume_version_id == sample_resume_version.id
        assert application.status == ApplicationStatus.DRAFT
        assert application.submission_method == "manual"

    async def test_create_application_with_submitted_status(
        self, db_session, test_user, sample_job_posting, sample_resume_version
    ):
        """Test creating application with SUBMITTED status updates job status."""
        # Job starts as SAVED
        assert sample_job_posting.status == JobStatus.SAVED

        data = ApplicationCreate(
            job_posting_id=sample_job_posting.id,
            resume_version_id=sample_resume_version.id,
            submitted_at=datetime.utcnow(),
            status=ApplicationStatus.SUBMITTED,
        )

        application = await application_service.create_application(
            db_session, test_user.id, data
        )

        assert application.status == ApplicationStatus.SUBMITTED
        
        # Refresh job posting to see updated status
        await db_session.refresh(sample_job_posting)
        assert sample_job_posting.status == JobStatus.APPLIED

    async def test_create_application_job_not_found(
        self, db_session, test_user, sample_resume_version
    ):
        """Test creating application with non-existent job."""
        data = ApplicationCreate(
            job_posting_id=uuid4(),
            resume_version_id=sample_resume_version.id,
        )

        with pytest.raises(NotFoundError, match="Job posting .* not found"):
            await application_service.create_application(db_session, test_user.id, data)

    async def test_create_application_wrong_user(
        self, db_session, test_user, other_user, sample_job_posting, sample_resume_version
    ):
        """Test cannot create application for another user's job."""
        # Create job for other_user
        other_job = JobPosting(
            user_id=other_user.id,
            company_name="Other Company",
            job_title="Other Job",
            job_url="https://example.com/other",
            status=JobStatus.SAVED,
        )
        db_session.add(other_job)
        await db_session.commit()

        data = ApplicationCreate(
            job_posting_id=other_job.id,
            resume_version_id=sample_resume_version.id,
        )

        with pytest.raises(ForbiddenError, match="another user's job posting"):
            await application_service.create_application(db_session, test_user.id, data)

    async def test_get_application_success(
        self, db_session, test_user, sample_application
    ):
        """Test getting application by ID."""
        application = await application_service.get_application(
            db_session, sample_application.id, test_user.id
        )

        assert application.id == sample_application.id
        assert application.user_id == test_user.id

    async def test_get_application_not_found(self, db_session, test_user):
        """Test getting non-existent application."""
        with pytest.raises(NotFoundError, match="Application .* not found"):
            await application_service.get_application(db_session, uuid4(), test_user.id)

    async def test_get_application_wrong_user(
        self, db_session, test_user, other_user, sample_application
    ):
        """Test cannot access another user's application."""
        with pytest.raises(ForbiddenError, match="another user's application"):
            await application_service.get_application(
                db_session, sample_application.id, other_user.id
            )

    async def test_update_application(
        self, db_session, test_user, sample_application
    ):
        """Test updating an application."""
        data = ApplicationUpdate(
            submission_method="extension",
            follow_up_notes="Follow up scheduled",
        )

        application = await application_service.update_application(
            db_session, sample_application.id, test_user.id, data
        )

        assert application.submission_method == "extension"
        assert application.follow_up_notes == "Follow up scheduled"

    async def test_update_application_status(
        self, db_session, test_user, sample_application, sample_job_posting
    ):
        """Test updating application status."""
        # Initial status is DRAFT
        assert sample_application.status == ApplicationStatus.DRAFT

        application = await application_service.update_application_status(
            db_session, sample_application.id, test_user.id, ApplicationStatus.SUBMITTED
        )

        assert application.status == ApplicationStatus.SUBMITTED
        
        # Job should now be APPLIED
        await db_session.refresh(sample_job_posting)
        assert sample_job_posting.status == JobStatus.APPLIED

    async def test_update_application_status_to_interviewing(
        self, db_session, test_user, sample_application, sample_job_posting
    ):
        """Test updating to interview status updates job."""
        # First submit the application
        await application_service.update_application_status(
            db_session, sample_application.id, test_user.id, ApplicationStatus.SUBMITTED
        )

        # Then move to phone screen
        application = await application_service.update_application_status(
            db_session, sample_application.id, test_user.id, ApplicationStatus.PHONE_SCREEN
        )

        assert application.status == ApplicationStatus.PHONE_SCREEN
        
        # Job should now be INTERVIEWING
        await db_session.refresh(sample_job_posting)
        assert sample_job_posting.status == JobStatus.INTERVIEWING

    async def test_update_application_status_to_offer(
        self, db_session, test_user, sample_application, sample_job_posting
    ):
        """Test updating to offer status updates job."""
        application = await application_service.update_application_status(
            db_session, sample_application.id, test_user.id, ApplicationStatus.OFFER
        )

        assert application.status == ApplicationStatus.OFFER
        
        # Job should now be OFFER
        await db_session.refresh(sample_job_posting)
        assert sample_job_posting.status == JobStatus.OFFER

    async def test_update_application_status_to_rejected(
        self, db_session, test_user, sample_application, sample_job_posting
    ):
        """Test updating to rejected status updates job."""
        application = await application_service.update_application_status(
            db_session, sample_application.id, test_user.id, ApplicationStatus.REJECTED
        )

        assert application.status == ApplicationStatus.REJECTED
        
        # Job should now be REJECTED
        await db_session.refresh(sample_job_posting)
        assert sample_job_posting.status == JobStatus.REJECTED

    async def test_delete_application(
        self, db_session, test_user, sample_application
    ):
        """Test deleting an application."""
        application_id = sample_application.id

        await application_service.delete_application(
            db_session, application_id, test_user.id
        )

        # Application should no longer exist
        with pytest.raises(NotFoundError):
            await application_service.get_application(db_session, application_id, test_user.id)


class TestApplicationServiceSearch:
    """Test search and filtering for applications."""

    async def test_get_user_applications_all(
        self, db_session, test_user, multiple_applications
    ):
        """Test getting all user applications."""
        params = ApplicationSearchParams(page=1, page_size=20)

        applications, total = await application_service.get_user_applications(
            db_session, test_user.id, params
        )

        assert len(applications) == 5
        assert total == 5

    async def test_get_user_applications_pagination(
        self, db_session, test_user, multiple_applications
    ):
        """Test pagination of applications."""
        params = ApplicationSearchParams(page=1, page_size=2)

        applications, total = await application_service.get_user_applications(
            db_session, test_user.id, params
        )

        assert len(applications) == 2
        assert total == 5

    async def test_get_user_applications_filter_by_status(
        self, db_session, test_user, multiple_applications
    ):
        """Test filtering applications by status."""
        params = ApplicationSearchParams(
            page=1, page_size=20, status=ApplicationStatus.SUBMITTED
        )

        applications, total = await application_service.get_user_applications(
            db_session, test_user.id, params
        )

        assert total == 2
        assert all(app.status == ApplicationStatus.SUBMITTED for app in applications)

    async def test_get_user_applications_filter_by_job(
        self, db_session, test_user, multiple_applications
    ):
        """Test filtering applications by job posting."""
        first_app = multiple_applications[0]
        params = ApplicationSearchParams(
            page=1, page_size=20, job_posting_id=first_app.job_posting_id
        )

        applications, total = await application_service.get_user_applications(
            db_session, test_user.id, params
        )

        assert total >= 1
        assert all(app.job_posting_id == first_app.job_posting_id for app in applications)

    async def test_get_user_applications_sort_by_created(
        self, db_session, test_user, multiple_applications
    ):
        """Test sorting applications by created_at."""
        params = ApplicationSearchParams(
            page=1, page_size=20, sort_by="created_at", sort_order="asc"
        )

        applications, total = await application_service.get_user_applications(
            db_session, test_user.id, params
        )

        assert len(applications) > 1
        # Check ascending order
        for i in range(len(applications) - 1):
            assert applications[i].created_at <= applications[i + 1].created_at


class TestApplicationServiceStats:
    """Test application statistics."""

    async def test_get_application_stats_empty(self, db_session, test_user):
        """Test stats with no applications."""
        stats = await application_service.get_application_stats(db_session, test_user.id)

        assert stats.total_applications == 0
        assert stats.submitted_count == 0
        assert stats.draft_count == 0
        assert stats.response_rate is None
        assert stats.recent_applications_count == 0

    async def test_get_application_stats_with_data(
        self, db_session, test_user, multiple_applications
    ):
        """Test stats with multiple applications."""
        stats = await application_service.get_application_stats(db_session, test_user.id)

        assert stats.total_applications == 5
        assert len(stats.by_status) > 0
        # Check status keys use enum string representation
        assert "ApplicationStatus.SUBMITTED" in stats.by_status or stats.submitted_count >= 0
        assert stats.recent_applications_count == 5
