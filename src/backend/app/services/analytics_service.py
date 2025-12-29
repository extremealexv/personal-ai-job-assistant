"""Analytics service for dashboard and metrics."""
from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application, ApplicationStatus
from app.models.cover_letter import CoverLetter
from app.models.job import JobPosting, JobStatus
from app.models.resume import ResumeVersion
from app.schemas.analytics import (
    DashboardSummary,
    FunnelAnalysis,
    FunnelStage,
    PerformanceMetrics,
    TimelineData,
    TimelineDataPoint,
    TimelineParams,
)


class AnalyticsService:
    """Service for analytics and metrics."""

    @staticmethod
    async def get_dashboard_summary(
        db: AsyncSession,
        user_id: UUID,
    ) -> DashboardSummary:
        """
        Get overall dashboard summary statistics.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            DashboardSummary with all metrics
        """
        # Job statistics
        job_stats_stmt = select(
            func.count(JobPosting.id).label("total"),
            JobPosting.status,
            func.avg(JobPosting.interest_level).label("avg_interest"),
        ).where(
            and_(
                JobPosting.user_id == user_id,
                JobPosting.deleted_at.is_(None),
            )
        ).group_by(JobPosting.status)
        
        job_result = await db.execute(job_stats_stmt)
        job_rows = job_result.all()
        
        total_jobs = 0
        jobs_by_status = {}
        avg_interest = 0.0
        
        for row in job_rows:
            count = row.total
            status = row.status
            total_jobs += count
            jobs_by_status[status] = count
        
        # Get average interest level across all jobs
        avg_interest_stmt = select(
            func.avg(JobPosting.interest_level)
        ).where(
            and_(
                JobPosting.user_id == user_id,
                JobPosting.deleted_at.is_(None),
            )
        )
        avg_interest_result = await db.execute(avg_interest_stmt)
        avg_interest_value = avg_interest_result.scalar()
        avg_interest = float(avg_interest_value) if avg_interest_value else 0.0
        
        # Application statistics
        app_stats_stmt = select(
            func.count(Application.id).label("total"),
            Application.status,
        ).where(
            Application.user_id == user_id
        ).group_by(Application.status)
        
        app_result = await db.execute(app_stats_stmt)
        app_rows = app_result.all()
        
        total_applications = 0
        applications_by_status = {}
        
        for row in app_rows:
            count = row.total
            status = row.status
            total_applications += count
            applications_by_status[status] = count
        
        # Calculate rates
        submitted_count = applications_by_status.get(ApplicationStatus.SUBMITTED, 0) + \
                         applications_by_status.get(ApplicationStatus.VIEWED, 0) + \
                         applications_by_status.get(ApplicationStatus.PHONE_SCREEN, 0) + \
                         applications_by_status.get(ApplicationStatus.TECHNICAL, 0) + \
                         applications_by_status.get(ApplicationStatus.ONSITE, 0) + \
                         applications_by_status.get(ApplicationStatus.OFFER, 0) + \
                         applications_by_status.get(ApplicationStatus.ACCEPTED, 0) + \
                         applications_by_status.get(ApplicationStatus.REJECTED, 0)
        
        response_count = applications_by_status.get(ApplicationStatus.VIEWED, 0) + \
                        applications_by_status.get(ApplicationStatus.PHONE_SCREEN, 0) + \
                        applications_by_status.get(ApplicationStatus.TECHNICAL, 0) + \
                        applications_by_status.get(ApplicationStatus.ONSITE, 0) + \
                        applications_by_status.get(ApplicationStatus.OFFER, 0) + \
                        applications_by_status.get(ApplicationStatus.ACCEPTED, 0)
        
        interview_count = applications_by_status.get(ApplicationStatus.PHONE_SCREEN, 0) + \
                         applications_by_status.get(ApplicationStatus.TECHNICAL, 0) + \
                         applications_by_status.get(ApplicationStatus.ONSITE, 0) + \
                         applications_by_status.get(ApplicationStatus.OFFER, 0) + \
                         applications_by_status.get(ApplicationStatus.ACCEPTED, 0)
        
        offer_count = applications_by_status.get(ApplicationStatus.OFFER, 0) + \
                     applications_by_status.get(ApplicationStatus.ACCEPTED, 0)
        
        response_rate = (response_count / submitted_count * 100) if submitted_count > 0 else 0.0
        interview_rate = (interview_count / submitted_count * 100) if submitted_count > 0 else 0.0
        offer_rate = (offer_count / submitted_count * 100) if submitted_count > 0 else 0.0
        
        # Cover letter statistics
        cl_stats_stmt = select(
            func.count(CoverLetter.id).label("total"),
            func.count(CoverLetter.id).filter(CoverLetter.is_active).label("active"),
        ).join(
            Application, CoverLetter.application_id == Application.id
        ).where(
            Application.user_id == user_id
        )
        
        cl_result = await db.execute(cl_stats_stmt)
        cl_row = cl_result.first()
        
        total_cover_letters = cl_row.total if cl_row else 0
        active_cover_letters = cl_row.active if cl_row else 0
        
        # Average versions per application
        avg_versions_stmt = select(
            func.avg(func.count(CoverLetter.id)).over()
        ).join(
            Application, CoverLetter.application_id == Application.id
        ).where(
            Application.user_id == user_id
        ).group_by(CoverLetter.application_id)
        
        avg_versions_result = await db.execute(avg_versions_stmt)
        avg_versions_value = avg_versions_result.scalar()
        avg_versions = float(avg_versions_value) if avg_versions_value else 0.0
        
        # Time-based metrics
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)
        
        apps_7_days_stmt = select(
            func.count(Application.id)
        ).where(
            and_(
                Application.user_id == user_id,
                Application.submitted_at >= seven_days_ago,
            )
        )
        apps_7_days_result = await db.execute(apps_7_days_stmt)
        applications_last_7_days = apps_7_days_result.scalar() or 0
        
        apps_30_days_stmt = select(
            func.count(Application.id)
        ).where(
            and_(
                Application.user_id == user_id,
                Application.submitted_at >= thirty_days_ago,
            )
        )
        apps_30_days_result = await db.execute(apps_30_days_stmt)
        applications_last_30_days = apps_30_days_result.scalar() or 0
        
        return DashboardSummary(
            total_jobs=total_jobs,
            jobs_by_status=jobs_by_status,
            avg_interest_level=avg_interest,
            total_applications=total_applications,
            applications_by_status=applications_by_status,
            response_rate=response_rate,
            interview_rate=interview_rate,
            offer_rate=offer_rate,
            total_cover_letters=total_cover_letters,
            active_cover_letters=active_cover_letters,
            avg_versions_per_application=avg_versions,
            applications_last_7_days=applications_last_7_days,
            applications_last_30_days=applications_last_30_days,
            avg_response_time_days=None,  # Could calculate if we track response dates
        )

    @staticmethod
    async def get_timeline_data(
        db: AsyncSession,
        user_id: UUID,
        params: TimelineParams,
    ) -> TimelineData:
        """
        Get timeline data for applications over time.
        
        Args:
            db: Database session
            user_id: User ID
            params: Timeline parameters
            
        Returns:
            TimelineData with data points
        """
        # Set default date range if not provided
        end_date = params.end_date or date.today()
        if params.start_date:
            start_date = params.start_date
        else:
            # Default to 3 months ago
            start_date = end_date - timedelta(days=90)
        
        # Query applications in date range
        stmt = select(
            func.date(Application.submitted_at).label("date"),
            func.count(Application.id).label("count"),
        ).where(
            and_(
                Application.user_id == user_id,
                Application.submitted_at.is_not(None),
                func.date(Application.submitted_at) >= start_date,
                func.date(Application.submitted_at) <= end_date,
            )
        ).group_by(
            func.date(Application.submitted_at)
        ).order_by(
            func.date(Application.submitted_at)
        )
        
        result = await db.execute(stmt)
        rows = result.all()
        
        # Create data points with cumulative counts
        data_points = []
        cumulative = 0
        
        for row in rows:
            cumulative += row.count
            data_points.append(
                TimelineDataPoint(
                    date=row.date,
                    count=row.count,
                    cumulative=cumulative,
                )
            )
        
        return TimelineData(
            metric=params.metric,
            granularity=params.granularity,
            data_points=data_points,
            total=cumulative,
            start_date=start_date,
            end_date=end_date,
        )

    @staticmethod
    async def get_performance_metrics(
        db: AsyncSession,
        user_id: UUID,
    ) -> PerformanceMetrics:
        """
        Get performance metrics and success rates.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            PerformanceMetrics with all metrics
        """
        # Overall counts
        total_apps_stmt = select(
            func.count(Application.id)
        ).where(
            and_(
                Application.user_id == user_id,
                Application.submitted_at.is_not(None),
            )
        )
        total_apps_result = await db.execute(total_apps_stmt)
        total_applications = total_apps_result.scalar() or 0
        
        # Count by status
        response_count = await AnalyticsService._count_apps_by_status_list(
            db, user_id, [
                ApplicationStatus.VIEWED,
                ApplicationStatus.PHONE_SCREEN,
                ApplicationStatus.TECHNICAL,
                ApplicationStatus.ONSITE,
                ApplicationStatus.OFFER,
                ApplicationStatus.ACCEPTED,
            ]
        )
        
        interview_count = await AnalyticsService._count_apps_by_status_list(
            db, user_id, [
                ApplicationStatus.PHONE_SCREEN,
                ApplicationStatus.TECHNICAL,
                ApplicationStatus.ONSITE,
                ApplicationStatus.OFFER,
                ApplicationStatus.ACCEPTED,
            ]
        )
        
        offer_count = await AnalyticsService._count_apps_by_status_list(
            db, user_id, [
                ApplicationStatus.OFFER,
                ApplicationStatus.ACCEPTED,
            ]
        )
        
        # Calculate rates
        response_rate = (response_count / total_applications * 100) if total_applications > 0 else 0.0
        interview_rate = (interview_count / total_applications * 100) if total_applications > 0 else 0.0
        offer_rate = (offer_count / total_applications * 100) if total_applications > 0 else 0.0
        
        # Top companies
        top_companies_stmt = select(
            JobPosting.company_name,
            func.count(Application.id).label("count"),
        ).join(
            Application, JobPosting.id == Application.job_posting_id
        ).where(
            Application.user_id == user_id
        ).group_by(
            JobPosting.company_name
        ).order_by(
            func.count(Application.id).desc()
        ).limit(10)
        
        top_companies_result = await db.execute(top_companies_stmt)
        top_companies = [
            {"company": row.company_name, "applications": row.count}
            for row in top_companies_result.all()
        ]
        
        # Resume version performance
        resume_perf_stmt = select(
            ResumeVersion.version_name,
            func.count(Application.id).label("count"),
        ).join(
            Application, ResumeVersion.id == Application.resume_version_id
        ).where(
            Application.user_id == user_id
        ).group_by(
            ResumeVersion.version_name
        ).order_by(
            func.count(Application.id).desc()
        ).limit(5)
        
        resume_perf_result = await db.execute(resume_perf_stmt)
        resume_performance = [
            {"version": row.version_name, "applications": row.count}
            for row in resume_perf_result.all()
        ]
        
        return PerformanceMetrics(
            total_applications=total_applications,
            total_responses=response_count,
            total_interviews=interview_count,
            total_offers=offer_count,
            response_rate=response_rate,
            interview_rate=interview_rate,
            offer_rate=offer_rate,
            avg_response_time_days=None,
            avg_time_to_interview_days=None,
            avg_time_to_offer_days=None,
            top_companies=top_companies,
            resume_version_performance=resume_performance,
        )

    @staticmethod
    async def get_funnel_analysis(
        db: AsyncSession,
        user_id: UUID,
    ) -> FunnelAnalysis:
        """
        Get conversion funnel analysis.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            FunnelAnalysis with stage data
        """
        # Count jobs by status
        total_jobs_stmt = select(
            func.count(JobPosting.id)
        ).where(
            and_(
                JobPosting.user_id == user_id,
                JobPosting.deleted_at.is_(None),
            )
        )
        total_jobs_result = await db.execute(total_jobs_stmt)
        total_jobs = total_jobs_result.scalar() or 0
        
        # Count jobs that were applied to
        applied_stmt = select(
            func.count(func.distinct(JobPosting.id))
        ).join(
            Application, JobPosting.id == Application.job_posting_id
        ).where(
            and_(
                JobPosting.user_id == user_id,
                Application.submitted_at.is_not(None),
            )
        )
        applied_result = await db.execute(applied_stmt)
        applied_count = applied_result.scalar() or 0
        
        # Count applications that got responses
        responded_count = await AnalyticsService._count_apps_by_status_list(
            db, user_id, [
                ApplicationStatus.VIEWED,
                ApplicationStatus.PHONE_SCREEN,
                ApplicationStatus.TECHNICAL,
                ApplicationStatus.ONSITE,
                ApplicationStatus.OFFER,
                ApplicationStatus.ACCEPTED,
            ]
        )
        
        # Count applications that got interviews
        interviewed_count = await AnalyticsService._count_apps_by_status_list(
            db, user_id, [
                ApplicationStatus.PHONE_SCREEN,
                ApplicationStatus.TECHNICAL,
                ApplicationStatus.ONSITE,
                ApplicationStatus.OFFER,
                ApplicationStatus.ACCEPTED,
            ]
        )
        
        # Count applications that got offers
        offered_count = await AnalyticsService._count_apps_by_status_list(
            db, user_id, [
                ApplicationStatus.OFFER,
                ApplicationStatus.ACCEPTED,
            ]
        )
        
        # Build funnel stages
        stages = []
        
        # Stage 1: Saved
        stages.append(FunnelStage(
            stage="Saved",
            count=total_jobs,
            percentage=100.0,
            conversion_from_previous=None,
        ))
        
        # Stage 2: Applied
        applied_pct = (applied_count / total_jobs * 100) if total_jobs > 0 else 0.0
        stages.append(FunnelStage(
            stage="Applied",
            count=applied_count,
            percentage=applied_pct,
            conversion_from_previous=applied_pct,
        ))
        
        # Stage 3: Responded
        responded_pct = (responded_count / total_jobs * 100) if total_jobs > 0 else 0.0
        responded_conv = (responded_count / applied_count * 100) if applied_count > 0 else 0.0
        stages.append(FunnelStage(
            stage="Responded",
            count=responded_count,
            percentage=responded_pct,
            conversion_from_previous=responded_conv,
        ))
        
        # Stage 4: Interviewed
        interviewed_pct = (interviewed_count / total_jobs * 100) if total_jobs > 0 else 0.0
        interviewed_conv = (interviewed_count / responded_count * 100) if responded_count > 0 else 0.0
        stages.append(FunnelStage(
            stage="Interviewed",
            count=interviewed_count,
            percentage=interviewed_pct,
            conversion_from_previous=interviewed_conv,
        ))
        
        # Stage 5: Offered
        offered_pct = (offered_count / total_jobs * 100) if total_jobs > 0 else 0.0
        offered_conv = (offered_count / interviewed_count * 100) if interviewed_count > 0 else 0.0
        stages.append(FunnelStage(
            stage="Offered",
            count=offered_count,
            percentage=offered_pct,
            conversion_from_previous=offered_conv,
        ))
        
        final_conversion = offered_pct
        
        return FunnelAnalysis(
            stages=stages,
            total_jobs=total_jobs,
            final_conversion_rate=final_conversion,
            avg_time_saved_to_applied=None,
            avg_time_applied_to_interview=None,
            avg_time_interview_to_offer=None,
        )

    @staticmethod
    async def _count_apps_by_status_list(
        db: AsyncSession,
        user_id: UUID,
        statuses: list[ApplicationStatus],
    ) -> int:
        """Helper to count applications by list of statuses."""
        stmt = select(
            func.count(Application.id)
        ).where(
            and_(
                Application.user_id == user_id,
                Application.status.in_(statuses),
            )
        )
        result = await db.execute(stmt)
        return result.scalar() or 0
