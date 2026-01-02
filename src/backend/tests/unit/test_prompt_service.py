"""Unit tests for PromptTemplateService."""

import pytest
from uuid import uuid4
from decimal import Decimal

from app.models.prompt import PromptTask, PromptTemplate
from app.schemas.prompt import (
    PromptTemplateCreate,
    PromptTemplateUpdate,
    PromptTemplateClone,
)
from app.services.prompt_service import PromptService
from app.core.exceptions import NotFoundError, ForbiddenError


@pytest.mark.asyncio
class TestPromptTemplateServiceCRUD:
    """Test CRUD operations for prompt templates."""

    async def test_create_prompt_template(self, db_session, test_user):
        """Test creating a new prompt template."""
        prompt_data = PromptTemplateCreate(
            task_type=PromptTask.RESUME_TAILOR,
            role_type="backend_engineer",
            name="Backend Engineer Resume Optimizer",
            prompt_text="You are an expert resume writer...",
            is_system_prompt=False,
        )

        prompt = await PromptService.create_prompt_template(
            db_session, test_user.id, prompt_data
        )

        assert prompt.id is not None
        assert prompt.user_id == test_user.id
        assert prompt.task_type == PromptTask.RESUME_TAILOR
        assert prompt.role_type == "backend_engineer"
        assert prompt.name == "Backend Engineer Resume Optimizer"
        assert prompt.version == 1
        assert prompt.is_active is True
        assert prompt.times_used == 0

    async def test_create_system_prompt(self, db_session, test_user):
        """Test creating a system-level prompt."""
        prompt_data = PromptTemplateCreate(
            task_type=PromptTask.COVER_LETTER,
            role_type=None,
            name="System Cover Letter Template",
            prompt_text="Generate a professional cover letter...",
            is_system_prompt=True,
        )

        prompt = await PromptService.create_prompt_template(
            db_session, test_user.id, prompt_data
        )

        assert prompt.is_system_prompt is True
        assert prompt.role_type is None

    async def test_get_prompt_template(self, db_session, test_user):
        """Test retrieving a prompt template by ID."""
        # Create prompt
        prompt_data = PromptTemplateCreate(
            task_type=PromptTask.FORM_ANSWERS,
            role_type="data_scientist",
            name="Form Answers Template",
            prompt_text="Answer form questions...",
        )
        created_prompt = await PromptService.create_prompt_template(
            db_session, test_user.id, prompt_data
        )

        # Retrieve prompt
        prompt = await PromptService.get_prompt_template(
            db_session, created_prompt.id, test_user.id
        )

        assert prompt.id == created_prompt.id
        assert prompt.name == "Form Answers Template"

    async def test_get_prompt_template_not_found(self, db_session, test_user):
        """Test getting non-existent prompt raises NotFoundError."""
        fake_id = uuid4()

        with pytest.raises(NotFoundError, match="not found"):
            await PromptService.get_prompt_template(
                db_session, fake_id, test_user.id
            )

    async def test_get_prompt_template_forbidden(
        self, db_session, test_user, other_user
    ):
        """Test getting another user's prompt raises ForbiddenError."""
        # Create prompt as other_user
        prompt_data = PromptTemplateCreate(
            task_type=PromptTask.RESUME_TAILOR,
            name="Other User's Template",
            prompt_text="...",
        )
        prompt = await PromptService.create_prompt_template(
            db_session, other_user.id, prompt_data
        )

        # Try to access as test_user
        with pytest.raises(ForbiddenError, match="Cannot access"):
            await PromptService.get_prompt_template(
                db_session, prompt.id, test_user.id
            )

    async def test_update_prompt_template(self, db_session, test_user):
        """Test updating a prompt template."""
        # Create prompt
        prompt_data = PromptTemplateCreate(
            task_type=PromptTask.RESUME_TAILOR,
            name="Original Name",
            prompt_text="Original text",
        )
        prompt = await PromptService.create_prompt_template(
            db_session, test_user.id, prompt_data
        )

        # Update prompt
        update_data = PromptTemplateUpdate(
            name="Updated Name",
            prompt_text="Updated text",
            is_active=False,
        )
        updated = await PromptService.update_prompt_template(
            db_session, prompt.id, test_user.id, update_data
        )

        assert updated.name == "Updated Name"
        assert updated.prompt_text == "Updated text"
        assert updated.is_active is False
        assert updated.task_type == PromptTask.RESUME_TAILOR  # Unchanged

    async def test_update_partial_fields(self, db_session, test_user):
        """Test updating only specific fields."""
        prompt_data = PromptTemplateCreate(
            task_type=PromptTask.COVER_LETTER,
            name="Original",
            prompt_text="Original",
            role_type="engineer",
        )
        prompt = await PromptService.create_prompt_template(
            db_session, test_user.id, prompt_data
        )

        # Update only name
        update_data = PromptTemplateUpdate(name="New Name")
        updated = await PromptService.update_prompt_template(
            db_session, prompt.id, test_user.id, update_data
        )

        assert updated.name == "New Name"
        assert updated.prompt_text == "Original"  # Unchanged
        assert updated.role_type == "engineer"  # Unchanged

    async def test_delete_prompt_template(self, db_session, test_user):
        """Test soft deleting a prompt template."""
        prompt_data = PromptTemplateCreate(
            task_type=PromptTask.RESUME_TAILOR,
            name="To Delete",
            prompt_text="...",
        )
        prompt = await PromptService.create_prompt_template(
            db_session, test_user.id, prompt_data
        )

        # Delete prompt
        await PromptService.delete_prompt_template(
            db_session, prompt.id, test_user.id
        )

        # Verify it's deleted (soft delete)
        with pytest.raises(NotFoundError):
            await PromptService.get_prompt_template(
                db_session, prompt.id, test_user.id
            )


@pytest.mark.asyncio
class TestPromptTemplateList:
    """Test listing and filtering prompt templates."""

    async def test_list_empty(self, db_session, test_user):
        """Test listing prompts when none exist."""
        prompts = await PromptService.list_prompt_templates(
            db_session, test_user.id
        )

        assert prompts == []

    async def test_list_prompts(self, db_session, test_user):
        """Test listing all prompts for a user."""
        # Create multiple prompts
        for i in range(3):
            prompt_data = PromptTemplateCreate(
                task_type=PromptTask.RESUME_TAILOR,
                name=f"Template {i}",
                prompt_text=f"Text {i}",
            )
            await PromptService.create_prompt_template(
                db_session, test_user.id, prompt_data
            )

        prompts = await PromptService.list_prompt_templates(
            db_session, test_user.id
        )

        assert len(prompts) == 3

    async def test_list_filter_by_task_type(self, db_session, test_user):
        """Test filtering prompts by task type."""
        # Create prompts with different task types
        await PromptService.create_prompt_template(
            db_session,
            test_user.id,
            PromptTemplateCreate(
                task_type=PromptTask.RESUME_TAILOR,
                name="Resume",
                prompt_text="...",
            ),
        )
        await PromptService.create_prompt_template(
            db_session,
            test_user.id,
            PromptTemplateCreate(
                task_type=PromptTask.COVER_LETTER,
                name="Cover Letter",
                prompt_text="...",
            ),
        )

        # Filter by RESUME_TAILOR
        prompts = await PromptService.list_prompt_templates(
            db_session, test_user.id, task_type=PromptTask.RESUME_TAILOR
        )

        assert len(prompts) == 1
        assert prompts[0].task_type == PromptTask.RESUME_TAILOR

    async def test_list_filter_by_role_type(self, db_session, test_user):
        """Test filtering prompts by role type."""
        await PromptService.create_prompt_template(
            db_session,
            test_user.id,
            PromptTemplateCreate(
                task_type=PromptTask.RESUME_TAILOR,
                role_type="backend_engineer",
                name="Backend",
                prompt_text="...",
            ),
        )
        await PromptService.create_prompt_template(
            db_session,
            test_user.id,
            PromptTemplateCreate(
                task_type=PromptTask.RESUME_TAILOR,
                role_type="frontend_engineer",
                name="Frontend",
                prompt_text="...",
            ),
        )

        prompts = await PromptService.list_prompt_templates(
            db_session, test_user.id, role_type="backend_engineer"
        )

        assert len(prompts) == 1
        assert prompts[0].role_type == "backend_engineer"

    async def test_list_filter_by_active_status(self, db_session, test_user):
        """Test filtering prompts by active status."""
        # Create active prompt
        active = await PromptService.create_prompt_template(
            db_session,
            test_user.id,
            PromptTemplateCreate(
                task_type=PromptTask.RESUME_TAILOR,
                name="Active",
                prompt_text="...",
            ),
        )

        # Create inactive prompt
        inactive = await PromptService.create_prompt_template(
            db_session,
            test_user.id,
            PromptTemplateCreate(
                task_type=PromptTask.RESUME_TAILOR,
                name="Inactive",
                prompt_text="...",
            ),
        )
        await PromptService.update_prompt_template(
            db_session,
            inactive.id,
            test_user.id,
            PromptTemplateUpdate(is_active=False),
        )

        # Filter for active only
        prompts = await PromptService.list_prompt_templates(
            db_session, test_user.id, is_active=True
        )

        assert len(prompts) == 1
        assert prompts[0].is_active is True

    async def test_list_pagination(self, db_session, test_user):
        """Test pagination of prompt list."""
        # Create 5 prompts
        for i in range(5):
            await PromptService.create_prompt_template(
                db_session,
                test_user.id,
                PromptTemplateCreate(
                    task_type=PromptTask.RESUME_TAILOR,
                    name=f"Template {i}",
                    prompt_text="...",
                ),
            )

        # Get first 2
        page1 = await PromptService.list_prompt_templates(
            db_session, test_user.id, skip=0, limit=2
        )
        assert len(page1) == 2

        # Get next 2
        page2 = await PromptService.list_prompt_templates(
            db_session, test_user.id, skip=2, limit=2
        )
        assert len(page2) == 2

        # Verify different results
        assert page1[0].id != page2[0].id

    async def test_list_user_isolation(self, db_session, test_user, other_user):
        """Test users only see their own prompts."""
        # Create prompt for test_user
        await PromptService.create_prompt_template(
            db_session,
            test_user.id,
            PromptTemplateCreate(
                task_type=PromptTask.RESUME_TAILOR,
                name="Test User Template",
                prompt_text="...",
            ),
        )

        # Create prompt for other_user
        await PromptService.create_prompt_template(
            db_session,
            other_user.id,
            PromptTemplateCreate(
                task_type=PromptTask.RESUME_TAILOR,
                name="Other User Template",
                prompt_text="...",
            ),
        )

        # Each user should only see their own
        test_user_prompts = await PromptService.list_prompt_templates(
            db_session, test_user.id
        )
        other_user_prompts = await PromptService.list_prompt_templates(
            db_session, other_user.id
        )

        assert len(test_user_prompts) == 1
        assert len(other_user_prompts) == 1
        assert test_user_prompts[0].name == "Test User Template"
        assert other_user_prompts[0].name == "Other User Template"


@pytest.mark.asyncio
class TestPromptTemplateClone:
    """Test cloning/duplicating prompt templates."""

    async def test_duplicate_prompt(self, db_session, test_user):
        """Test duplicating a prompt template."""
        # Create original
        original = await PromptService.create_prompt_template(
            db_session,
            test_user.id,
            PromptTemplateCreate(
                task_type=PromptTask.RESUME_TAILOR,
                role_type="backend_engineer",
                name="Original",
                prompt_text="Original text",
            ),
        )

        # Duplicate with modifications
        clone_data = PromptTemplateClone(
            name="Cloned Version",
            prompt_text="Modified text",
            role_type="fullstack_engineer",
        )
        cloned = await PromptService.duplicate_prompt_template(
            db_session, original.id, test_user.id, clone_data
        )

        assert cloned.id != original.id
        assert cloned.name == "Cloned Version"
        assert cloned.prompt_text == "Modified text"
        assert cloned.role_type == "fullstack_engineer"
        assert cloned.task_type == original.task_type  # Inherited
        assert cloned.parent_template_id == original.id
        assert cloned.version == 1  # New version starts at 1

    async def test_duplicate_without_role_change(self, db_session, test_user):
        """Test duplicating without changing role_type."""
        original = await PromptService.create_prompt_template(
            db_session,
            test_user.id,
            PromptTemplateCreate(
                task_type=PromptTask.COVER_LETTER,
                role_type="engineer",
                name="Original",
                prompt_text="...",
            ),
        )

        clone_data = PromptTemplateClone(
            name="Clone",
            prompt_text="...",
            role_type=None,  # Keep original
        )
        cloned = await PromptService.duplicate_prompt_template(
            db_session, original.id, test_user.id, clone_data
        )

        assert cloned.role_type == "engineer"  # Inherited from original


@pytest.mark.asyncio
class TestPromptTemplateStats:
    """Test usage statistics tracking."""

    async def test_get_stats_new_prompt(self, db_session, test_user):
        """Test getting stats for a newly created prompt."""
        prompt = await PromptService.create_prompt_template(
            db_session,
            test_user.id,
            PromptTemplateCreate(
                task_type=PromptTask.RESUME_TAILOR,
                name="New Prompt",
                prompt_text="...",
            ),
        )

        stats = await PromptService.get_prompt_stats(
            db_session, prompt.id, test_user.id
        )

        assert stats["prompt_id"] == prompt.id
        assert stats["times_used"] == 0
        assert stats["avg_satisfaction_score"] is None

    async def test_increment_usage(self, db_session, test_user):
        """Test incrementing usage counter."""
        prompt = await PromptService.create_prompt_template(
            db_session,
            test_user.id,
            PromptTemplateCreate(
                task_type=PromptTask.COVER_LETTER,
                name="Test",
                prompt_text="...",
            ),
        )

        # Increment usage
        await PromptService.increment_usage(db_session, prompt.id)
        await db_session.refresh(prompt)

        assert prompt.times_used == 1

    async def test_increment_usage_with_satisfaction(self, db_session, test_user):
        """Test incrementing usage with satisfaction score."""
        prompt = await PromptService.create_prompt_template(
            db_session,
            test_user.id,
            PromptTemplateCreate(
                task_type=PromptTask.RESUME_TAILOR,
                name="Test",
                prompt_text="...",
            ),
        )

        # Add first rating
        await PromptService.increment_usage(
            db_session, prompt.id, satisfaction_score=4.0
        )
        await db_session.refresh(prompt)

        assert prompt.times_used == 1
        assert float(prompt.avg_satisfaction_score) == 4.0

        # Add second rating
        await PromptService.increment_usage(
            db_session, prompt.id, satisfaction_score=5.0
        )
        await db_session.refresh(prompt)

        assert prompt.times_used == 2
        assert float(prompt.avg_satisfaction_score) == 4.5  # (4 + 5) / 2

    async def test_increment_usage_nonexistent_prompt(self, db_session):
        """Test incrementing usage for non-existent prompt fails silently."""
        fake_id = uuid4()

        # Should not raise error
        await PromptService.increment_usage(db_session, fake_id)
