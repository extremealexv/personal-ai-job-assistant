"""Service layer for prompt template operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.prompt import PromptTask, PromptTemplate
from app.schemas.prompt import (
    PromptTemplateClone,
    PromptTemplateCreate,
    PromptTemplateUpdate,
)


class PromptService:
    """Service for prompt template management."""

    @staticmethod
    async def create_prompt_template(
        db: AsyncSession, user_id: UUID, prompt_data: PromptTemplateCreate
    ) -> PromptTemplate:
        """
        Create a new prompt template.

        Args:
            db: Database session
            user_id: User ID for ownership
            prompt_data: Prompt template data

        Returns:
            Created prompt template
        """
        prompt = PromptTemplate(
            user_id=user_id,
            task_type=prompt_data.task_type,
            role_type=prompt_data.role_type,
            name=prompt_data.name,
            prompt_text=prompt_data.prompt_text,
            is_system_prompt=prompt_data.is_system_prompt,
            version=1,
            is_active=True,
        )

        db.add(prompt)
        await db.commit()
        await db.refresh(prompt)
        return prompt

    @staticmethod
    async def get_prompt_template(
        db: AsyncSession, prompt_id: UUID, user_id: UUID
    ) -> PromptTemplate:
        """
        Get a prompt template by ID.

        Args:
            db: Database session
            prompt_id: Prompt template ID
            user_id: User ID for authorization

        Returns:
            Prompt template

        Raises:
            NotFoundError: If prompt not found
            ForbiddenError: If user doesn't own the prompt
        """
        stmt = select(PromptTemplate).where(
            and_(
                PromptTemplate.id == prompt_id,
                PromptTemplate.deleted_at.is_(None),
            )
        )
        result = await db.execute(stmt)
        prompt = result.scalar_one_or_none()

        if not prompt:
            raise NotFoundError(f"Prompt template {prompt_id} not found")

        if prompt.user_id != user_id:
            raise ForbiddenError("Cannot access prompt owned by another user")

        return prompt

    @staticmethod
    async def list_prompt_templates(
        db: AsyncSession,
        user_id: UUID,
        task_type: Optional[PromptTask] = None,
        role_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[PromptTemplate]:
        """
        List prompt templates with optional filters.

        Args:
            db: Database session
            user_id: User ID for authorization
            task_type: Filter by task type
            role_type: Filter by role type
            is_active: Filter by active status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of prompt templates
        """
        stmt = select(PromptTemplate).where(
            and_(
                PromptTemplate.user_id == user_id,
                PromptTemplate.deleted_at.is_(None),
            )
        )

        # Apply filters
        if task_type is not None:
            stmt = stmt.where(PromptTemplate.task_type == task_type)
        if role_type is not None:
            stmt = stmt.where(PromptTemplate.role_type == role_type)
        if is_active is not None:
            stmt = stmt.where(PromptTemplate.is_active == is_active)

        # Order by most recently updated, then by name
        stmt = stmt.order_by(desc(PromptTemplate.updated_at), PromptTemplate.name)

        # Pagination
        stmt = stmt.offset(skip).limit(limit)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_prompt_template(
        db: AsyncSession,
        prompt_id: UUID,
        user_id: UUID,
        prompt_data: PromptTemplateUpdate,
    ) -> PromptTemplate:
        """
        Update a prompt template.

        Args:
            db: Database session
            prompt_id: Prompt template ID
            user_id: User ID for authorization
            prompt_data: Updated prompt data

        Returns:
            Updated prompt template

        Raises:
            NotFoundError: If prompt not found
            ForbiddenError: If user doesn't own the prompt
        """
        prompt = await PromptService.get_prompt_template(db, prompt_id, user_id)

        # Update fields if provided
        update_data = prompt_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(prompt, field, value)

        await db.commit()
        await db.refresh(prompt)
        return prompt

    @staticmethod
    async def delete_prompt_template(
        db: AsyncSession, prompt_id: UUID, user_id: UUID
    ) -> None:
        """
        Delete (soft delete) a prompt template.

        Args:
            db: Database session
            prompt_id: Prompt template ID
            user_id: User ID for authorization

        Raises:
            NotFoundError: If prompt not found
            ForbiddenError: If user doesn't own the prompt
        """
        prompt = await PromptService.get_prompt_template(db, prompt_id, user_id)

        # Soft delete
        from datetime import datetime, timezone

        prompt.deleted_at = datetime.now(timezone.utc)

        await db.commit()

    @staticmethod
    async def duplicate_prompt_template(
        db: AsyncSession,
        prompt_id: UUID,
        user_id: UUID,
        clone_data: PromptTemplateClone,
    ) -> PromptTemplate:
        """
        Duplicate a prompt template with modifications.

        Args:
            db: Database session
            prompt_id: Source prompt template ID
            user_id: User ID for authorization
            clone_data: Modified data for the clone

        Returns:
            New cloned prompt template

        Raises:
            NotFoundError: If source prompt not found
            ForbiddenError: If user doesn't own the source prompt
        """
        # Get source template
        source = await PromptService.get_prompt_template(db, prompt_id, user_id)

        # Create new template with modified data
        new_prompt = PromptTemplate(
            user_id=user_id,
            task_type=source.task_type,
            role_type=clone_data.role_type
            if clone_data.role_type is not None
            else source.role_type,
            name=clone_data.name,
            prompt_text=clone_data.prompt_text,
            is_system_prompt=source.is_system_prompt,
            version=1,
            is_active=True,
            parent_template_id=prompt_id,  # Link to parent
        )

        db.add(new_prompt)
        await db.commit()
        await db.refresh(new_prompt)
        return new_prompt

    @staticmethod
    async def get_prompt_stats(
        db: AsyncSession, prompt_id: UUID, user_id: UUID
    ) -> dict:
        """
        Get usage statistics for a prompt template.

        Args:
            db: Database session
            prompt_id: Prompt template ID
            user_id: User ID for authorization

        Returns:
            Dictionary with usage statistics

        Raises:
            NotFoundError: If prompt not found
            ForbiddenError: If user doesn't own the prompt
        """
        prompt = await PromptService.get_prompt_template(db, prompt_id, user_id)

        return {
            "prompt_id": prompt.id,
            "name": prompt.name,
            "task_type": prompt.task_type,
            "role_type": prompt.role_type,
            "times_used": prompt.times_used,
            "avg_satisfaction_score": (
                float(prompt.avg_satisfaction_score)
                if prompt.avg_satisfaction_score
                else None
            ),
            "version": prompt.version,
            "is_active": prompt.is_active,
            "created_at": prompt.created_at,
            "updated_at": prompt.updated_at,
        }

    @staticmethod
    async def increment_usage(
        db: AsyncSession, prompt_id: UUID, satisfaction_score: Optional[float] = None
    ) -> None:
        """
        Increment usage counter and optionally update satisfaction score.

        Args:
            db: Database session
            prompt_id: Prompt template ID
            satisfaction_score: Optional satisfaction rating (0-5)
        """
        stmt = select(PromptTemplate).where(PromptTemplate.id == prompt_id)
        result = await db.execute(stmt)
        prompt = result.scalar_one_or_none()

        if not prompt:
            return  # Silently fail if prompt not found

        prompt.times_used += 1

        # Update average satisfaction score if provided
        if satisfaction_score is not None:
            if prompt.avg_satisfaction_score is None:
                prompt.avg_satisfaction_score = satisfaction_score
            else:
                # Calculate new average
                total = (
                    float(prompt.avg_satisfaction_score) * (prompt.times_used - 1)
                    + satisfaction_score
                )
                prompt.avg_satisfaction_score = total / prompt.times_used

        await db.commit()
