"""Integration tests for Prompt Templates API endpoints."""

import pytest
from uuid import uuid4

from app.models.prompt import PromptTask


@pytest.mark.asyncio
class TestPromptTemplateCRUD:
    """Test CRUD operations via API."""

    async def test_create_prompt_template(self, async_client, auth_headers):
        """Test creating a prompt template."""
        response = await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "resume_tailor",
                "role_type": "backend_engineer",
                "name": "Backend Engineer Resume Optimizer",
                "prompt_text": "You are an expert resume writer...",
                "is_system_prompt": False,
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Backend Engineer Resume Optimizer"
        assert data["task_type"] == "resume_tailor"
        assert data["role_type"] == "backend_engineer"
        assert data["version"] == 1
        assert data["is_active"] is True
        assert data["times_used"] == 0
        assert "id" in data

    async def test_create_prompt_template_without_auth(self, async_client):
        """Test creating prompt without authentication fails."""
        response = await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "resume_tailor",
                "name": "Test",
                "prompt_text": "...",
            },
        )

        assert response.status_code == 403

    async def test_create_prompt_invalid_task_type(
        self, async_client, auth_headers
    ):
        """Test creating prompt with invalid task_type fails."""
        response = await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "invalid_task",
                "name": "Test",
                "prompt_text": "...",
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_create_prompt_missing_required_fields(
        self, async_client, auth_headers
    ):
        """Test creating prompt without required fields fails."""
        response = await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "resume_tailor",
                # Missing name and prompt_text
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_get_prompt_template(self, async_client, auth_headers):
        """Test retrieving a prompt template by ID."""
        # Create prompt
        create_response = await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "cover_letter",
                "name": "Cover Letter Template",
                "prompt_text": "Generate a cover letter...",
            },
            headers=auth_headers,
        )
        prompt_id = create_response.json()["id"]

        # Get prompt
        response = await async_client.get(
            f"/api/v1/prompt-templates/{prompt_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == prompt_id
        assert data["name"] == "Cover Letter Template"

    async def test_get_prompt_template_not_found(
        self, async_client, auth_headers
    ):
        """Test getting non-existent prompt returns 404."""
        fake_id = str(uuid4())
        response = await async_client.get(
            f"/api/v1/prompt-templates/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_update_prompt_template(self, async_client, auth_headers):
        """Test updating a prompt template."""
        # Create prompt
        create_response = await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "form_answers",
                "name": "Original Name",
                "prompt_text": "Original text",
            },
            headers=auth_headers,
        )
        prompt_id = create_response.json()["id"]

        # Update prompt
        response = await async_client.put(
            f"/api/v1/prompt-templates/{prompt_id}",
            json={
                "name": "Updated Name",
                "prompt_text": "Updated text",
                "is_active": False,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["prompt_text"] == "Updated text"
        assert data["is_active"] is False

    async def test_update_prompt_partial_fields(
        self, async_client, auth_headers
    ):
        """Test updating only specific fields."""
        # Create prompt
        create_response = await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "resume_tailor",
                "role_type": "engineer",
                "name": "Original",
                "prompt_text": "Original",
            },
            headers=auth_headers,
        )
        prompt_id = create_response.json()["id"]

        # Update only name
        response = await async_client.put(
            f"/api/v1/prompt-templates/{prompt_id}",
            json={"name": "New Name"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["prompt_text"] == "Original"  # Unchanged
        assert data["role_type"] == "engineer"  # Unchanged

    async def test_delete_prompt_template(self, async_client, auth_headers):
        """Test deleting a prompt template."""
        # Create prompt
        create_response = await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "resume_tailor",
                "name": "To Delete",
                "prompt_text": "...",
            },
            headers=auth_headers,
        )
        prompt_id = create_response.json()["id"]

        # Delete prompt
        response = await async_client.delete(
            f"/api/v1/prompt-templates/{prompt_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify it's deleted
        get_response = await async_client.get(
            f"/api/v1/prompt-templates/{prompt_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404


@pytest.mark.asyncio
class TestPromptTemplateList:
    """Test listing and filtering prompt templates."""

    async def test_list_prompts_empty(self, async_client, auth_headers):
        """Test listing prompts when none exist."""
        response = await async_client.get(
            "/api/v1/prompt-templates/",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data == []

    async def test_list_prompts(self, async_client, auth_headers):
        """Test listing all prompts."""
        # Create multiple prompts
        for i in range(3):
            await async_client.post(
                "/api/v1/prompt-templates/",
                json={
                    "task_type": "resume_tailor",
                    "name": f"Template {i}",
                    "prompt_text": f"Text {i}",
                },
                headers=auth_headers,
            )

        response = await async_client.get(
            "/api/v1/prompt-templates/",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    async def test_list_prompts_pagination(self, async_client, auth_headers):
        """Test pagination of prompt list."""
        # Create 5 prompts
        for i in range(5):
            await async_client.post(
                "/api/v1/prompt-templates/",
                json={
                    "task_type": "resume_tailor",
                    "name": f"Template {i}",
                    "prompt_text": "...",
                },
                headers=auth_headers,
            )

        # Get first 2
        response = await async_client.get(
            "/api/v1/prompt-templates/?skip=0&limit=2",
            headers=auth_headers,
        )
        assert response.status_code == 200
        page1 = response.json()
        assert len(page1) == 2

        # Get next 2
        response = await async_client.get(
            "/api/v1/prompt-templates/?skip=2&limit=2",
            headers=auth_headers,
        )
        assert response.status_code == 200
        page2 = response.json()
        assert len(page2) == 2

        # Verify different results
        assert page1[0]["id"] != page2[0]["id"]

    async def test_list_filter_by_task_type(self, async_client, auth_headers):
        """Test filtering prompts by task type."""
        # Create prompts with different task types
        await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "resume_tailor",
                "name": "Resume",
                "prompt_text": "...",
            },
            headers=auth_headers,
        )
        await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "cover_letter",
                "name": "Cover Letter",
                "prompt_text": "...",
            },
            headers=auth_headers,
        )

        # Filter by resume_tailor
        response = await async_client.get(
            "/api/v1/prompt-templates/?task_type=resume_tailor",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["task_type"] == "resume_tailor"

    async def test_list_filter_by_role_type(self, async_client, auth_headers):
        """Test filtering prompts by role type."""
        await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "resume_tailor",
                "role_type": "backend_engineer",
                "name": "Backend",
                "prompt_text": "...",
            },
            headers=auth_headers,
        )
        await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "resume_tailor",
                "role_type": "frontend_engineer",
                "name": "Frontend",
                "prompt_text": "...",
            },
            headers=auth_headers,
        )

        response = await async_client.get(
            "/api/v1/prompt-templates/?role_type=backend_engineer",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["role_type"] == "backend_engineer"

    async def test_list_filter_by_active_status(
        self, async_client, auth_headers
    ):
        """Test filtering prompts by active status."""
        # Create active prompt
        await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "resume_tailor",
                "name": "Active",
                "prompt_text": "...",
            },
            headers=auth_headers,
        )

        # Create and deactivate prompt
        create_response = await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "resume_tailor",
                "name": "Inactive",
                "prompt_text": "...",
            },
            headers=auth_headers,
        )
        prompt_id = create_response.json()["id"]
        await async_client.put(
            f"/api/v1/prompt-templates/{prompt_id}",
            json={"is_active": False},
            headers=auth_headers,
        )

        # Filter for active only
        response = await async_client.get(
            "/api/v1/prompt-templates/?is_active=true",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["is_active"] is True


@pytest.mark.asyncio
class TestPromptTemplateClone:
    """Test cloning/duplicating prompt templates."""

    async def test_duplicate_prompt(self, async_client, auth_headers):
        """Test duplicating a prompt template."""
        # Create original
        create_response = await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "resume_tailor",
                "role_type": "backend_engineer",
                "name": "Original",
                "prompt_text": "Original text",
            },
            headers=auth_headers,
        )
        original_id = create_response.json()["id"]

        # Duplicate with modifications
        response = await async_client.post(
            f"/api/v1/prompt-templates/{original_id}/duplicate",
            json={
                "name": "Cloned Version",
                "prompt_text": "Modified text",
                "role_type": "fullstack_engineer",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] != original_id
        assert data["name"] == "Cloned Version"
        assert data["prompt_text"] == "Modified text"
        assert data["role_type"] == "fullstack_engineer"
        assert data["task_type"] == "resume_tailor"  # Inherited
        assert data["parent_template_id"] == original_id

    async def test_duplicate_nonexistent_prompt(
        self, async_client, auth_headers
    ):
        """Test duplicating non-existent prompt returns 404."""
        fake_id = str(uuid4())
        response = await async_client.post(
            f"/api/v1/prompt-templates/{fake_id}/duplicate",
            json={
                "name": "Clone",
                "prompt_text": "...",
            },
            headers=auth_headers,
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestPromptTemplateStats:
    """Test usage statistics endpoint."""

    async def test_get_prompt_stats(self, async_client, auth_headers):
        """Test getting prompt statistics."""
        # Create prompt
        create_response = await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "cover_letter",
                "name": "Test",
                "prompt_text": "...",
            },
            headers=auth_headers,
        )
        prompt_id = create_response.json()["id"]

        # Get stats
        response = await async_client.get(
            f"/api/v1/prompt-templates/{prompt_id}/stats",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["prompt_id"] == prompt_id
        assert data["times_used"] == 0
        assert data["avg_satisfaction_score"] is None

    async def test_get_stats_nonexistent_prompt(
        self, async_client, auth_headers
    ):
        """Test getting stats for non-existent prompt returns 404."""
        fake_id = str(uuid4())
        response = await async_client.get(
            f"/api/v1/prompt-templates/{fake_id}/stats",
            headers=auth_headers,
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestPromptTemplateAuthorization:
    """Test authorization and user isolation."""

    async def test_cannot_access_other_user_prompt(
        self, async_client, auth_headers, other_user_auth_headers
    ):
        """Test users cannot access other users' prompts."""
        # Create prompt as user 1
        create_response = await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "resume_tailor",
                "name": "User 1 Prompt",
                "prompt_text": "...",
            },
            headers=auth_headers,
        )
        prompt_id = create_response.json()["id"]

        # Try to access as user 2
        response = await async_client.get(
            f"/api/v1/prompt-templates/{prompt_id}",
            headers=other_user_auth_headers,
        )

        assert response.status_code == 403

    async def test_cannot_update_other_user_prompt(
        self, async_client, auth_headers, other_user_auth_headers
    ):
        """Test users cannot update other users' prompts."""
        # Create prompt as user 1
        create_response = await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "resume_tailor",
                "name": "User 1 Prompt",
                "prompt_text": "...",
            },
            headers=auth_headers,
        )
        prompt_id = create_response.json()["id"]

        # Try to update as user 2
        response = await async_client.put(
            f"/api/v1/prompt-templates/{prompt_id}",
            json={"name": "Hacked Name"},
            headers=other_user_auth_headers,
        )

        assert response.status_code == 403

    async def test_cannot_delete_other_user_prompt(
        self, async_client, auth_headers, other_user_auth_headers
    ):
        """Test users cannot delete other users' prompts."""
        # Create prompt as user 1
        create_response = await async_client.post(
            "/api/v1/prompt-templates/",
            json={
                "task_type": "resume_tailor",
                "name": "User 1 Prompt",
                "prompt_text": "...",
            },
            headers=auth_headers,
        )
        prompt_id = create_response.json()["id"]

        # Try to delete as user 2
        response = await async_client.delete(
            f"/api/v1/prompt-templates/{prompt_id}",
            headers=other_user_auth_headers,
        )

        assert response.status_code == 403
