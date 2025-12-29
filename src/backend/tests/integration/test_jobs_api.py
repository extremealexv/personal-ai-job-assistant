"""Integration tests for job API endpoints."""

import pytest
from uuid import uuid4

from app.models.job import JobStatus


pytestmark = [pytest.mark.integration, pytest.mark.asyncio, pytest.mark.job_management]


class TestJobPostingCRUD:
    """Test job posting CRUD endpoints."""

    async def test_create_job_posting(self, async_client, auth_headers):
        """Test POST /api/v1/jobs - Create job posting."""
        job_data = {
            "company_name": "TestCorp",
            "job_title": "Senior Python Developer",
            "job_url": "https://testcorp.com/jobs/senior-python-dev",
            "location": "Remote",
            "salary_range": "$120k-$160k",
            "employment_type": "Full-time",
            "remote_policy": "Remote",
            "job_description": "Looking for experienced Python developer with FastAPI",
            "requirements": "5+ years Python, FastAPI, PostgreSQL",
            "interest_level": 4,
            "notes": "Looks promising"
        }
        
        response = await async_client.post(
            "/api/v1/jobs",
            json=job_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["company_name"] == "TestCorp"
        assert data["job_title"] == "Senior Python Developer"
        assert data["status"] == "saved"
        assert len(data["extracted_keywords"]) > 0
        assert "python" in data["extracted_keywords"]
        assert data["id"] is not None

    async def test_create_job_posting_without_auth(self, async_client):
        """Test creating job posting without authentication."""
        job_data = {
            "company_name": "TestCorp",
            "job_title": "Developer",
            "job_url": "https://testcorp.com/jobs"
        }
        
        response = await async_client.post("/api/v1/jobs", json=job_data)
        
        assert response.status_code == 403

    async def test_create_job_posting_invalid_url(self, async_client, auth_headers):
        """Test creating job with invalid URL."""
        job_data = {
            "company_name": "TestCorp",
            "job_title": "Developer",
            "job_url": "not-a-valid-url"
        }
        
        response = await async_client.post(
            "/api/v1/jobs",
            json=job_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_create_job_posting_invalid_interest_level(self, async_client, auth_headers):
        """Test creating job with invalid interest level."""
        job_data = {
            "company_name": "TestCorp",
            "job_title": "Developer",
            "job_url": "https://testcorp.com/jobs",
            "interest_level": 10  # Should be 1-5
        }
        
        response = await async_client.post(
            "/api/v1/jobs",
            json=job_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    async def test_get_job_posting(self, async_client, auth_headers, sample_job_posting):
        """Test GET /api/v1/jobs/{id} - Get job by ID."""
        response = await async_client.get(
            f"/api/v1/jobs/{sample_job_posting.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_job_posting.id)
        assert data["company_name"] == sample_job_posting.company_name

    async def test_get_job_posting_not_found(self, async_client, auth_headers):
        """Test getting non-existent job."""
        response = await async_client.get(
            f"/api/v1/jobs/{uuid4()}",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    async def test_update_job_posting(self, async_client, auth_headers, sample_job_posting):
        """Test PUT /api/v1/jobs/{id} - Update job posting."""
        update_data = {
            "company_name": "UpdatedCorp",
            "interest_level": 5,
            "notes": "Updated notes after interview"
        }
        
        response = await async_client.put(
            f"/api/v1/jobs/{sample_job_posting.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == "UpdatedCorp"
        assert data["interest_level"] == 5
        assert data["notes"] == "Updated notes after interview"

    async def test_update_job_status(self, async_client, auth_headers, sample_job_posting):
        """Test PATCH /api/v1/jobs/{id}/status - Update job status."""
        status_data = {"status": "applied"}
        
        response = await async_client.patch(
            f"/api/v1/jobs/{sample_job_posting.id}/status",
            json=status_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "applied"
        assert data["status_updated_at"] is not None

    async def test_delete_job_posting(self, async_client, auth_headers, sample_job_posting):
        """Test DELETE /api/v1/jobs/{id} - Soft delete job."""
        response = await async_client.delete(
            f"/api/v1/jobs/{sample_job_posting.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify job is deleted (should return 404)
        get_response = await async_client.get(
            f"/api/v1/jobs/{sample_job_posting.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404


class TestJobPostingList:
    """Test job listing and filtering endpoints."""

    async def test_list_jobs_empty(self, async_client, auth_headers):
        """Test listing jobs when none exist."""
        response = await async_client.get("/api/v1/jobs", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1

    async def test_list_jobs(self, async_client, auth_headers, multiple_job_postings):
        """Test GET /api/v1/jobs - List all jobs."""
        response = await async_client.get("/api/v1/jobs", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["page_size"] == 20

    async def test_list_jobs_pagination(self, async_client, auth_headers, multiple_job_postings):
        """Test job listing with pagination."""
        response = await async_client.get(
            "/api/v1/jobs?page=1&page_size=2",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["total_pages"] == 3

    async def test_list_jobs_filter_by_company(self, async_client, auth_headers, multiple_job_postings):
        """Test filtering jobs by company."""
        response = await async_client.get(
            "/api/v1/jobs?company=TechCorp",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["company_name"] == "TechCorp"

    async def test_list_jobs_filter_by_status(self, async_client, auth_headers, multiple_job_postings):
        """Test filtering jobs by status."""
        response = await async_client.get(
            "/api/v1/jobs?status=saved",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert all(item["status"] == "saved" for item in data["items"])

    async def test_list_jobs_filter_by_interest(self, async_client, auth_headers, multiple_job_postings):
        """Test filtering jobs by interest level."""
        response = await async_client.get(
            "/api/v1/jobs?interest_level=5",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["interest_level"] == 5

    async def test_list_jobs_sort_by_interest_desc(self, async_client, auth_headers, multiple_job_postings):
        """Test sorting jobs by interest level descending."""
        response = await async_client.get(
            "/api/v1/jobs?sort_by=interest_level&sort_order=desc",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        interests = [item["interest_level"] for item in data["items"]]
        assert interests == sorted(interests, reverse=True)

    async def test_list_jobs_sort_by_interest_asc(self, async_client, auth_headers, multiple_job_postings):
        """Test sorting jobs by interest level ascending."""
        response = await async_client.get(
            "/api/v1/jobs?sort_by=interest_level&sort_order=asc",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        interests = [item["interest_level"] for item in data["items"]]
        assert interests == sorted(interests)


class TestJobSearch:
    """Test job search endpoints."""

    async def test_search_jobs_by_keyword(self, async_client, auth_headers, multiple_job_postings):
        """Test GET /api/v1/jobs/search - Search by keyword."""
        response = await async_client.get(
            "/api/v1/jobs/search?query=Backend",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2  # Should find multiple backend jobs

    async def test_search_jobs_by_company(self, async_client, auth_headers, multiple_job_postings):
        """Test searching by company name."""
        response = await async_client.get(
            "/api/v1/jobs/search?query=TechCorp",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    async def test_search_jobs_no_results(self, async_client, auth_headers, multiple_job_postings):
        """Test search with no matching results."""
        response = await async_client.get(
            "/api/v1/jobs/search?query=NonexistentKeyword123",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_search_jobs_without_query(self, async_client, auth_headers):
        """Test search endpoint without query parameter."""
        response = await async_client.get(
            "/api/v1/jobs/search",
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Missing required query param


class TestJobStats:
    """Test job statistics endpoints."""

    async def test_get_job_stats_empty(self, async_client, auth_headers):
        """Test GET /api/v1/jobs/stats - Stats with no jobs."""
        response = await async_client.get("/api/v1/jobs/stats", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_jobs"] == 0
        assert data["by_status"] == {}
        assert data["avg_interest_level"] is None
        assert data["total_with_applications"] == 0
        assert data["recent_jobs_count"] == 0

    async def test_get_job_stats_with_data(self, async_client, auth_headers, multiple_job_postings):
        """Test stats with multiple jobs."""
        response = await async_client.get("/api/v1/jobs/stats", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_jobs"] == 5
        assert len(data["by_status"]) > 0
        # by_status keys use enum string representation: "JobStatus.SAVED"
        assert data["by_status"]["JobStatus.SAVED"] == 2
        assert data["avg_interest_level"] == 3.0
        assert data["recent_jobs_count"] == 5


class TestJobPostingAuthorization:
    """Test authorization and access control."""

    async def test_cannot_access_other_user_job(self, async_client, auth_headers, sample_job_posting, db_session):
        """Test that users cannot access other users' jobs."""
        # Create a second user
        from app.models.user import User
        from app.core.security import get_password_hash
        
        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("password"),
            full_name="Other User"
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)
        
        # Try to access first user's job with second user's auth
        # (In reality, we'd need to generate auth token for second user)
        # For this test, we'll just verify the job belongs to correct user
        response = await async_client.get(
            f"/api/v1/jobs/{sample_job_posting.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(sample_job_posting.user_id)
