"""Unit tests for cover letter service layer."""

import pytest
from uuid import uuid4

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.job import CoverLetter
from app.schemas.cover_letter import (
    CoverLetterCreate,
    CoverLetterSearchParams,
    CoverLetterUpdate,
)
from app.services import cover_letter_service


class TestCoverLetterServiceCRUD:
    """Tests for cover letter CRUD operations."""

    async def test_create_cover_letter(
        self, db_session, test_user, sample_application
    ):
        """Test creating a cover letter."""
        data = CoverLetterCreate(
            application_id=sample_application.id,
            content="Dear Hiring Manager,\n\nI am excited to apply for this position. With over 10 years of experience in software development, I believe I would be a great fit for your team and organization.",
            prompt_template_id=None,
            ai_model_used="gpt-4",
        )

        cover_letter = await cover_letter_service.create_cover_letter(
            db_session, test_user.id, data
        )

        assert cover_letter.id is not None
        assert cover_letter.application_id == sample_application.id
        assert cover_letter.content == data.content
        assert cover_letter.version_number == 1
        assert cover_letter.is_active is True  # First version should be active
        assert cover_letter.ai_model_used == "gpt-4"

    async def test_create_second_version_not_active(
        self, db_session, test_user, sample_cover_letter
    ):
        """Test that second version is not automatically active."""
        data = CoverLetterCreate(
            application_id=sample_cover_letter.application_id,
            content="Updated version of the cover letter with new information highlighting my recent achievements and relevant skills for this specific role.",
        )

        cover_letter = await cover_letter_service.create_cover_letter(
            db_session, test_user.id, data
        )

        assert cover_letter.version_number == 2
        assert cover_letter.is_active is False  # Should not auto-activate

    async def test_create_cover_letter_application_not_found(
        self, db_session, test_user
    ):
        """Test creating cover letter for non-existent application."""
        data = CoverLetterCreate(
            application_id=uuid4(),
            content="Dear Hiring Manager, I am writing to express my strong interest in this position and would like to discuss how my background aligns with your needs.",
        )

        with pytest.raises(NotFoundError, match="Application .* not found"):
            await cover_letter_service.create_cover_letter(
                db_session, test_user.id, data
            )

    async def test_create_cover_letter_wrong_user(
        self, db_session, sample_application
    ):
        """Test creating cover letter for another user's application."""
        wrong_user_id = uuid4()
        data = CoverLetterCreate(
            application_id=sample_application.id,
            content="Dear Hiring Manager, I am writing to express my strong interest in this position and would like to discuss how my background aligns with your needs.",
        )

        with pytest.raises(
            ForbiddenError, match="permission to create cover letters"
        ):
            await cover_letter_service.create_cover_letter(
                db_session, wrong_user_id, data
            )

    async def test_get_cover_letter_success(
        self, db_session, test_user, sample_cover_letter
    ):
        """Test getting a cover letter by ID."""
        cover_letter = await cover_letter_service.get_cover_letter(
            db_session, sample_cover_letter.id, test_user.id
        )

        assert cover_letter.id == sample_cover_letter.id
        assert cover_letter.content == sample_cover_letter.content

    async def test_get_cover_letter_not_found(self, db_session, test_user):
        """Test getting non-existent cover letter."""
        with pytest.raises(NotFoundError, match="Cover letter .* not found"):
            await cover_letter_service.get_cover_letter(
                db_session, uuid4(), test_user.id
            )

    async def test_get_cover_letter_wrong_user(
        self, db_session, sample_cover_letter
    ):
        """Test getting cover letter belonging to another user."""
        wrong_user_id = uuid4()

        with pytest.raises(
            ForbiddenError, match="permission to access this cover letter"
        ):
            await cover_letter_service.get_cover_letter(
                db_session, sample_cover_letter.id, wrong_user_id
            )

    async def test_update_cover_letter(
        self, db_session, test_user, sample_cover_letter
    ):
        """Test updating a cover letter."""
        update_data = CoverLetterUpdate(
            content="Updated cover letter content with new information highlighting my recent achievements, technical skills, and how they align with the company's mission."
        )

        cover_letter = await cover_letter_service.update_cover_letter(
            db_session, sample_cover_letter.id, test_user.id, update_data
        )

        assert cover_letter.content == update_data.content

    async def test_update_cover_letter_set_active(
        self, db_session, test_user, multiple_cover_letter_versions
    ):
        """Test setting a cover letter as active deactivates others."""
        # multiple_cover_letter_versions has version 1 active, version 2 inactive
        inactive_version = next(
            cl for cl in multiple_cover_letter_versions if not cl.is_active
        )

        update_data = CoverLetterUpdate(is_active=True)

        await cover_letter_service.update_cover_letter(
            db_session, inactive_version.id, test_user.id, update_data
        )

        # Refresh both versions
        await db_session.refresh(inactive_version)
        active_version = next(
            cl for cl in multiple_cover_letter_versions if cl.is_active
        )
        await db_session.refresh(active_version)

        assert inactive_version.is_active is True
        assert active_version.is_active is False

    async def test_delete_cover_letter(
        self, db_session, test_user, sample_cover_letter
    ):
        """Test deleting a cover letter."""
        await cover_letter_service.delete_cover_letter(
            db_session, sample_cover_letter.id, test_user.id
        )

        # Verify cover letter is deleted
        with pytest.raises(NotFoundError):
            await cover_letter_service.get_cover_letter(
                db_session, sample_cover_letter.id, test_user.id
            )


class TestCoverLetterServiceVersioning:
    """Tests for cover letter version management."""

    async def test_get_cover_letters_by_application(
        self, db_session, test_user, multiple_cover_letter_versions
    ):
        """Test getting all versions for an application."""
        application_id = multiple_cover_letter_versions[0].application_id

        cover_letters = await cover_letter_service.get_cover_letters_by_application(
            db_session, application_id, test_user.id
        )

        assert len(cover_letters) == 2
        # Should be ordered by version descending
        assert cover_letters[0].version_number == 2
        assert cover_letters[1].version_number == 1

    async def test_get_cover_letters_by_application_not_found(
        self, db_session, test_user
    ):
        """Test getting versions for non-existent application."""
        with pytest.raises(NotFoundError, match="Application .* not found"):
            await cover_letter_service.get_cover_letters_by_application(
                db_session, uuid4(), test_user.id
            )

    async def test_set_active_version(
        self, db_session, test_user, multiple_cover_letter_versions
    ):
        """Test activating a specific version."""
        application_id = multiple_cover_letter_versions[0].application_id

        # Activate version 2
        cover_letter = await cover_letter_service.set_active_version(
            db_session, application_id, 2, test_user.id
        )

        assert cover_letter.version_number == 2
        assert cover_letter.is_active is True

        # Check version 1 is deactivated
        version_1 = next(
            cl for cl in multiple_cover_letter_versions if cl.version_number == 1
        )
        await db_session.refresh(version_1)
        assert version_1.is_active is False

    async def test_set_active_version_not_found(self, db_session, test_user, sample_application):
        """Test activating non-existent version."""
        with pytest.raises(
            NotFoundError, match="Cover letter version .* not found"
        ):
            await cover_letter_service.set_active_version(
                db_session, sample_application.id, 99, test_user.id
            )


class TestCoverLetterServiceSearch:
    """Tests for searching and filtering cover letters."""

    async def test_get_user_cover_letters_all(
        self, db_session, test_user, multiple_cover_letter_versions
    ):
        """Test getting all cover letters for user."""
        params = CoverLetterSearchParams()

        cover_letters, total = await cover_letter_service.get_user_cover_letters(
            db_session, test_user.id, params
        )

        assert len(cover_letters) == 2
        assert total == 2

    async def test_get_user_cover_letters_pagination(
        self, db_session, test_user, multiple_cover_letter_versions
    ):
        """Test pagination of cover letters."""
        params = CoverLetterSearchParams(page=1, page_size=1)

        cover_letters, total = await cover_letter_service.get_user_cover_letters(
            db_session, test_user.id, params
        )

        assert len(cover_letters) == 1
        assert total == 2

    async def test_get_user_cover_letters_filter_by_application(
        self, db_session, test_user, multiple_cover_letter_versions
    ):
        """Test filtering by application."""
        application_id = multiple_cover_letter_versions[0].application_id

        params = CoverLetterSearchParams(application_id=application_id)

        cover_letters, total = await cover_letter_service.get_user_cover_letters(
            db_session, test_user.id, params
        )

        assert len(cover_letters) == 2
        assert all(cl.application_id == application_id for cl in cover_letters)

    async def test_get_user_cover_letters_filter_by_active(
        self, db_session, test_user, multiple_cover_letter_versions
    ):
        """Test filtering by active status."""
        params = CoverLetterSearchParams(is_active=True)

        cover_letters, total = await cover_letter_service.get_user_cover_letters(
            db_session, test_user.id, params
        )

        assert len(cover_letters) == 1
        assert cover_letters[0].is_active is True

    async def test_get_user_cover_letters_sort_by_version(
        self, db_session, test_user, multiple_cover_letter_versions
    ):
        """Test sorting by version number."""
        params = CoverLetterSearchParams(sort_by="version_number", sort_order="asc")

        cover_letters, total = await cover_letter_service.get_user_cover_letters(
            db_session, test_user.id, params
        )

        assert cover_letters[0].version_number < cover_letters[1].version_number
