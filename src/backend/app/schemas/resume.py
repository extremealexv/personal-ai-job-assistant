"""Resume schemas for API request/response models."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import Field

from app.models.resume import DegreeType, ExperienceType, SkillCategory
from app.schemas.base import BaseResponse, BaseSchema


# ============================================================================
# Master Resume
# ============================================================================


class MasterResumeBase(BaseSchema):
    """Base master resume schema."""

    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: Optional[str] = None


class MasterResumeCreate(MasterResumeBase):
    """Schema for creating a master resume."""

    original_filename: Optional[str] = None
    file_path: Optional[str] = None
    raw_text: Optional[str] = None


class MasterResumeUpdate(MasterResumeBase):
    """Schema for updating a master resume."""

    pass


class MasterResumeResponse(MasterResumeBase, BaseResponse):
    """Schema for master resume API responses."""

    user_id: UUID
    original_filename: Optional[str] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None


# ============================================================================
# Work Experience
# ============================================================================


class WorkExperienceBase(BaseSchema):
    """Base work experience schema."""

    company_name: str
    job_title: str
    employment_type: Optional[ExperienceType] = None
    location: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None
    achievements: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    display_order: int = 0


class WorkExperienceCreate(WorkExperienceBase):
    """Schema for creating work experience."""

    master_resume_id: UUID


class WorkExperienceUpdate(BaseSchema):
    """Schema for updating work experience."""

    company_name: Optional[str] = None
    job_title: Optional[str] = None
    employment_type: Optional[ExperienceType] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None
    achievements: Optional[list[str]] = None
    technologies: Optional[list[str]] = None
    display_order: Optional[int] = None


class WorkExperienceResponse(WorkExperienceBase, BaseResponse):
    """Schema for work experience API responses."""

    master_resume_id: UUID


# ============================================================================
# Education
# ============================================================================


class EducationBase(BaseSchema):
    """Base education schema."""

    institution: str
    degree_type: Optional[DegreeType] = None
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[Decimal] = Field(None, ge=0, le=4.0)
    honors: list[str] = Field(default_factory=list)
    activities: list[str] = Field(default_factory=list)
    display_order: int = 0


class EducationCreate(EducationBase):
    """Schema for creating education."""

    master_resume_id: UUID


class EducationUpdate(BaseSchema):
    """Schema for updating education."""

    institution: Optional[str] = None
    degree_type: Optional[DegreeType] = None
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[Decimal] = Field(None, ge=0, le=4.0)
    honors: Optional[list[str]] = None
    activities: Optional[list[str]] = None
    display_order: Optional[int] = None


class EducationResponse(EducationBase, BaseResponse):
    """Schema for education API responses."""

    master_resume_id: UUID


# ============================================================================
# Skill
# ============================================================================


class SkillBase(BaseSchema):
    """Base skill schema."""

    skill_name: str
    category: Optional[SkillCategory] = None
    proficiency_level: Optional[str] = None
    years_of_experience: Optional[int] = Field(None, ge=0)
    display_order: int = 0


class SkillCreate(SkillBase):
    """Schema for creating a skill."""

    master_resume_id: UUID


class SkillUpdate(BaseSchema):
    """Schema for updating a skill."""

    skill_name: Optional[str] = None
    category: Optional[SkillCategory] = None
    proficiency_level: Optional[str] = None
    years_of_experience: Optional[int] = Field(None, ge=0)
    display_order: Optional[int] = None


class SkillResponse(SkillBase, BaseResponse):
    """Schema for skill API responses."""

    master_resume_id: UUID


# ============================================================================
# Certification
# ============================================================================


class CertificationBase(BaseSchema):
    """Base certification schema."""

    certification_name: str
    issuing_organization: Optional[str] = None
    issue_date: Optional[date] = None
    expiration_date: Optional[date] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    display_order: int = 0


class CertificationCreate(CertificationBase):
    """Schema for creating a certification."""

    master_resume_id: UUID


class CertificationUpdate(BaseSchema):
    """Schema for updating a certification."""

    certification_name: Optional[str] = None
    issuing_organization: Optional[str] = None
    issue_date: Optional[date] = None
    expiration_date: Optional[date] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    display_order: Optional[int] = None


class CertificationResponse(CertificationBase, BaseResponse):
    """Schema for certification API responses."""

    master_resume_id: UUID


# ============================================================================
# Resume Version
# ============================================================================


class ResumeVersionBase(BaseSchema):
    """Base resume version schema."""

    version_name: str
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    modifications: Optional[dict[str, Any]] = Field(default_factory=dict)


class ResumeVersionCreate(ResumeVersionBase):
    """Schema for creating a resume version."""

    master_resume_id: UUID
    job_posting_id: Optional[UUID] = None
    prompt_template_id: Optional[UUID] = None
    ai_model_used: Optional[str] = None


class ResumeVersionUpdate(BaseSchema):
    """Schema for updating a resume version."""

    version_name: Optional[str] = None
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    modifications: Optional[dict[str, Any]] = None
    pdf_file_path: Optional[str] = None
    docx_file_path: Optional[str] = None


class ResumeVersionResponse(ResumeVersionBase, BaseResponse):
    """Schema for resume version API responses."""

    master_resume_id: UUID
    job_posting_id: Optional[UUID] = None
    prompt_template_id: Optional[UUID] = None
    ai_model_used: Optional[str] = None
    generation_timestamp: Optional[datetime] = None
    pdf_file_path: Optional[str] = None
    docx_file_path: Optional[str] = None
    times_used: int
    applications_count: int
    response_rate: Optional[Decimal] = None


# ============================================================================
# File Upload
# ============================================================================


class ResumeUploadResponse(BaseSchema):
    """Schema for resume upload response."""

    id: UUID
    filename: str
    file_size: int
    status: str = "processing"
    created_at: datetime


# ============================================================================
# List Responses (for CRUD endpoints)
# ============================================================================


class WorkExperienceListResponse(BaseSchema):
    """Schema for work experience list response."""

    items: list[WorkExperienceResponse]
    total: int


class EducationListResponse(BaseSchema):
    """Schema for education list response."""

    items: list[EducationResponse]
    total: int


class SkillListResponse(BaseSchema):
    """Schema for skill list response."""

    items: list[SkillResponse]
    total: int


class CertificationListResponse(BaseSchema):
    """Schema for certification list response."""

    items: list[CertificationResponse]
    total: int
