"""Tests for structured data CRUD operations (Phase 2)."""
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


class TestWorkExperience:
    """Test work experience CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_work_experience(
        self, async_client: AsyncClient, auth_headers: dict, master_resume_id: str
    ):
        """Test creating work experience."""
        data = {
            "master_resume_id": master_resume_id,
            "company_name": "TechCorp",
            "job_title": "Senior Developer",
            "employment_type": "full_time",
            "start_date": "2020-01-01",
            "is_current": True,
            "description": "Developed backend systems",
        }

        response = await async_client.post(
            "/api/v1/resumes/work-experiences",
            headers=auth_headers,
            json=data,
        )

        assert response.status_code == 201
        result = response.json()
        assert result["company_name"] == "TechCorp"
        assert result["job_title"] == "Senior Developer"

    @pytest.mark.asyncio
    async def test_list_work_experiences(
        self, async_client: AsyncClient, auth_headers: dict, master_resume_id: str
    ):
        """Test listing work experiences."""
        # Create one first
        data = {
            "master_resume_id": master_resume_id,
            "company_name": "TechCorp",
            "job_title": "Developer",
            "employment_type": "full_time",
            "start_date": "2020-01-01",
            "is_current": True,
        }
        await async_client.post(
            "/api/v1/resumes/work-experiences",
            headers=auth_headers,
            json=data,
        )

        # List
        response = await async_client.get(
            "/api/v1/resumes/work-experiences",
            headers=auth_headers,
        )

        assert response.status_code == 200
        result = response.json()
        assert result["total"] >= 1
        assert len(result["items"]) >= 1

    @pytest.mark.asyncio
    async def test_update_work_experience(
        self, async_client: AsyncClient, auth_headers: dict, master_resume_id: str
    ):
        """Test updating work experience."""
        # Create
        create_data = {
            "master_resume_id": master_resume_id,
            "company_name": "TechCorp",
            "job_title": "Developer",
            "employment_type": "full_time",
            "start_date": "2020-01-01",
            "is_current": True,
        }
        create_response = await async_client.post(
            "/api/v1/resumes/work-experiences",
            headers=auth_headers,
            json=create_data,
        )
        work_id = create_response.json()["id"]

        # Update
        update_data = {"job_title": "Senior Developer"}
        response = await async_client.put(
            f"/api/v1/resumes/work-experiences/{work_id}",
            headers=auth_headers,
            json=update_data,
        )

        assert response.status_code == 200
        assert response.json()["job_title"] == "Senior Developer"

    @pytest.mark.asyncio
    async def test_delete_work_experience(
        self, async_client: AsyncClient, auth_headers: dict, master_resume_id: str
    ):
        """Test deleting work experience."""
        # Create
        create_data = {
            "master_resume_id": master_resume_id,
            "company_name": "TechCorp",
            "job_title": "Developer",
            "employment_type": "full_time",
            "start_date": "2020-01-01",
            "is_current": True,
        }
        create_response = await async_client.post(
            "/api/v1/resumes/work-experiences",
            headers=auth_headers,
            json=create_data,
        )
        work_id = create_response.json()["id"]

        # Delete
        response = await async_client.delete(
            f"/api/v1/resumes/work-experiences/{work_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204


class TestEducation:
    """Test education CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_education(
        self, async_client: AsyncClient, auth_headers: dict, master_resume_id: str
    ):
        """Test creating education entry."""
        data = {
            "master_resume_id": master_resume_id,
            "institution": "Stanford University",
            "degree_type": "bachelor",
            "field_of_study": "Computer Science",
            "start_date": "2010-09-01",
            "end_date": "2014-06-01",
        }

        response = await async_client.post(
            "/api/v1/resumes/education",
            headers=auth_headers,
            json=data,
        )

        assert response.status_code == 201
        result = response.json()
        assert result["institution"] == "Stanford University"


class TestSkills:
    """Test skills CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_skill(
        self, async_client: AsyncClient, auth_headers: dict, master_resume_id: str
    ):
        """Test creating a skill."""
        data = {
            "master_resume_id": master_resume_id,
            "skill_name": "Python",
            "category": "programming_language",
        }

        response = await async_client.post(
            "/api/v1/resumes/skills",
            headers=auth_headers,
            json=data,
        )

        assert response.status_code == 201
        result = response.json()
        assert result["skill_name"] == "Python"

    @pytest.mark.asyncio
    async def test_list_skills(
        self, async_client: AsyncClient, auth_headers: dict, master_resume_id: str
    ):
        """Test listing skills."""
        # Create one first
        data = {
            "master_resume_id": master_resume_id,
            "skill_name": "Python",
            "category": "programming_language",
        }
        await async_client.post(
            "/api/v1/resumes/skills",
            headers=auth_headers,
            json=data,
        )

        # List
        response = await async_client.get(
            "/api/v1/resumes/skills",
            headers=auth_headers,
        )

        assert response.status_code == 200
        result = response.json()
        assert result["total"] >= 1


class TestCertifications:
    """Test certifications CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_certification(
        self, async_client: AsyncClient, auth_headers: dict, master_resume_id: str
    ):
        """Test creating a certification."""
        data = {
            "master_resume_id": master_resume_id,
            "certification_name": "AWS Solutions Architect",
            "issuing_organization": "Amazon Web Services",
            "issue_date": "2022-01-15",
        }

        response = await async_client.post(
            "/api/v1/resumes/certifications",
            headers=auth_headers,
            json=data,
        )

        assert response.status_code == 201
        result = response.json()
        assert result["certification_name"] == "AWS Solutions Architect"
