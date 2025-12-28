"""Tests for resume version management (Phase 3)."""
import io

import pytest
from httpx import AsyncClient


@pytest.fixture
async def master_resume_id(
    async_client: AsyncClient, auth_headers: dict, test_pdf_content: bytes
) -> str:
    """Create a master resume and return its ID."""
    files = {"file": ("resume.pdf", io.BytesIO(test_pdf_content), "application/pdf")}
    response = await async_client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers,
        files=files,
    )
    return response.json()["id"]


class TestResumeVersions:
    """Test resume version CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_resume_version(
        self, async_client: AsyncClient, auth_headers: dict, master_resume_id: str
    ):
        """Test creating a resume version."""
        data = {
            "master_resume_id": master_resume_id,
            "version_name": "Backend Engineer - TechCorp",
            "target_role": "Backend Engineer",
            "target_company": "TechCorp",
            "modifications": {
                "skills_emphasized": ["Python", "FastAPI"],
            },
        }

        response = await async_client.post(
            "/api/v1/resumes/versions",
            headers=auth_headers,
            json=data,
        )

        assert response.status_code == 201
        result = response.json()
        assert result["version_name"] == "Backend Engineer - TechCorp"
        assert result["target_role"] == "Backend Engineer"

    @pytest.mark.asyncio
    async def test_list_resume_versions(
        self, async_client: AsyncClient, auth_headers: dict, master_resume_id: str
    ):
        """Test listing resume versions."""
        # Create version first
        data = {
            "master_resume_id": master_resume_id,
            "version_name": "Test Version",
            "target_role": "Developer",
        }
        await async_client.post(
            "/api/v1/resumes/versions",
            headers=auth_headers,
            json=data,
        )

        # List
        response = await async_client.get(
            "/api/v1/resumes/versions",
            headers=auth_headers,
        )

        assert response.status_code == 200
        result = response.json()
        assert result["total"] >= 1
        assert len(result["items"]) >= 1

    @pytest.mark.asyncio
    async def test_get_resume_version(
        self, async_client: AsyncClient, auth_headers: dict, master_resume_id: str
    ):
        """Test getting a specific resume version."""
        # Create
        create_data = {
            "master_resume_id": master_resume_id,
            "version_name": "Test Version",
            "target_role": "Developer",
        }
        create_response = await async_client.post(
            "/api/v1/resumes/versions",
            headers=auth_headers,
            json=create_data,
        )
        version_id = create_response.json()["id"]

        # Get
        response = await async_client.get(
            f"/api/v1/resumes/versions/{version_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["id"] == version_id

    @pytest.mark.asyncio
    async def test_update_resume_version(
        self, async_client: AsyncClient, auth_headers: dict, master_resume_id: str
    ):
        """Test updating a resume version."""
        # Create
        create_data = {
            "master_resume_id": master_resume_id,
            "version_name": "Original Name",
            "target_role": "Developer",
        }
        create_response = await async_client.post(
            "/api/v1/resumes/versions",
            headers=auth_headers,
            json=create_data,
        )
        version_id = create_response.json()["id"]

        # Update
        update_data = {"version_name": "Updated Name"}
        response = await async_client.put(
            f"/api/v1/resumes/versions/{version_id}",
            headers=auth_headers,
            json=update_data,
        )

        assert response.status_code == 200
        assert response.json()["version_name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_delete_resume_version(
        self, async_client: AsyncClient, auth_headers: dict, master_resume_id: str
    ):
        """Test deleting a resume version (soft delete)."""
        # Create
        create_data = {
            "master_resume_id": master_resume_id,
            "version_name": "Test Version",
            "target_role": "Developer",
        }
        create_response = await async_client.post(
            "/api/v1/resumes/versions",
            headers=auth_headers,
            json=create_data,
        )
        version_id = create_response.json()["id"]

        # Delete
        response = await async_client.delete(
            f"/api/v1/resumes/versions/{version_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify it's gone
        get_response = await async_client.get(
            f"/api/v1/resumes/versions/{version_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404
