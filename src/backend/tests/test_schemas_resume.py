"""Tests for resume schemas."""

import pytest
from datetime import date
from uuid import uuid4

from pydantic import ValidationError

from app.schemas.resume import (
    WorkExperienceCreate,
    WorkExperienceResponse,
    EducationCreate,
    SkillCreate,
    CertificationCreate,
    MasterResumeCreate,
    MasterResumeResponse,
    ResumeVersionCreate,
)


@pytest.mark.unit
def test_work_experience_create_valid():
    """Test creating valid work experience."""
    exp = WorkExperienceCreate(
        company_name="TechCorp",
        job_title="Senior Engineer",
        employment_type="FULL_TIME",
        start_date=date(2020, 1, 1),
        is_current=True,
        description="Leading backend development",
        achievements=["Improved performance by 40%"],
        technologies=["Python", "FastAPI"],
    )
    
    assert exp.company_name == "TechCorp"
    assert exp.job_title == "Senior Engineer"
    assert exp.is_current is True
    assert len(exp.achievements) == 1
    assert len(exp.technologies) == 2


@pytest.mark.unit
def test_work_experience_missing_required_fields():
    """Test work experience fails without required fields."""
    with pytest.raises(ValidationError):
        WorkExperienceCreate(
            company_name="TechCorp",
            # Missing job_title and start_date
        )


@pytest.mark.unit
def test_work_experience_with_end_date():
    """Test work experience with end date."""
    exp = WorkExperienceCreate(
        company_name="OldCorp",
        job_title="Engineer",
        start_date=date(2018, 1, 1),
        end_date=date(2020, 12, 31),
        is_current=False,
    )
    
    assert exp.end_date == date(2020, 12, 31)
    assert exp.is_current is False


@pytest.mark.unit
def test_education_create_valid():
    """Test creating valid education."""
    edu = EducationCreate(
        institution="University of California",
        degree_type="BACHELOR",
        field_of_study="Computer Science",
        start_date=date(2012, 9, 1),
        end_date=date(2016, 5, 15),
        gpa=3.75,
    )
    
    assert edu.institution == "University of California"
    assert edu.degree_type == "BACHELOR"
    assert edu.field_of_study == "Computer Science"
    assert edu.gpa == 3.75


@pytest.mark.unit
def test_education_without_gpa():
    """Test education without GPA."""
    edu = EducationCreate(
        institution="University",
        degree_type="MASTER",
        field_of_study="Data Science",
    )
    
    assert edu.gpa is None


@pytest.mark.unit
def test_skill_create_valid():
    """Test creating valid skill."""
    skill = SkillCreate(
        skill_name="Python",
        category="PROGRAMMING_LANGUAGE",
        proficiency_level="Expert",
        years_of_experience=8,
    )
    
    assert skill.skill_name == "Python"
    assert skill.category == "PROGRAMMING_LANGUAGE"
    assert skill.years_of_experience == 8


@pytest.mark.unit
def test_skill_missing_required():
    """Test skill fails without skill name."""
    with pytest.raises(ValidationError):
        SkillCreate(category="PROGRAMMING_LANGUAGE")


@pytest.mark.unit
def test_certification_create_valid():
    """Test creating valid certification."""
    cert = CertificationCreate(
        certification_name="AWS Solutions Architect",
        issuing_organization="Amazon Web Services",
        issue_date=date(2023, 6, 15),
        expiration_date=date(2026, 6, 15),
        credential_id="AWS-12345",
    )
    
    assert cert.certification_name == "AWS Solutions Architect"
    assert cert.issuing_organization == "Amazon Web Services"
    assert cert.credential_id == "AWS-12345"


@pytest.mark.unit
def test_certification_without_expiration():
    """Test certification without expiration date."""
    cert = CertificationCreate(
        certification_name="Lifetime Certification",
        issuing_organization="Test Org",
    )
    
    assert cert.expiration_date is None


@pytest.mark.unit
def test_master_resume_create_valid():
    """Test creating valid master resume."""
    resume = MasterResumeCreate(
        full_name="John Doe",
        email="john@example.com",
        phone="+1234567890",
        summary="Experienced software engineer",
    )
    
    assert resume.full_name == "John Doe"
    assert resume.email == "john@example.com"
    assert resume.summary == "Experienced software engineer"


@pytest.mark.unit
def test_master_resume_invalid_email():
    """Test master resume fails with invalid email."""
    with pytest.raises(ValidationError):
        MasterResumeCreate(
            full_name="John Doe",
            email="invalid-email",
        )


@pytest.mark.unit
def test_resume_version_create_valid():
    """Test creating valid resume version."""
    version = ResumeVersionCreate(
        version_name="Backend Engineer - TechCorp",
        target_role="Backend Engineer",
        target_company="TechCorp",
        modifications={"summary": "Optimized for backend role"},
    )
    
    assert version.version_name == "Backend Engineer - TechCorp"
    assert version.target_role == "Backend Engineer"
    assert version.modifications["summary"] == "Optimized for backend role"


@pytest.mark.unit
def test_resume_version_missing_name():
    """Test resume version fails without name."""
    with pytest.raises(ValidationError):
        ResumeVersionCreate(target_role="Engineer")


@pytest.mark.unit
def test_work_experience_response():
    """Test work experience response schema."""
    exp = WorkExperienceResponse(
        id=uuid4(),
        master_resume_id=uuid4(),
        company_name="TechCorp",
        job_title="Engineer",
        start_date=date(2020, 1, 1),
        is_current=True,
    )
    
    assert exp.company_name == "TechCorp"
    assert isinstance(exp.id, type(uuid4()))


@pytest.mark.unit
def test_master_resume_response_with_relations():
    """Test master resume response with work experiences."""
    resume = MasterResumeResponse(
        id=uuid4(),
        user_id=uuid4(),
        full_name="John Doe",
        email="john@example.com",
        work_experiences=[],
        education=[],
        skills=[],
        certifications=[],
    )
    
    assert resume.full_name == "John Doe"
    assert isinstance(resume.work_experiences, list)
    assert isinstance(resume.skills, list)
