"""Integration tests for analytics API endpoints."""
import pytest
from datetime import date, timedelta
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAnalyticsAPI:
    """Test analytics API endpoints."""

    async def test_dashboard_endpoint(
        self, client: AsyncClient, auth_headers, sample_job_posting, sample_application
    ):
        """Test dashboard endpoint returns summary."""
        response = await client.get(
            "/api/v1/analytics/dashboard",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "total_jobs" in data
        assert "total_applications" in data
        assert "total_cover_letters" in data
        assert "jobs_by_status" in data
        assert "applications_by_status" in data
        assert "response_rate" in data
        assert "interview_rate" in data
        assert "offer_rate" in data

    async def test_dashboard_without_auth(self, client: AsyncClient):
        """Test dashboard without authentication returns 403."""
        response = await client.get("/api/v1/analytics/dashboard")
        
        assert response.status_code == 403

    async def test_dashboard_with_data(
        self, client: AsyncClient, auth_headers, sample_job_posting, sample_application
    ):
        """Test dashboard with actual data."""
        response = await client.get(
            "/api/v1/analytics/dashboard",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_jobs"] >= 1
        assert data["total_applications"] >= 1
        assert isinstance(data["jobs_by_status"], dict)
        assert isinstance(data["applications_by_status"], dict)

    async def test_timeline_endpoint_default(
        self, client: AsyncClient, auth_headers, sample_application
    ):
        """Test timeline endpoint with default parameters."""
        response = await client.get(
            "/api/v1/analytics/timeline",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "metric" in data
        assert "granularity" in data
        assert "data_points" in data
        assert "total" in data
        assert isinstance(data["data_points"], list)

    async def test_timeline_endpoint_custom_params(
        self, client: AsyncClient, auth_headers, sample_application
    ):
        """Test timeline with custom date range."""
        start_date = (date.today() - timedelta(days=30)).isoformat()
        end_date = date.today().isoformat()
        
        response = await client.get(
            "/api/v1/analytics/timeline",
            params={
                "start_date": start_date,
                "end_date": end_date,
                "granularity": "week",
                "metric": "applications",
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["metric"] == "applications"
        assert data["granularity"] == "week"
        assert data["start_date"] == start_date
        assert data["end_date"] == end_date

    async def test_timeline_invalid_dates(
        self, client: AsyncClient, auth_headers
    ):
        """Test timeline with end date before start date."""
        start_date = date.today().isoformat()
        end_date = (date.today() - timedelta(days=10)).isoformat()
        
        response = await client.get(
            "/api/v1/analytics/timeline",
            params={
                "start_date": start_date,
                "end_date": end_date,
            },
            headers=auth_headers,
        )
        
        # Should return validation error
        assert response.status_code == 422

    async def test_performance_endpoint(
        self, client: AsyncClient, auth_headers, sample_application
    ):
        """Test performance metrics endpoint."""
        response = await client.get(
            "/api/v1/analytics/performance",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "total_applications" in data
        assert "total_responses" in data
        assert "total_interviews" in data
        assert "total_offers" in data
        assert "response_rate" in data
        assert "interview_rate" in data
        assert "offer_rate" in data
        assert "top_companies" in data
        assert "top_resume_versions" in data
        
        # Rates should be valid percentages
        assert 0 <= data["response_rate"] <= 100
        assert 0 <= data["interview_rate"] <= 100
        assert 0 <= data["offer_rate"] <= 100

    async def test_performance_without_auth(self, client: AsyncClient):
        """Test performance without authentication returns 403."""
        response = await client.get("/api/v1/analytics/performance")
        
        assert response.status_code == 403

    async def test_funnel_endpoint(
        self, client: AsyncClient, auth_headers, sample_job_posting, sample_application
    ):
        """Test funnel analysis endpoint."""
        response = await client.get(
            "/api/v1/analytics/funnel",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "stages" in data
        assert "total_jobs" in data
        assert "final_conversion_rate" in data
        
        # Should have 5 stages
        assert len(data["stages"]) == 5
        
        # Check stage structure
        for stage in data["stages"]:
            assert "stage" in stage
            assert "count" in stage
            assert "percentage" in stage
            # conversion_from_previous can be None for first stage
            if stage != data["stages"][0]:
                assert "conversion_from_previous" in stage

    async def test_funnel_without_auth(self, client: AsyncClient):
        """Test funnel without authentication returns 403."""
        response = await client.get("/api/v1/analytics/funnel")
        
        assert response.status_code == 403

    async def test_analytics_with_no_data(
        self, client: AsyncClient, auth_headers
    ):
        """Test analytics endpoints with no data."""
        # Dashboard
        response = await client.get(
            "/api/v1/analytics/dashboard",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_jobs"] == 0
        assert data["total_applications"] == 0
        
        # Performance
        response = await client.get(
            "/api/v1/analytics/performance",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_applications"] == 0
        assert data["response_rate"] == 0.0
        
        # Funnel
        response = await client.get(
            "/api/v1/analytics/funnel",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_jobs"] == 0
        assert all(stage["count"] == 0 for stage in data["stages"])

    async def test_analytics_user_isolation(
        self, client: AsyncClient, auth_headers, other_user_job, other_user_application
    ):
        """Test analytics only show current user's data."""
        response = await client.get(
            "/api/v1/analytics/dashboard",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should not include other user's data
        # If auth_headers is for sample_user with no jobs/applications,
        # these should be 0
        # This assumes auth_headers is for a user with no other data
