"""Prompt template schemas for API request/response models."""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.models.prompt import PromptTask
from app.schemas.base import BaseResponse, BaseSchema


class PromptTemplateBase(BaseSchema):
    """Base prompt template schema."""

    task_type: PromptTask
    role_type: Optional[str] = None
    name: str
    prompt_text: str
    is_system_prompt: bool = False


class PromptTemplateCreate(PromptTemplateBase):
    """Schema for creating a prompt template."""

    pass


class PromptTemplateUpdate(BaseSchema):
    """Schema for updating a prompt template."""

    task_type: Optional[PromptTask] = None
    role_type: Optional[str] = None
    name: Optional[str] = None
    prompt_text: Optional[str] = None
    is_system_prompt: Optional[bool] = None
    is_active: Optional[bool] = None


class PromptTemplateResponse(PromptTemplateBase, BaseResponse):
    """Schema for prompt template API responses."""

    user_id: UUID
    version: int
    is_active: bool
    parent_template_id: Optional[UUID] = None
    times_used: int
    avg_satisfaction_score: Optional[Decimal] = Field(None, ge=0, le=5)


class PromptTemplateClone(BaseSchema):
    """Schema for cloning a prompt template with modifications."""

    name: str
    prompt_text: str
    role_type: Optional[str] = None
