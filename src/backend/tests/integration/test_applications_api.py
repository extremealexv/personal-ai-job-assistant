"""Integration tests for application API endpoints."""

import pytest
from datetime import datetime
from uuid import uuid4

from app.models.job import ApplicationStatus, JobStatus


class TestApplicationCRUD:
    """Test CRUD operations for applications."""

    async def test_create_application(
        self, async_client, auth_headers, sample_job_posting, sample_resume_version
    ):
        """Test POST /api/v1/applications - Create application."""
        response = await async_client.post(
            "/api/v1/applications",
            headers=auth_headers,
            json={
                "job_posting_id": str(sample_job_posting.id),
                "resume_version_id": str(sample_resume_version.id),
                "submission_method": "manual",
                "status": "draft",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["job_posting_id"] == str(sample_job_posting.id)
        assert data["resume_version_id"] == str(sample_resume_version.id)
        assert data["status"] == "draft"
        assert data["submission_method"] == "manual"
        assert data["job_company_name"] == sample_job_posting.company_name
        assert data["job_title"] == sample_job_posting.job_title

    async def test_create_application_without_auth(
        self, async_client, sample_job_posting, sample_resume_version
    ):
        """Test creating application without authentication."""
        response = await async_client.post(
            "/api/v1/applications",
            json={
                "job_posting_id": str(sample_job_posting.id),
                "resume_version_id": str(sample_resume_version.id),
            },
        )

        assert response.status_code == 403

    async def test_create_application_invalid_status(
        self, async_client, auth_headers, sample_job_posting, sample_resume_version
    ):
        """Test creating application with invalid initial status."""
        response = await async_client.post(
            "/api/v1/applications",
            headers=auth_headers,
            json={
                "job_posting_id": str(sample_job_posting.id),
                "resume_version_id": str(sample_resume_version.id),
                "status": "offer",  # Invalid initial status
            },
        )

        assert response.status_code == 422

    async def test_create_application_job_not_found(
        self, async_client, auth_headers, sample_resume_version
    ):
        """Test creating application with non-existent job."""
        response = await async_client.post(
            "/api/v1/applications",
            headers=auth_headers,
            json={
                "job_posting_id": str(uuid4()),
                "resume_version_id": str(sample_resume_version.id),
            },
        )

        assert response.status_code == 404

    async def test_get_application(
        self, async_client, auth_headers, sample_application
    ):
        """Test GET /api/v1/applications/{id} - Get application by ID."""
        response = await async_client.get(
            f"/api/v1/applications/{sample_application.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_application.id)
        assert "job_company_name" in data
        assert "job_title" in data

    async def test_get_application_not_found(self, async_client, auth_headers):
        """Test getting non-existent application."""
        response = await async_client.get(
            f"/api/v1/applications/{uuid4()}", headers=auth_headers
        )

        assert response.status_code == 404

    async def test_update_application(
        self, async_client, auth_headers, sample_application
    ):
        """Test PUT /api/v1/applications/{id} - Update application."""
        response = await async_client.put(
            f"/api/v1/applications/{sample_application.id}",
            headers=auth_headers,
            json={
                "submission_method": "extension",
                "follow_up_notes": "Need to follow up next week",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["submission_method"] == "extension"
        assert data["follow_up_notes"] == "Need to follow up next week"

    async def test_update_application_status(
        self, async_client, auth_headers, sample_application
    ):
        """Test PATCH /api/v1/applications/{id}/status - Update status."""
        response = await async_client.patch(
            f"/api/v1/applications/{sample_application.id}/status",
            headers=auth_headers,
            json={"status": "submitted"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "submitted"

    async def test_delete_application(
        self, async_client, auth_headers, sample_application
    ):
        """Test DELETE /api/v1/applications/{id} - Delete application."""
        response = await async_client.delete(
            f"/api/v1/applications/{sample_application.id}", headers=auth_headers
        )

        assert response.status_code == 204

        # Verify deletion
        response = await async_client.get(
            f"/api/v1/applications/{sample_application.id}", headers=auth_headers
        )
        assert response.status_code == 404


class TestApplicationList:
    """Test listing and filtering applications."""

    async def test_list_applications_empty(self, async_client, auth_headers):
        """Test listing with no applications."""
        response = await async_client.get("/api/v1/applications", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

    async def test_list_applications(
        self, async_client, auth_headers, multiple_applications
    ):
        """Test GET /api/v1/applications - List all applications."""
        response = await async_client.get("/api/v1/applications", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 5
        # Check each item has job details
        for item in data["items"]:
            assert "job_company_name" in item
            assert "job_title" in item

    async def test_list_applications_pagination(
        self, async_client, auth_headers, multiple_applications
    ):
        """Test pagination of applications."""
        response = await async_client.get(
            "/api/v1/applications?page=1&page_size=2", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total_pages"] == 3

    async def test_list_applications_filter_by_status(
        self, async_client, auth_headers, multiple_applications
    ):
        """Test filtering applications by status."""
        response = await async_client.get(
            "/api/v1/applications?status=submitted", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all(item["status"] == "submitted" for item in data["items"])

    async def test_list_applications_filter_by_job(
        self, async_client, auth_headers, multiple_applications
    ):
        """Test filtering applications by job posting."""
        job_id = multiple_applications[0].job_posting_id

        response = await async_client.get(
            f"/api/v1/applications?job_posting_id={job_id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert all(item["job_posting_id"] == str(job_id) for item in data["items"])

    async def test_list_applications_sort_by_created_desc(
        self, async_client, auth_headers, multiple_applications
    ):
        """Test sorting applications by created_at descending."""
        response = await async_client.get(
            "/api/v1/applications?sort_by=created_at&sort_order=desc",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]
        # Check descending order
        for i in range(len(items) - 1):
            assert items[i]["created_at"] >= items[i + 1]["created_at"]

    async def test_list_applications_sort_by_created_asc(
        self, async_client, auth_headers, multiple_applications
    ):
        """Test sorting applications by created_at ascending."""
        response = await async_client.get(
            "/api/v1/applications?sort_by=created_at&sort_order=asc",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        items = data["items"]
        # Check ascending order
        for i in range(len(items) - 1):
            assert items[i]["created_at"] <= items[i + 1]["created_at"]


class TestApplicationStats:
    """Test application statistics."""

    async def test_get_application_stats_empty(self, async_client, auth_headers):
        """Test GET /api/v1/applications/stats - Empty stats."""
        response = await async_client.get(
            "/api/v1/applications/stats", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_applications"] == 0
        assert data["submitted_count"] == 0
        assert data["draft_count"] == 0
        assert data["response_rate"] is None
        assert data["recent_applications_count"] == 0

    async def test_get_application_stats_with_data(
        self, async_client, auth_headers, multiple_applications
    ):
        """Test stats with multiple applications."""
        response = await async_client.get(
            "/api/v1/applications/stats", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_applications"] == 5
        assert len(data["by_status"]) > 0
        # Check status counts
        assert data["submitted_count"] >= 2
        assert data["draft_count"] >= 1
        assert data["recent_applications_count"] == 5


class TestApplicationAuthorization:
    """Test authorization and access control."""

    async def test_cannot_access_other_user_application(
        self, async_client, auth_headers, sample_application, db_session, other_user
    ):
        """Test that users cannot access other users' applications."""
        from app.core.security import create_access_token

        # Create token for other user
        other_token = create_access_token(
            data={"sub": other_user.email, "user_id": str(other_user.id)}
        )
        other_headers = {"Authorization": f"Bearer {other_token}"}

        # Try to access sample_application (belongs to test_user)
        response = await async_client.get(
            f"/api/v1/applications/{sample_application.id}", headers=other_headers
        )

        assert response.status_code == 403
