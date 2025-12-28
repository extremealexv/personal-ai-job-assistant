"""Pydantic schemas for API request/response models."""

from app.schemas.analytics import (
    AnalyticsSnapshotCreate,
    AnalyticsSnapshotResponse,
    AnalyticsSnapshotUpdate,
    InterviewEventCreate,
    InterviewEventResponse,
    InterviewEventUpdate,
)
from app.schemas.credential import (
    CredentialCreate,
    CredentialResponse,
    CredentialUpdate,
)
from app.schemas.email import EmailThreadCreate, EmailThreadResponse
from app.schemas.job import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
    CoverLetterCreate,
    CoverLetterResponse,
    CoverLetterUpdate,
    JobPostingCreate,
    JobPostingResponse,
    JobPostingUpdate,
)
from app.schemas.prompt import (
    PromptTemplateCreate,
    PromptTemplateResponse,
    PromptTemplateUpdate,
)
from app.schemas.resume import (
    CertificationCreate,
    CertificationResponse,
    CertificationUpdate,
    EducationCreate,
    EducationResponse,
    EducationUpdate,
    MasterResumeCreate,
    MasterResumeResponse,
    MasterResumeUpdate,
    ResumeVersionCreate,
    ResumeVersionResponse,
    ResumeVersionUpdate,
    SkillCreate,
    SkillResponse,
    SkillUpdate,
    WorkExperienceCreate,
    WorkExperienceResponse,
    WorkExperienceUpdate,
)
from app.schemas.user import UserCreate, UserResponse, UserUpdate

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    # Resume
    "MasterResumeCreate",
    "MasterResumeUpdate",
    "MasterResumeResponse",
    "WorkExperienceCreate",
    "WorkExperienceUpdate",
    "WorkExperienceResponse",
    "EducationCreate",
    "EducationUpdate",
    "EducationResponse",
    "SkillCreate",
    "SkillUpdate",
    "SkillResponse",
    "CertificationCreate",
    "CertificationUpdate",
    "CertificationResponse",
    "ResumeVersionCreate",
    "ResumeVersionUpdate",
    "ResumeVersionResponse",
    # Job
    "JobPostingCreate",
    "JobPostingUpdate",
    "JobPostingResponse",
    "ApplicationCreate",
    "ApplicationUpdate",
    "ApplicationResponse",
    "CoverLetterCreate",
    "CoverLetterUpdate",
    "CoverLetterResponse",
    # Prompt
    "PromptTemplateCreate",
    "PromptTemplateUpdate",
    "PromptTemplateResponse",
    # Credential
    "CredentialCreate",
    "CredentialUpdate",
    "CredentialResponse",
    # Email
    "EmailThreadCreate",
    "EmailThreadResponse",
    # Analytics
    "InterviewEventCreate",
    "InterviewEventUpdate",
    "InterviewEventResponse",
    "AnalyticsSnapshotCreate",
    "AnalyticsSnapshotUpdate",
    "AnalyticsSnapshotResponse",
]
