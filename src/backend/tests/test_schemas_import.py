"""Test that all schemas can be imported without errors."""

import pytest


@pytest.mark.unit
def test_import_user_schemas():
    """Test importing user schemas."""
    from app.schemas.user import (
        UserBase,
        UserCreate,
        UserUpdate,
        UserResponse,
        UserLogin,
    )
    
    assert UserBase is not None
    assert UserCreate is not None
    assert UserUpdate is not None
    assert UserResponse is not None
    assert UserLogin is not None


@pytest.mark.unit
def test_import_resume_schemas():
    """Test importing resume schemas."""
    from app.schemas.resume import (
        WorkExperienceBase,
        WorkExperienceCreate,
        WorkExperienceUpdate,
        WorkExperienceResponse,
        EducationBase,
        EducationCreate,
        SkillBase,
        SkillCreate,
        CertificationBase,
        CertificationCreate,
        MasterResumeBase,
        MasterResumeCreate,
        MasterResumeUpdate,
        MasterResumeResponse,
        ResumeVersionBase,
        ResumeVersionCreate,
        ResumeVersionUpdate,
        ResumeVersionResponse,
    )
    
    assert WorkExperienceBase is not None
    assert MasterResumeCreate is not None
    assert ResumeVersionResponse is not None


@pytest.mark.unit
def test_import_job_schemas():
    """Test importing job schemas."""
    from app.schemas.job import (
        JobPostingBase,
        JobPostingCreate,
        JobPostingUpdate,
        JobPostingResponse,
        ApplicationBase,
        ApplicationCreate,
        ApplicationUpdate,
        ApplicationResponse,
    )
    
    assert JobPostingBase is not None
    assert JobPostingCreate is not None
    assert ApplicationCreate is not None
    assert ApplicationResponse is not None


@pytest.mark.unit
def test_import_prompt_schemas():
    """Test importing prompt schemas."""
    from app.schemas.prompt import (
        PromptTemplateBase,
        PromptTemplateCreate,
        PromptTemplateUpdate,
        PromptTemplateResponse,
    )
    
    assert PromptTemplateBase is not None
    assert PromptTemplateCreate is not None


@pytest.mark.unit
def test_import_credential_schemas():
    """Test importing credential schemas."""
    from app.schemas.credential import (
        CredentialBase,
        CredentialCreate,
        CredentialUpdate,
        CredentialResponse,
    )
    
    assert CredentialBase is not None
    assert CredentialCreate is not None


@pytest.mark.unit
def test_import_email_schemas():
    """Test importing email schemas."""
    from app.schemas.email import (
        EmailThreadBase,
        EmailThreadCreate,
        EmailThreadUpdate,
        EmailThreadResponse,
    )
    
    assert EmailThreadBase is not None
    assert EmailThreadCreate is not None


@pytest.mark.unit
def test_import_analytics_schemas():
    """Test importing analytics schemas."""
    from app.schemas.analytics import (
        AnalyticsSnapshotBase,
        AnalyticsSnapshotCreate,
        AnalyticsSnapshotResponse,
    )
    
    assert AnalyticsSnapshotBase is not None
    assert AnalyticsSnapshotCreate is not None


@pytest.mark.unit
def test_import_base_schemas():
    """Test importing base schemas."""
    from app.schemas.base import BaseSchema, BaseResponse
    
    assert BaseSchema is not None
    assert BaseResponse is not None
