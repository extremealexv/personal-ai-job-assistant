"""Tests for advanced resume features (Phase 4)."""
import io

import pytest
from httpx import AsyncClient


@pytest.fixture
async def master_resume_with_data(
    async_client: AsyncClient, auth_headers: dict, test_pdf_content: bytes
) -> str:
    """Create a master resume with work experience and skills."""
    # Upload resume
    files = {"file": ("resume.pdf", io.BytesIO(test_pdf_content), "application/pdf")}
    response = await async_client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers,
        files=files,
    )
    resume_id = response.json()["id"]

    # Add work experience
    work_data = {
        "master_resume_id": resume_id,
        "company_name": "TechCorp",
        "job_title": "Senior Python Developer",
        "employment_type": "full_time",
        "start_date": "2020-01-01",
        "is_current": True,
        "description": "Python backend development",
    }
    await async_client.post(
        "/api/v1/resumes/work-experiences",
        headers=auth_headers,
        json=work_data,
    )

    # Add skills
    skills = ["Python", "FastAPI", "PostgreSQL"]
    for skill in skills:
        skill_data = {
            "master_resume_id": resume_id,
            "skill_name": skill,
            "category": "programming_language",
        }
        await async_client.post(
            "/api/v1/resumes/skills",
            headers=auth_headers,
            json=skill_data,
        )

    return resume_id


class TestSearch:
    """Test resume search functionality."""

    @pytest.mark.asyncio
    async def test_search_by_skill(
        self, async_client: AsyncClient, auth_headers: dict, master_resume_with_data: str
    ):
        """Test searching by skill name."""
        response = await async_client.get(
            "/api/v1/resumes/search?q=Python",
            headers=auth_headers,
        )

        assert response.status_code == 200
        result = response.json()
        assert result["total_results"] > 0
        assert len(result["skills"]) > 0
        assert any(skill["skill_name"] == "Python" for skill in result["skills"])

    @pytest.mark.asyncio
    async def test_search_by_company(
        self, async_client: AsyncClient, auth_headers: dict, master_resume_with_data: str
    ):
        """Test searching by company name."""
        response = await async_client.get(
            "/api/v1/resumes/search?q=TechCorp",
            headers=auth_headers,
        )

        assert response.status_code == 200
        result = response.json()
        assert result["total_results"] > 0
        assert len(result["work_experiences"]) > 0

    @pytest.mark.asyncio
    async def test_search_no_results(
        self, async_client: AsyncClient, auth_headers: dict, master_resume_with_data: str
    ):
        """Test search with no matching results."""
        response = await async_client.get(
            "/api/v1/resumes/search?q=NonExistentTerm123456",
            headers=auth_headers,
        )

        assert response.status_code == 200
        result = response.json()
        assert result["total_results"] == 0


class TestStatistics:
    """Test resume statistics functionality."""

    @pytest.mark.asyncio
    async def test_get_stats_empty(
        self, async_client: AsyncClient, auth_headers: dict, test_pdf_content: bytes
    ):
        """Test getting stats for resume with no structured data."""
        # Upload resume only
        files = {"file": ("resume.pdf", io.BytesIO(test_pdf_content), "application/pdf")}
        await async_client.post(
            "/api/v1/resumes/upload",
            headers=auth_headers,
            files=files,
        )

        response = await async_client.get(
            "/api/v1/resumes/stats",
            headers=auth_headers,
        )

        assert response.status_code == 200
        result = response.json()
        assert "structured_data" in result
        assert "resume_versions" in result

    @pytest.mark.asyncio
    async def test_get_stats_with_data(
        self, async_client: AsyncClient, auth_headers: dict, master_resume_with_data: str
    ):
        """Test getting stats with structured data."""
        response = await async_client.get(
            "/api/v1/resumes/stats",
            headers=auth_headers,
        )

        assert response.status_code == 200
        result = response.json()
        assert result["structured_data"]["work_experiences"] >= 1
        assert result["structured_data"]["skills"] >= 3


class TestDuplicateVersion:
    """Test resume version duplication."""

    @pytest.mark.asyncio
    async def test_duplicate_version(
        self, async_client: AsyncClient, auth_headers: dict, test_pdf_content: bytes
    ):
        """Test duplicating a resume version."""
        # Upload resume
        files = {"file": ("resume.pdf", io.BytesIO(test_pdf_content), "application/pdf")}
        upload_response = await async_client.post(
            "/api/v1/resumes/upload",
            headers=auth_headers,
            files=files,
        )
        resume_id = upload_response.json()["id"]

        # Create version
        version_data = {
            "master_resume_id": resume_id,
            "version_name": "Original Version",
            "target_role": "Developer",
        }
        create_response = await async_client.post(
            "/api/v1/resumes/versions",
            headers=auth_headers,
            json=version_data,
        )
        version_id = create_response.json()["id"]

        # Duplicate
        response = await async_client.post(
            f"/api/v1/resumes/versions/{version_id}/duplicate",
            headers=auth_headers,
        )

        assert response.status_code == 201
        result = response.json()
        assert "(Copy)" in result["version_name"]
        assert result["id"] != version_id

    @pytest.mark.asyncio
    async def test_duplicate_nonexistent_version(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test duplicating a non-existent version returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await async_client.post(
            f"/api/v1/resumes/versions/{fake_id}/duplicate",
            headers=auth_headers,
        )

        assert response.status_code == 404
