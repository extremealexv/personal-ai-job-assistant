"""API endpoints for prompt template management."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.prompt import PromptTask
from app.models.user import User
from app.schemas.prompt import (
    PromptTemplateClone,
    PromptTemplateCreate,
    PromptTemplateResponse,
    PromptTemplateUpdate,
)
from app.services.prompt_service import PromptService

router = APIRouter()


@router.post("", response_model=PromptTemplateResponse, status_code=201)
async def create_prompt_template(
    prompt_data: PromptTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromptTemplateResponse:
    """
    Create a new prompt template.

    - **task_type**: Type of task (resume_tailor, cover_letter, form_answers, email_classification)
    - **role_type**: Optional role type (e.g., "backend_engineer", "data_scientist")
    - **name**: Template name (max 255 characters)
    - **prompt_text**: The actual prompt text
    - **is_system_prompt**: Whether this is a system-level prompt (default: false)

    Returns the created prompt template with ID and metadata.
    """
    prompt = await PromptService.create_prompt_template(
        db, current_user.id, prompt_data
    )
    return PromptTemplateResponse.model_validate(prompt)


@router.get("", response_model=list[PromptTemplateResponse])
async def list_prompt_templates(
    task_type: Optional[PromptTask] = Query(None, description="Filter by task type"),
    role_type: Optional[str] = Query(None, description="Filter by role type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PromptTemplateResponse]:
    """
    List prompt templates with optional filters.

    **Filters:**
    - **task_type**: Filter by task (resume_tailor, cover_letter, etc.)
    - **role_type**: Filter by role (e.g., "backend_engineer")
    - **is_active**: Filter by active status (true/false)
    - **skip**: Pagination offset (default: 0)
    - **limit**: Pagination limit (default: 100, max: 100)

    Returns list of prompt templates ordered by most recently updated.
    """
    prompts = await PromptService.list_prompt_templates(
        db,
        current_user.id,
        task_type=task_type,
        role_type=role_type,
        is_active=is_active,
        skip=skip,
        limit=limit,
    )
    return [PromptTemplateResponse.model_validate(p) for p in prompts]


@router.get("/{prompt_id}", response_model=PromptTemplateResponse)
async def get_prompt_template(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromptTemplateResponse:
    """
    Get a specific prompt template by ID.

    - **prompt_id**: UUID of the prompt template

    Returns:
    - Prompt template details

    Raises:
    - 404: Prompt template not found
    - 403: Cannot access prompt owned by another user
    """
    prompt = await PromptService.get_prompt_template(db, prompt_id, current_user.id)
    return PromptTemplateResponse.model_validate(prompt)


@router.put("/{prompt_id}", response_model=PromptTemplateResponse)
async def update_prompt_template(
    prompt_id: UUID,
    prompt_data: PromptTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromptTemplateResponse:
    """
    Update a prompt template.

    - **prompt_id**: UUID of the prompt template to update

    **Updatable fields:**
    - task_type
    - role_type
    - name
    - prompt_text
    - is_system_prompt
    - is_active

    Only provided fields will be updated. Returns updated prompt template.

    Raises:
    - 404: Prompt template not found
    - 403: Cannot update prompt owned by another user
    """
    prompt = await PromptService.update_prompt_template(
        db, prompt_id, current_user.id, prompt_data
    )
    return PromptTemplateResponse.model_validate(prompt)


@router.delete("/{prompt_id}", status_code=204)
async def delete_prompt_template(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a prompt template (soft delete).

    - **prompt_id**: UUID of the prompt template to delete

    The template is soft-deleted and can be recovered if needed.

    Raises:
    - 404: Prompt template not found
    - 403: Cannot delete prompt owned by another user
    """
    await PromptService.delete_prompt_template(db, prompt_id, current_user.id)


@router.post("/{prompt_id}/duplicate", response_model=PromptTemplateResponse, status_code=201)
async def duplicate_prompt_template(
    prompt_id: UUID,
    clone_data: PromptTemplateClone,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromptTemplateResponse:
    """
    Clone a prompt template with modifications.

    - **prompt_id**: UUID of the source prompt template
    - **name**: New name for the cloned template
    - **prompt_text**: Modified prompt text
    - **role_type**: Optional modified role type

    Creates a new prompt template based on the source, with specified modifications.
    The new template will reference the source as its parent.

    Useful for:
    - Creating variations of existing prompts
    - Adapting prompts for different roles
    - A/B testing prompt versions

    Raises:
    - 404: Source prompt template not found
    - 403: Cannot clone prompt owned by another user
    """
    prompt = await PromptService.duplicate_prompt_template(
        db, prompt_id, current_user.id, clone_data
    )
    return PromptTemplateResponse.model_validate(prompt)


@router.get("/{prompt_id}/stats", response_model=dict)
async def get_prompt_stats(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get usage statistics for a prompt template.

    - **prompt_id**: UUID of the prompt template

    Returns:
    - **times_used**: Number of times the prompt has been used
    - **avg_satisfaction_score**: Average user satisfaction rating (0-5)
    - **version**: Current version number
    - **is_active**: Active status
    - **created_at**: Creation timestamp
    - **updated_at**: Last update timestamp

    Useful for:
    - Evaluating prompt effectiveness
    - Comparing prompt performance
    - Identifying most popular prompts

    Raises:
    - 404: Prompt template not found
    - 403: Cannot access prompt owned by another user
    """
    stats = await PromptService.get_prompt_stats(db, prompt_id, current_user.id)
    return stats
