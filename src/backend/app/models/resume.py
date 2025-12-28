"""Resume-related models."""

import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.job import JobPosting, Application
    from app.models.prompt import PromptTemplate


class ExperienceType(str, enum.Enum):
    """Employment type enumeration."""

    FULL_TIME = "full_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"


class DegreeType(str, enum.Enum):
    """Degree type enumeration."""

    HIGH_SCHOOL = "high_school"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    DOCTORATE = "doctorate"
    PROFESSIONAL = "professional"
    CERTIFICATE = "certificate"
    BOOTCAMP = "bootcamp"


class SkillCategory(str, enum.Enum):
    """Skill category enumeration."""

    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    TOOL = "tool"
    SOFT_SKILL = "soft_skill"
    CERTIFICATION = "certification"
    OTHER = "other"


class MasterResume(Base):
    """Master resume - canonical parsed resume data."""

    __tablename__ = "master_resumes"

    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Original file metadata
    original_filename: Mapped[Optional[str]] = mapped_column(String(500))
    file_path: Mapped[Optional[str]] = mapped_column(String(1000))
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))

    # Parsed content
    raw_text: Mapped[Optional[str]] = mapped_column(Text)

    # Personal information (structured)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))
    github_url: Mapped[Optional[str]] = mapped_column(String(500))
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(500))
    summary: Mapped[Optional[str]] = mapped_column(Text)

    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="master_resumes")
    work_experiences: Mapped[list["WorkExperience"]] = relationship(
        back_populates="master_resume",
        cascade="all, delete-orphan",
        order_by="WorkExperience.display_order",
    )
    education: Mapped[list["Education"]] = relationship(
        back_populates="master_resume", cascade="all, delete-orphan"
    )
    skills: Mapped[list["Skill"]] = relationship(
        back_populates="master_resume", cascade="all, delete-orphan"
    )
    certifications: Mapped[list["Certification"]] = relationship(
        back_populates="master_resume", cascade="all, delete-orphan"
    )
    resume_versions: Mapped[list["ResumeVersion"]] = relationship(
        back_populates="master_resume", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<MasterResume(name={self.full_name}, user_id={self.user_id})>"


class WorkExperience(Base):
    """Work experience entry from master resume."""

    __tablename__ = "work_experiences"

    # Foreign keys
    master_resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("master_resumes.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Job details
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    employment_type: Mapped[Optional[ExperienceType]] = mapped_column(
        Enum(ExperienceType, name="experience_type", values_callable=lambda x: [e.value for e in x])
    )
    location: Mapped[Optional[str]] = mapped_column(String(255))

    # Dates
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Content
    description: Mapped[Optional[str]] = mapped_column(Text)
    achievements: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    technologies: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))

    # Ordering
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    master_resume: Mapped["MasterResume"] = relationship(back_populates="work_experiences")

    def __repr__(self) -> str:
        return f"<WorkExperience(company={self.company_name}, title={self.job_title})>"


class Education(Base):
    """Education entry from master resume."""

    __tablename__ = "education"

    # Foreign keys
    master_resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("master_resumes.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Education details
    institution: Mapped[str] = mapped_column(String(255), nullable=False)
    degree_type: Mapped[Optional[DegreeType]] = mapped_column(
        Enum(DegreeType, name="degree_type", values_callable=lambda x: [e.value for e in x])
    )
    field_of_study: Mapped[Optional[str]] = mapped_column(String(255))
    location: Mapped[Optional[str]] = mapped_column(String(255))

    # Dates
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    gpa: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2))

    # Additional info
    honors: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    activities: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))

    # Ordering
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    master_resume: Mapped["MasterResume"] = relationship(back_populates="education")

    def __repr__(self) -> str:
        return f"<Education(institution={self.institution}, degree={self.degree_type})>"


class Skill(Base):
    """Skill from master resume."""

    __tablename__ = "skills"

    # Foreign keys
    master_resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("master_resumes.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Skill details
    skill_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[Optional[SkillCategory]] = mapped_column(
        Enum(SkillCategory, name="skill_category", values_callable=lambda x: [e.value for e in x])
    )
    proficiency_level: Mapped[Optional[str]] = mapped_column(String(50))
    years_of_experience: Mapped[Optional[int]] = mapped_column(Integer)

    # Ordering
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    master_resume: Mapped["MasterResume"] = relationship(back_populates="skills")

    def __repr__(self) -> str:
        return f"<Skill(name={self.skill_name}, category={self.category})>"


class Certification(Base):
    """Professional certification from master resume."""

    __tablename__ = "certifications"

    # Foreign keys
    master_resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("master_resumes.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Certification details
    certification_name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuing_organization: Mapped[Optional[str]] = mapped_column(String(255))
    issue_date: Mapped[Optional[date]] = mapped_column(Date)
    expiration_date: Mapped[Optional[date]] = mapped_column(Date)
    credential_id: Mapped[Optional[str]] = mapped_column(String(255))
    credential_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Ordering
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    master_resume: Mapped["MasterResume"] = relationship(back_populates="certifications")

    def __repr__(self) -> str:
        return f"<Certification(name={self.certification_name})>"


class ResumeVersion(Base):
    """Tailored resume version for specific job."""

    __tablename__ = "resume_versions"

    # Foreign keys
    master_resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("master_resumes.id", ondelete="CASCADE"),
        nullable=False,
    )
    job_posting_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_postings.id", ondelete="SET NULL")
    )

    # Version metadata
    version_name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_role: Mapped[Optional[str]] = mapped_column(String(255))
    target_company: Mapped[Optional[str]] = mapped_column(String(255))

    # Modifications (stored as JSONB for flexibility)
    modifications: Mapped[Optional[dict]] = mapped_column(JSONB)

    # AI generation metadata
    prompt_template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prompt_templates.id", ondelete="SET NULL")
    )
    ai_model_used: Mapped[Optional[str]] = mapped_column(String(100))
    generation_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Generated files
    pdf_file_path: Mapped[Optional[str]] = mapped_column(String(1000))
    docx_file_path: Mapped[Optional[str]] = mapped_column(String(1000))

    # Usage statistics
    times_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    applications_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    response_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    master_resume: Mapped["MasterResume"] = relationship(back_populates="resume_versions")
    job_posting: Mapped[Optional["JobPosting"]] = relationship(
        back_populates="resume_versions"
    )
    prompt_template: Mapped[Optional["PromptTemplate"]] = relationship(
        back_populates="resume_versions"
    )
    applications: Mapped[list["Application"]] = relationship(back_populates="resume_version")

    def __repr__(self) -> str:
        return f"<ResumeVersion(name={self.version_name}, job={self.target_company})>"
