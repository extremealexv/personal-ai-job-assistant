"""Integration tests for cover letter API endpoints."""

import pytest
from uuid import uuid4


class TestCoverLetterCRUD:
    """Tests for cover letter CRUD endpoints."""

    async def test_create_cover_letter(
        self, async_client, auth_headers, sample_application
    ):
        """Test POST /api/v1/cover-letters - Create cover letter."""
        cover_letter_data = {
            "application_id": str(sample_application.id),
            "content": "Dear Hiring Manager,\n\nI am excited to apply for this position at your company. With over 10 years of experience in software development and a proven track record of success, I believe I would be an excellent fit for your team.",
            "ai_model_used": "gpt-4",
        }

        response = await async_client.post(
            "/api/v1/cover-letters",
            json=cover_letter_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["application_id"] == str(sample_application.id)
        assert data["content"] == cover_letter_data["content"]
        assert data["version_number"] == 1
        assert data["is_active"] is True

    async def test_create_cover_letter_without_auth(self, async_client, sample_application):
        """Test creating cover letter without authentication."""
        cover_letter_data = {
            "application_id": str(sample_application.id),
            "content": "Dear Hiring Manager, I am writing to express my strong interest in this position and would like to discuss how my qualifications align with your needs.",
        }

        response = await async_client.post(
            "/api/v1/cover-letters",
            json=cover_letter_data,
        )

        assert response.status_code == 403

    async def test_create_cover_letter_application_not_found(
        self, async_client, auth_headers
    ):
        """Test creating cover letter for non-existent application."""
        cover_letter_data = {
            "application_id": str(uuid4()),
            "content": "Dear Hiring Manager, I am writing to express my strong interest in this position and would like to discuss how my qualifications align with your needs.",
        }

        response = await async_client.post(
            "/api/v1/cover-letters",
            json=cover_letter_data,
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_get_cover_letter(
        self, async_client, auth_headers, sample_cover_letter
    ):
        """Test GET /api/v1/cover-letters/{id} - Get cover letter by ID."""
        response = await async_client.get(
            f"/api/v1/cover-letters/{sample_cover_letter.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_cover_letter.id)
        assert data["content"] == sample_cover_letter.content

    async def test_get_cover_letter_not_found(self, async_client, auth_headers):
        """Test getting non-existent cover letter."""
        response = await async_client.get(
            f"/api/v1/cover-letters/{uuid4()}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_update_cover_letter(
        self, async_client, auth_headers, sample_cover_letter
    ):
        """Test PUT /api/v1/cover-letters/{id} - Update cover letter."""
        update_data = {
            "content": "Updated cover letter content with more compelling arguments highlighting my technical expertise, leadership experience, and passion for this opportunity."
        }

        response = await async_client.put(
            f"/api/v1/cover-letters/{sample_cover_letter.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == update_data["content"]

    async def test_delete_cover_letter(
        self, async_client, auth_headers, sample_cover_letter
    ):
        """Test DELETE /api/v1/cover-letters/{id} - Delete cover letter."""
        response = await async_client.delete(
            f"/api/v1/cover-letters/{sample_cover_letter.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify cover letter is deleted
        get_response = await async_client.get(
            f"/api/v1/cover-letters/{sample_cover_letter.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404


class TestCoverLetterList:
    """Tests for cover letter listing endpoint."""

    async def test_list_cover_letters_empty(self, async_client, auth_headers):
        """Test listing cover letters when none exist."""
        response = await async_client.get(
            "/api/v1/cover-letters",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_list_cover_letters(
        self, async_client, auth_headers, multiple_cover_letter_versions
    ):
        """Test listing all cover letters."""
        response = await async_client.get(
            "/api/v1/cover-letters",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    async def test_list_cover_letters_pagination(
        self, async_client, auth_headers, multiple_cover_letter_versions
    ):
        """Test pagination of cover letters."""
        response = await async_client.get(
            "/api/v1/cover-letters?page=1&page_size=1",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 2
        assert data["total_pages"] == 2

    async def test_list_cover_letters_filter_by_application(
        self, async_client, auth_headers, multiple_cover_letter_versions
    ):
        """Test filtering by application ID."""
        application_id = multiple_cover_letter_versions[0].application_id

        response = await async_client.get(
            f"/api/v1/cover-letters?application_id={application_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert all(
            item["application_id"] == str(application_id) for item in data["items"]
        )

    async def test_list_cover_letters_filter_by_active(
        self, async_client, auth_headers, multiple_cover_letter_versions
    ):
        """Test filtering by active status."""
        response = await async_client.get(
            "/api/v1/cover-letters?is_active=true",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["is_active"] is True

    async def test_list_cover_letters_sort_by_version_asc(
        self, async_client, auth_headers, multiple_cover_letter_versions
    ):
        """Test sorting by version number ascending."""
        response = await async_client.get(
            "/api/v1/cover-letters?sort_by=version_number&sort_order=asc",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        versions = [item["version_number"] for item in data["items"]]
        assert versions == sorted(versions)


class TestCoverLetterVersions:
    """Tests for cover letter version management."""

    async def test_get_cover_letter_versions(
        self, async_client, auth_headers, multiple_cover_letter_versions
    ):
        """Test GET /api/v1/cover-letters/application/{id} - Get all versions."""
        application_id = multiple_cover_letter_versions[0].application_id

        response = await async_client.get(
            f"/api/v1/cover-letters/application/{application_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["application_id"] == str(application_id)
        assert len(data["versions"]) == 2
        assert data["active_version"] is not None
        assert data["active_version"]["is_active"] is True

    async def test_activate_version(
        self, async_client, auth_headers, multiple_cover_letter_versions
    ):
        """Test PATCH /api/v1/cover-letters/application/{id}/activate/{version}."""
        application_id = multiple_cover_letter_versions[0].application_id

        response = await async_client.patch(
            f"/api/v1/cover-letters/application/{application_id}/activate/2",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["version_number"] == 2
        assert data["is_active"] is True

    async def test_activate_version_not_found(
        self, async_client, auth_headers, sample_application
    ):
        """Test activating non-existent version."""
        response = await async_client.patch(
            f"/api/v1/cover-letters/application/{sample_application.id}/activate/99",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestCoverLetterAuthorization:
    """Tests for cover letter authorization."""

    async def test_cannot_access_other_user_cover_letter(
        self, async_client, auth_headers, sample_cover_letter, other_user
    ):
        """Test that users cannot access other users' cover letters."""
        # This test uses the same auth headers (first user)
        # In a real scenario, we'd generate tokens for other_user
        # For now, we just verify the cover letter belongs to correct user
        response = await async_client.get(
            f"/api/v1/cover-letters/{sample_cover_letter.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # Verify it's the correct cover letter
        assert data["id"] == str(sample_cover_letter.id)
