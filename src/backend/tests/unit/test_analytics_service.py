"""Unit tests for analytics service."""
import pytest
from datetime import date, datetime, timedelta
from uuid import uuid4

from app.models.application import Application, ApplicationStatus
from app.models.cover_letter import CoverLetter
from app.models.job import JobPosting, JobStatus
from app.schemas.analytics import TimelineParams
from app.services.analytics_service import AnalyticsService


@pytest.mark.asyncio
class TestAnalyticsService:
    """Test analytics service functionality."""

    async def test_get_dashboard_summary_empty(
        self, db_session, test_user
    ):
        """Test dashboard with no data."""
        summary = await AnalyticsService.get_dashboard_summary(db_session, test_user.id)
        
        assert summary.total_jobs == 0
        assert summary.total_applications == 0
        assert summary.total_cover_letters == 0

    async def test_get_dashboard_summary_with_data(
        self, db_session, test_user, sample_job_posting, sample_application, sample_cover_letter
    ):
        """Test dashboard with actual data."""
        summary = await AnalyticsService.get_dashboard_summary(db_session, test_user.id)
        
        assert summary.total_jobs >= 1
        assert summary.total_applications >= 1
        assert summary.total_cover_letters >= 1
        assert summary.avg_interest_level > 0

    async def test_dashboard_job_statistics(
        self, db_session, test_user
    ):
        """Test job statistics in dashboard."""
        # Create jobs with different statuses
        job1 = JobPosting(
            user_id=test_user.id,
            company_name="Company 1",
            job_title="Job 1",
            job_url="https://example.com/1",
            status=JobStatus.SAVED,
            interest_level=5,
        )
        job2 = JobPosting(
            user_id=test_user.id,
            company_name="Company 2",
            job_title="Job 2",
            job_url="https://example.com/2",
            status=JobStatus.APPLIED,
            interest_level=4,
        )
        db_session.add_all([job1, job2])
        await db_session.commit()
        
        summary = await AnalyticsService.get_dashboard_summary(db_session, test_user.id)
        
        assert summary.total_jobs == 2
        assert JobStatus.SAVED in summary.jobs_by_status
        assert JobStatus.APPLIED in summary.jobs_by_status
        assert summary.avg_interest_level == 4.5

    async def test_dashboard_application_rates(
        self, db_session, test_user, sample_job_posting, sample_resume_version
    ):
        """Test application success rate calculations."""
        # Create applications with different statuses
        app1 = Application(
            user_id=test_user.id,
            job_posting_id=sample_job_posting.id,
            resume_version_id=sample_resume_version.id,
            status=ApplicationStatus.SUBMITTED,
            submitted_at=datetime.utcnow(),
        )
        app2 = Application(
            user_id=test_user.id,
            job_posting_id=sample_job_posting.id,
            resume_version_id=sample_resume_version.id,
            status=ApplicationStatus.PHONE_SCREEN,
            submitted_at=datetime.utcnow(),
        )
        app3 = Application(
            user_id=test_user.id,
            job_posting_id=sample_job_posting.id,
            resume_version_id=sample_resume_version.id,
            status=ApplicationStatus.OFFER,
            submitted_at=datetime.utcnow(),
        )
        db_session.add_all([app1, app2, app3])
        await db_session.commit()
        
        summary = await AnalyticsService.get_dashboard_summary(db_session, test_user.id)
        
        assert summary.total_applications == 3
        # Response rate: 2/3 (phone_screen and offer responded)
        assert summary.response_rate > 0
        # Interview rate: 2/3 (phone_screen and offer)
        assert summary.interview_rate > 0
        # Offer rate: 1/3
        assert summary.offer_rate > 0

    async def test_dashboard_time_based_metrics(
        self, db_session, test_user, sample_job_posting, sample_resume_version
    ):
        """Test time-based application metrics."""
        # Create application in last 7 days
        recent_app = Application(
            user_id=test_user.id,
            job_posting_id=sample_job_posting.id,
            resume_version_id=sample_resume_version.id,
            status=ApplicationStatus.SUBMITTED,
            submitted_at=datetime.utcnow() - timedelta(days=3),
        )
        # Create application in last 30 days
        older_app = Application(
            user_id=test_user.id,
            job_posting_id=sample_job_posting.id,
            resume_version_id=sample_resume_version.id,
            status=ApplicationStatus.SUBMITTED,
            submitted_at=datetime.utcnow() - timedelta(days=20),
        )
        db_session.add_all([recent_app, older_app])
        await db_session.commit()
        
        summary = await AnalyticsService.get_dashboard_summary(db_session, test_user.id)
        
        assert summary.applications_last_7_days >= 1
        assert summary.applications_last_30_days >= 2

    async def test_get_timeline_data_default_range(
        self, db_session, test_user, sample_job_posting, sample_resume_version
    ):
        """Test timeline data with default date range."""
        # Create applications at different dates
        for days_ago in [5, 10, 15]:
            app = Application(
                user_id=test_user.id,
                job_posting_id=sample_job_posting.id,
                resume_version_id=sample_resume_version.id,
                status=ApplicationStatus.SUBMITTED,
                submitted_at=datetime.utcnow() - timedelta(days=days_ago),
            )
            db_session.add(app)
        await db_session.commit()
        
        params = TimelineParams(
            metric="applications",
            granularity="day",
        )
        
        timeline = await AnalyticsService.get_timeline_data(db_session, test_user.id, params)
        
        assert timeline.total >= 3
        assert len(timeline.data_points) >= 3
        assert timeline.metric == "applications"
        assert timeline.granularity == "day"

    async def test_get_timeline_data_custom_range(
        self, db_session, test_user, sample_job_posting, sample_resume_version
    ):
        """Test timeline with custom date range."""
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        params = TimelineParams(
            start_date=start_date,
            end_date=end_date,
            metric="applications",
            granularity="week",
        )
        
        timeline = await AnalyticsService.get_timeline_data(db_session, test_user.id, params)
        
        assert timeline.start_date == start_date
        assert timeline.end_date == end_date

    async def test_timeline_cumulative_counts(
        self, db_session, test_user, sample_job_posting, sample_resume_version
    ):
        """Test cumulative counts in timeline."""
        # Create applications on same day
        for i in range(3):
            app = Application(
                user_id=test_user.id,
                job_posting_id=sample_job_posting.id,
                resume_version_id=sample_resume_version.id,
                status=ApplicationStatus.SUBMITTED,
                submitted_at=datetime.utcnow() - timedelta(days=1),
            )
            db_session.add(app)
        await db_session.commit()
        
        params = TimelineParams(
            metric="applications",
            granularity="day",
        )
        
        timeline = await AnalyticsService.get_timeline_data(db_session, test_user.id, params)
        
        # Cumulative should increase with each data point
        if len(timeline.data_points) > 1:
            for i in range(len(timeline.data_points) - 1):
                assert timeline.data_points[i + 1].cumulative >= timeline.data_points[i].cumulative

    async def test_get_performance_metrics_empty(
        self, db_session, test_user
    ):
        """Test performance metrics with no applications."""
        metrics = await AnalyticsService.get_performance_metrics(db_session, test_user.id)
        
        assert metrics.total_applications == 0
        assert metrics.response_rate == 0.0
        assert metrics.interview_rate == 0.0
        assert metrics.offer_rate == 0.0

    async def test_get_performance_metrics_with_data(
        self, db_session, test_user, sample_job_posting, sample_resume_version
    ):
        """Test performance metrics calculation."""
        # Create varied applications
        statuses = [
            ApplicationStatus.SUBMITTED,
            ApplicationStatus.SUBMITTED,
            ApplicationStatus.PHONE_SCREEN,
            ApplicationStatus.OFFER,
        ]
        
        for status in statuses:
            app = Application(
                user_id=test_user.id,
                job_posting_id=sample_job_posting.id,
                resume_version_id=sample_resume_version.id,
                status=status,
                submitted_at=datetime.utcnow(),
            )
            db_session.add(app)
        await db_session.commit()
        
        metrics = await AnalyticsService.get_performance_metrics(db_session, test_user.id)
        
        assert metrics.total_applications == 4
        assert metrics.total_responses >= 2
        assert metrics.total_interviews >= 2
        assert metrics.total_offers >= 1
        assert 0 <= metrics.response_rate <= 100
        assert 0 <= metrics.interview_rate <= 100
        assert 0 <= metrics.offer_rate <= 100

    async def test_performance_top_companies(
        self, db_session, test_user, sample_resume_version
    ):
        """Test top companies by application count."""
        # Create jobs and applications for different companies
        companies = ["Company A", "Company A", "Company B"]
        
        for company in companies:
            job = JobPosting(
                user_id=test_user.id,
                company_name=company,
                job_title="Engineer",
                job_url=f"https://example.com/{company}",
            )
            db_session.add(job)
            await db_session.flush()
            
            app = Application(
                user_id=test_user.id,
                job_posting_id=job.id,
                resume_version_id=sample_resume_version.id,
                status=ApplicationStatus.SUBMITTED,
                submitted_at=datetime.utcnow(),
            )
            db_session.add(app)
        await db_session.commit()
        
        metrics = await AnalyticsService.get_performance_metrics(db_session, test_user.id)
        
        assert len(metrics.top_companies) >= 2
        # Company A should have most applications
        assert metrics.top_companies[0]["company"] == "Company A"
        assert metrics.top_companies[0]["applications"] == 2

    async def test_get_funnel_analysis_empty(
        self, db_session, test_user
    ):
        """Test funnel with no data."""
        funnel = await AnalyticsService.get_funnel_analysis(db_session, test_user.id)
        
        assert funnel.total_jobs == 0
        assert len(funnel.stages) == 5
        assert all(stage.count == 0 for stage in funnel.stages)

    async def test_get_funnel_analysis_with_data(
        self, db_session, test_user, sample_resume_version
    ):
        """Test funnel conversion tracking."""
        # Create 10 saved jobs
        jobs = []
        for i in range(10):
            job = JobPosting(
                user_id=test_user.id,
                company_name=f"Company {i}",
                job_title="Engineer",
                job_url=f"https://example.com/{i}",
                status=JobStatus.SAVED,
            )
            db_session.add(job)
            jobs.append(job)
        await db_session.flush()
        
        # Apply to 5 jobs
        for i in range(5):
            app = Application(
                user_id=test_user.id,
                job_posting_id=jobs[i].id,
                resume_version_id=sample_resume_version.id,
                status=ApplicationStatus.SUBMITTED,
                submitted_at=datetime.utcnow(),
            )
            db_session.add(app)
        await db_session.flush()
        
        # Get response on 2 applications
        stmt = db_session.query(Application).limit(2)
        apps = await stmt.all()
        for app in apps[:2]:
            app.status = ApplicationStatus.PHONE_SCREEN
        
        await db_session.commit()
        
        funnel = await AnalyticsService.get_funnel_analysis(db_session, test_user.id)
        
        assert funnel.total_jobs == 10
        assert funnel.stages[0].stage == "Saved"
        assert funnel.stages[0].count == 10
        assert funnel.stages[1].stage == "Applied"
        assert funnel.stages[1].count == 5
        # Response stage should have at least 2
        assert funnel.stages[2].count >= 2

    async def test_funnel_conversion_rates(
        self, db_session, test_user, sample_job_posting, sample_resume_version
    ):
        """Test funnel stage conversion rate calculations."""
        # Create application that progressed through funnel
        app = Application(
            user_id=test_user.id,
            job_posting_id=sample_job_posting.id,
            resume_version_id=sample_resume_version.id,
            status=ApplicationStatus.OFFER,
            submitted_at=datetime.utcnow(),
        )
        db_session.add(app)
        await db_session.commit()
        
        funnel = await AnalyticsService.get_funnel_analysis(db_session, test_user.id)
        
        # Check conversion rates are percentages
        for stage in funnel.stages:
            assert 0 <= stage.percentage <= 100
            if stage.conversion_from_previous is not None:
                assert 0 <= stage.conversion_from_previous <= 100

    async def test_analytics_user_isolation(
        self, db_session, test_user, other_user, sample_resume_version
    ):
        """Test analytics only show user's own data."""
        # Create job and application for other user
        other_job = JobPosting(
            user_id=other_user.id,
            company_name="Other Company",
            job_title="Other Job",
            job_url="https://example.com/other",
        )
        db_session.add(other_job)
        await db_session.flush()
        
        other_app = Application(
            user_id=other_user.id,
            job_posting_id=other_job.id,
            resume_version_id=sample_resume_version.id,
            status=ApplicationStatus.SUBMITTED,
            submitted_at=datetime.utcnow(),
        )
        db_session.add(other_app)
        await db_session.commit()
        
        # Get analytics for test_user
        summary = await AnalyticsService.get_dashboard_summary(db_session, test_user.id)
        
        # Should not include other user's data
        assert summary.total_jobs == 0
        assert summary.total_applications == 0
