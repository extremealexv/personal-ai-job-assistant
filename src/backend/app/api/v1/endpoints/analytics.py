"""Analytics API endpoints."""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.analytics import (
    DashboardSummary,
    FunnelAnalysis,
    PerformanceMetrics,
    TimelineData,
    TimelineParams,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardSummary:
    """
    Get overall dashboard summary with all key metrics.
    
    Includes:
    - Job statistics (total, by status, average interest)
    - Application statistics (total, by status, rates)
    - Cover letter statistics (total, active, versions)
    - Recent activity (last 7/30 days)
    
    Returns comprehensive dashboard data.
    """
    return await AnalyticsService.get_dashboard_summary(db, current_user.id)


@router.get("/timeline", response_model=TimelineData)
async def get_timeline(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    granularity: str = Query("week", description="day, week, or month"),
    metric: str = Query("applications", description="Metric to track"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TimelineData:
    """
    Get timeline data showing applications over time.
    
    - **start_date**: Start of timeline (default: 90 days ago)
    - **end_date**: End of timeline (default: today)
    - **granularity**: Time bucket size - day, week, month (default: week)
    - **metric**: What to track - applications, responses, interviews, offers (default: applications)
    
    Returns data points with counts and cumulative totals.
    """
    params = TimelineParams(
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        metric=metric,
    )
    
    return await AnalyticsService.get_timeline_data(db, current_user.id, params)


@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PerformanceMetrics:
    """
    Get detailed performance metrics and success rates.
    
    Includes:
    - Overall counts (applications, responses, interviews, offers)
    - Success rates (response rate, interview rate, offer rate)
    - Time metrics (average days to response/interview/offer)
    - Top companies by application count
    - Resume version performance comparison
    
    Returns comprehensive performance analytics.
    """
    return await AnalyticsService.get_performance_metrics(db, current_user.id)


@router.get("/funnel", response_model=FunnelAnalysis)
async def get_funnel(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FunnelAnalysis:
    """
    Get conversion funnel analysis from saved jobs to offers.
    
    Tracks progression through stages:
    1. Saved (jobs bookmarked)
    2. Applied (applications submitted)
    3. Responded (got response from company)
    4. Interviewed (phone/technical/onsite)
    5. Offered (received job offer)
    
    Shows conversion rates between stages and overall success rate.
    """
    return await AnalyticsService.get_funnel_analysis(db, current_user.id)
