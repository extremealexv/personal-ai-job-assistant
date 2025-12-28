"""Tests for master resume management (Phase 1)."""
import io

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def uploaded_resume_id(
    async_client: AsyncClient, auth_headers: dict, test_pdf_content: bytes, db_session
) -> str:
    """Upload a resume and return its ID for testing retrieval/deletion."""
    files = {"file": ("resume.pdf", io.BytesIO(test_pdf_content), "application/pdf")}
    response = await async_client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers,
        files=files,
    )
    assert response.status_code == 201, f"Upload failed: {response.json()}"
    
    # Ensure the upload is committed and visible
    await db_session.commit()
    
    return response.json()["id"]


class TestMasterResumeUpload:
    """Test master resume upload functionality."""

    @pytest.mark.asyncio
    async def test_upload_pdf_resume(
        self, async_client: AsyncClient, auth_headers: dict, test_pdf_content: bytes
    ):
        """Test uploading a PDF resume."""
        files = {"file": ("resume.pdf", io.BytesIO(test_pdf_content), "application/pdf")}
        response = await async_client.post(
            "/api/v1/resumes/upload",
            headers=auth_headers,
            files=files,
        )

        assert response.status_code == 201
        result = response.json()
        assert "id" in result
        assert result["filename"] == "resume.pdf"
        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_upload_without_auth(
        self, async_client: AsyncClient, test_pdf_content: bytes
    ):
        """Test that uploading without authentication fails."""
        files = {"file": ("resume.pdf", io.BytesIO(test_pdf_content), "application/pdf")}
        response = await async_client.post(
            "/api/v1/resumes/upload",
            files=files,
        )

        assert response.status_code == 403
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_upload_invalid_file_type(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test that invalid file types are rejected."""
        files = {"file": ("document.txt", io.BytesIO(b"text content"), "text/plain")}
        response = await async_client.post(
            "/api/v1/resumes/upload",
            headers=auth_headers,
            files=files,
        )

        assert response.status_code == 400


class TestMasterResumeRetrieval:
    """Test master resume retrieval."""

    @pytest.mark.asyncio
    async def test_get_master_resume(
        self, async_client: AsyncClient, auth_headers: dict, uploaded_resume_id: str
    ):
        """Test retrieving a master resume."""
        response = await async_client.get(
            f"/api/v1/resumes/{uploaded_resume_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        result = response.json()
        assert result["id"] == uploaded_resume_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_resume(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test retrieving a non-existent resume returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await async_client.get(
            f"/api/v1/resumes/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestMasterResumeDeletion:
    """Test master resume deletion."""

    @pytest.mark.asyncio
    async def test_delete_master_resume(
        self, async_client: AsyncClient, auth_headers: dict, uploaded_resume_id: str
    ):
        """Test deleting a master resume."""
        # Delete
        response = await async_client.delete(
            f"/api/v1/resumes/{uploaded_resume_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify it's gone
        get_response = await async_client.get(
            f"/api/v1/resumes/{uploaded_resume_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404
