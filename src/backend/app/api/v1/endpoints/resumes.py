"""Resume management endpoints."""
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.resume import (
    Certification,
    Education,
    MasterResume,
    ResumeVersion,
    Skill,
    WorkExperience,
)
from app.models.user import User
from app.schemas.resume import (
    CertificationCreate,
    CertificationListResponse,
    CertificationResponse,
    CertificationUpdate,
    EducationCreate,
    EducationListResponse,
    EducationResponse,
    EducationUpdate,
    MasterResumeResponse,
    ResumeUploadResponse,
    ResumeVersionCreate,
    ResumeVersionListResponse,
    ResumeVersionResponse,
    ResumeVersionUpdate,
    SkillCreate,
    SkillListResponse,
    SkillResponse,
    SkillUpdate,
    WorkExperienceCreate,
    WorkExperienceListResponse,
    WorkExperienceResponse,
    WorkExperienceUpdate,
)
from app.utils.file_storage import FileStorage
from app.utils.file_validation import FileValidator
from app.utils.text_extraction import TextExtractor

router = APIRouter()


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload master resume",
    description="Upload a resume file (PDF or DOCX) for parsing and storage.",
)
async def upload_resume(
    file: Annotated[UploadFile, File(description="Resume file (PDF or DOCX, max 10MB)")],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeUploadResponse:
    """Upload and process a resume file.

    Args:
        file: The resume file to upload.
        db: Database session.
        current_user: Current authenticated user.

    Returns:
        Resume upload response with ID and status.

    Raises:
        HTTPException: If validation fails or processing error occurs.
    """
    # Validate file
    await FileValidator.validate_resume_file(file)

    # Check if user already has a master resume
    stmt = select(MasterResume).where(
        MasterResume.user_id == current_user.id,
        MasterResume.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    existing_resume = result.scalar_one_or_none()

    if existing_resume:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Master resume already exists. Please delete the existing one first.",
        )

    # Sanitize filename
    safe_filename = FileValidator.sanitize_filename(file.filename or "resume.pdf")
    unique_filename = FileStorage.generate_unique_filename(safe_filename)

    # Get upload directory for user
    upload_dir = FileStorage.get_upload_directory(str(current_user.id))

    # Save file
    file_path = await FileStorage.save_upload_file(file, upload_dir, unique_filename)

    # Extract text
    try:
        raw_text = await TextExtractor.extract_text(file_path)
    except Exception as e:
        # Clean up file if extraction fails
        await FileStorage.delete_file(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract text from resume: {str(e)}",
        ) from e

    # Create master resume record
    master_resume = MasterResume(
        user_id=current_user.id,
        original_filename=file.filename,
        file_path=str(file_path),
        file_size_bytes=file_path.stat().st_size,
        mime_type=file.content_type,
        raw_text=raw_text,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db.add(master_resume)
    await db.commit()
    await db.refresh(master_resume)

    return ResumeUploadResponse(
        id=master_resume.id,
        filename=file.filename or "unknown",
        file_size=master_resume.file_size_bytes or 0,
        status="completed",
        created_at=master_resume.created_at,
    )


@router.get(
    "/master",
    response_model=MasterResumeResponse,
    summary="Get master resume",
    description="Retrieve the user's master resume.",
)
async def get_master_resume(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MasterResumeResponse:
    """Get the user's master resume.

    Args:
        db: Database session.
        current_user: Current authenticated user.

    Returns:
        Master resume data.

    Raises:
        HTTPException: If no master resume exists.
    """
    stmt = select(MasterResume).where(
        MasterResume.user_id == current_user.id,
        MasterResume.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    master_resume = result.scalar_one_or_none()

    if not master_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No master resume found. Please upload a resume first.",
        )

    return MasterResumeResponse.model_validate(master_resume)


@router.delete(
    "/master",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete master resume",
    description="Soft delete the user's master resume and associated file.",
)
async def delete_master_resume(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete the user's master resume.

    Args:
        db: Database session.
        current_user: Current authenticated user.

    Raises:
        HTTPException: If no master resume exists.
    """
    stmt = select(MasterResume).where(
        MasterResume.user_id == current_user.id,
        MasterResume.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    master_resume = result.scalar_one_or_none()

    if not master_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No master resume found.",
        )

    # Soft delete the resume
    master_resume.deleted_at = datetime.now(timezone.utc)
    await db.commit()

    # Delete the physical file
    if master_resume.file_path:
        try:
            file_path = Path(master_resume.file_path)
            await FileStorage.delete_file(file_path)
        except Exception as e:
            # Log error but don't fail the request
            print(f"Error deleting file: {e}")


# ==============================================================================
# Work Experience Endpoints
# ==============================================================================


@router.get(
    "/work-experiences",
    response_model=WorkExperienceListResponse,
    summary="List work experiences",
    description="Get all work experiences for the user's master resume.",
)
async def list_work_experiences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkExperienceListResponse:
    """List all work experiences."""
    # Get master resume
    stmt = select(MasterResume).where(
        MasterResume.user_id == current_user.id,
        MasterResume.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    master_resume = result.scalar_one_or_none()

    if not master_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No master resume found. Please upload a resume first.",
        )

    # Get work experiences
    stmt = (
        select(WorkExperience)
        .where(WorkExperience.master_resume_id == master_resume.id)
        .order_by(WorkExperience.display_order, WorkExperience.start_date.desc())
    )
    result = await db.execute(stmt)
    experiences = result.scalars().all()

    return WorkExperienceListResponse(
        items=[WorkExperienceResponse.model_validate(exp) for exp in experiences],
        total=len(experiences),
    )


@router.post(
    "/work-experiences",
    response_model=WorkExperienceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create work experience",
    description="Add a new work experience to the master resume.",
)
async def create_work_experience(
    data: WorkExperienceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkExperienceResponse:
    """Create a new work experience."""
    # Verify master resume exists
    stmt = select(MasterResume).where(
        MasterResume.id == data.master_resume_id,
        MasterResume.user_id == current_user.id,
        MasterResume.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    master_resume = result.scalar_one_or_none()

    if not master_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master resume not found.",
        )

    # Create work experience
    work_exp = WorkExperience(
        master_resume_id=data.master_resume_id,
        company_name=data.company_name,
        job_title=data.job_title,
        employment_type=data.employment_type,
        location=data.location,
        start_date=data.start_date,
        end_date=data.end_date,
        is_current=data.is_current,
        description=data.description,
        achievements=data.achievements,
        technologies=data.technologies,
        display_order=data.display_order,
    )

    db.add(work_exp)
    await db.commit()
    await db.refresh(work_exp)

    return WorkExperienceResponse.model_validate(work_exp)


@router.put(
    "/work-experiences/{experience_id}",
    response_model=WorkExperienceResponse,
    summary="Update work experience",
    description="Update an existing work experience.",
)
async def update_work_experience(
    experience_id: UUID,
    data: WorkExperienceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkExperienceResponse:
    """Update a work experience."""
    # Get work experience
    stmt = (
        select(WorkExperience)
        .join(MasterResume)
        .where(
            WorkExperience.id == experience_id,
            MasterResume.user_id == current_user.id,
            MasterResume.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    work_exp = result.scalar_one_or_none()

    if not work_exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work experience not found.",
        )

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(work_exp, field, value)

    await db.commit()
    await db.refresh(work_exp)

    return WorkExperienceResponse.model_validate(work_exp)


@router.delete(
    "/work-experiences/{experience_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete work experience",
    description="Delete a work experience.",
)
async def delete_work_experience(
    experience_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a work experience."""
    # Get work experience
    stmt = (
        select(WorkExperience)
        .join(MasterResume)
        .where(
            WorkExperience.id == experience_id,
            MasterResume.user_id == current_user.id,
            MasterResume.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    work_exp = result.scalar_one_or_none()

    if not work_exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work experience not found.",
        )

    await db.delete(work_exp)
    await db.commit()


# ==============================================================================
# Education Endpoints
# ==============================================================================


@router.get(
    "/education",
    response_model=EducationListResponse,
    summary="List education",
    description="Get all education entries for the user's master resume.",
)
async def list_education(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EducationListResponse:
    """List all education entries."""
    # Get master resume
    stmt = select(MasterResume).where(
        MasterResume.user_id == current_user.id,
        MasterResume.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    master_resume = result.scalar_one_or_none()

    if not master_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No master resume found. Please upload a resume first.",
        )

    # Get education
    stmt = (
        select(Education)
        .where(Education.master_resume_id == master_resume.id)
        .order_by(Education.display_order, Education.end_date.desc())
    )
    result = await db.execute(stmt)
    education_list = result.scalars().all()

    return EducationListResponse(
        items=[EducationResponse.model_validate(edu) for edu in education_list],
        total=len(education_list),
    )


@router.post(
    "/education",
    response_model=EducationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create education",
    description="Add a new education entry to the master resume.",
)
async def create_education(
    data: EducationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EducationResponse:
    """Create a new education entry."""
    # Verify master resume exists
    stmt = select(MasterResume).where(
        MasterResume.id == data.master_resume_id,
        MasterResume.user_id == current_user.id,
        MasterResume.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    master_resume = result.scalar_one_or_none()

    if not master_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master resume not found.",
        )

    # Create education
    education = Education(
        master_resume_id=data.master_resume_id,
        institution=data.institution,
        degree_type=data.degree_type,
        field_of_study=data.field_of_study,
        location=data.location,
        start_date=data.start_date,
        end_date=data.end_date,
        gpa=data.gpa,
        honors=data.honors,
        activities=data.activities,
        display_order=data.display_order,
    )

    db.add(education)
    await db.commit()
    await db.refresh(education)

    return EducationResponse.model_validate(education)


@router.put(
    "/education/{education_id}",
    response_model=EducationResponse,
    summary="Update education",
    description="Update an existing education entry.",
)
async def update_education(
    education_id: UUID,
    data: EducationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EducationResponse:
    """Update an education entry."""
    # Get education
    stmt = (
        select(Education)
        .join(MasterResume)
        .where(
            Education.id == education_id,
            MasterResume.user_id == current_user.id,
            MasterResume.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    education = result.scalar_one_or_none()

    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education not found.",
        )

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(education, field, value)

    await db.commit()
    await db.refresh(education)

    return EducationResponse.model_validate(education)


@router.delete(
    "/education/{education_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete education",
    description="Delete an education entry.",
)
async def delete_education(
    education_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete an education entry."""
    # Get education
    stmt = (
        select(Education)
        .join(MasterResume)
        .where(
            Education.id == education_id,
            MasterResume.user_id == current_user.id,
            MasterResume.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    education = result.scalar_one_or_none()

    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education not found.",
        )

    await db.delete(education)
    await db.commit()


# ==============================================================================
# Skills Endpoints
# ==============================================================================


@router.get(
    "/skills",
    response_model=SkillListResponse,
    summary="List skills",
    description="Get all skills for the user's master resume.",
)
async def list_skills(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SkillListResponse:
    """List all skills."""
    # Get master resume
    stmt = select(MasterResume).where(
        MasterResume.user_id == current_user.id,
        MasterResume.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    master_resume = result.scalar_one_or_none()

    if not master_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No master resume found. Please upload a resume first.",
        )

    # Get skills
    stmt = (
        select(Skill)
        .where(Skill.master_resume_id == master_resume.id)
        .order_by(Skill.display_order, Skill.skill_name)
    )
    result = await db.execute(stmt)
    skills = result.scalars().all()

    return SkillListResponse(
        items=[SkillResponse.model_validate(skill) for skill in skills],
        total=len(skills),
    )


@router.post(
    "/skills",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create skill",
    description="Add a new skill to the master resume.",
)
async def create_skill(
    data: SkillCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SkillResponse:
    """Create a new skill."""
    # Verify master resume exists
    stmt = select(MasterResume).where(
        MasterResume.id == data.master_resume_id,
        MasterResume.user_id == current_user.id,
        MasterResume.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    master_resume = result.scalar_one_or_none()

    if not master_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master resume not found.",
        )

    # Create skill
    skill = Skill(
        master_resume_id=data.master_resume_id,
        skill_name=data.skill_name,
        category=data.category,
        proficiency_level=data.proficiency_level,
        years_of_experience=data.years_of_experience,
        display_order=data.display_order,
    )

    db.add(skill)
    await db.commit()
    await db.refresh(skill)

    return SkillResponse.model_validate(skill)


@router.put(
    "/skills/{skill_id}",
    response_model=SkillResponse,
    summary="Update skill",
    description="Update an existing skill.",
)
async def update_skill(
    skill_id: UUID,
    data: SkillUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SkillResponse:
    """Update a skill."""
    # Get skill
    stmt = (
        select(Skill)
        .join(MasterResume)
        .where(
            Skill.id == skill_id,
            MasterResume.user_id == current_user.id,
            MasterResume.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    skill = result.scalar_one_or_none()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found.",
        )

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(skill, field, value)

    await db.commit()
    await db.refresh(skill)

    return SkillResponse.model_validate(skill)


@router.delete(
    "/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete skill",
    description="Delete a skill.",
)
async def delete_skill(
    skill_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a skill."""
    # Get skill
    stmt = (
        select(Skill)
        .join(MasterResume)
        .where(
            Skill.id == skill_id,
            MasterResume.user_id == current_user.id,
            MasterResume.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    skill = result.scalar_one_or_none()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found.",
        )

    await db.delete(skill)
    await db.commit()


# ==============================================================================
# Certifications Endpoints
# ==============================================================================


@router.get(
    "/certifications",
    response_model=CertificationListResponse,
    summary="List certifications",
    description="Get all certifications for the user's master resume.",
)
async def list_certifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CertificationListResponse:
    """List all certifications."""
    # Get master resume
    stmt = select(MasterResume).where(
        MasterResume.user_id == current_user.id,
        MasterResume.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    master_resume = result.scalar_one_or_none()

    if not master_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No master resume found. Please upload a resume first.",
        )

    # Get certifications
    stmt = (
        select(Certification)
        .where(Certification.master_resume_id == master_resume.id)
        .order_by(Certification.display_order, Certification.issue_date.desc())
    )
    result = await db.execute(stmt)
    certifications = result.scalars().all()

    return CertificationListResponse(
        items=[CertificationResponse.model_validate(cert) for cert in certifications],
        total=len(certifications),
    )


@router.post(
    "/certifications",
    response_model=CertificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create certification",
    description="Add a new certification to the master resume.",
)
async def create_certification(
    data: CertificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CertificationResponse:
    """Create a new certification."""
    # Verify master resume exists
    stmt = select(MasterResume).where(
        MasterResume.id == data.master_resume_id,
        MasterResume.user_id == current_user.id,
        MasterResume.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    master_resume = result.scalar_one_or_none()

    if not master_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master resume not found.",
        )

    # Create certification
    certification = Certification(
        master_resume_id=data.master_resume_id,
        certification_name=data.certification_name,
        issuing_organization=data.issuing_organization,
        issue_date=data.issue_date,
        expiration_date=data.expiration_date,
        credential_id=data.credential_id,
        credential_url=data.credential_url,
        display_order=data.display_order,
    )

    db.add(certification)
    await db.commit()
    await db.refresh(certification)

    return CertificationResponse.model_validate(certification)


@router.put(
    "/certifications/{certification_id}",
    response_model=CertificationResponse,
    summary="Update certification",
    description="Update an existing certification.",
)
async def update_certification(
    certification_id: UUID,
    data: CertificationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CertificationResponse:
    """Update a certification."""
    # Get certification
    stmt = (
        select(Certification)
        .join(MasterResume)
        .where(
            Certification.id == certification_id,
            MasterResume.user_id == current_user.id,
            MasterResume.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    certification = result.scalar_one_or_none()

    if not certification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification not found.",
        )

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(certification, field, value)

    await db.commit()
    await db.refresh(certification)

    return CertificationResponse.model_validate(certification)


@router.delete(
    "/certifications/{certification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete certification",
    description="Delete a certification.",
)
async def delete_certification(
    certification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a certification."""
    # Get certification
    stmt = (
        select(Certification)
        .join(MasterResume)
        .where(
            Certification.id == certification_id,
            MasterResume.user_id == current_user.id,
            MasterResume.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    certification = result.scalar_one_or_none()

    if not certification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification not found.",
        )

    await db.delete(certification)
    await db.commit()


# ============================================================================
# Phase 3: Resume Versions
# ============================================================================


@router.post(
    "/versions",
    response_model=ResumeVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create resume version",
)
async def create_resume_version(
    version_data: ResumeVersionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeVersion:
    """Create a new tailored resume version."""
    # Verify master resume exists and user owns it
    stmt = select(MasterResume).where(
        MasterResume.id == version_data.master_resume_id,
        MasterResume.user_id == current_user.id,
        MasterResume.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    master_resume = result.scalar_one_or_none()

    if not master_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master resume not found.",
        )

    # Create resume version
    resume_version = ResumeVersion(
        master_resume_id=version_data.master_resume_id,
        job_posting_id=version_data.job_posting_id,
        version_name=version_data.version_name,
        target_role=version_data.target_role,
        target_company=version_data.target_company,
        modifications=version_data.modifications,
        prompt_template_id=version_data.prompt_template_id,
        ai_model_used=version_data.ai_model_used,
        generation_timestamp=datetime.now(timezone.utc),
    )

    db.add(resume_version)
    await db.commit()
    await db.refresh(resume_version)

    return resume_version


@router.get(
    "/versions",
    response_model=ResumeVersionListResponse,
    summary="List resume versions",
)
async def list_resume_versions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeVersionListResponse:
    """Get all resume versions for the user's master resume."""
    # Get user's master resume
    stmt_master = select(MasterResume).where(
        MasterResume.user_id == current_user.id,
        MasterResume.deleted_at.is_(None),
    )
    result_master = await db.execute(stmt_master)
    master_resume = result_master.scalar_one_or_none()

    if not master_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master resume not found.",
        )

    # Get all resume versions
    stmt = (
        select(ResumeVersion)
        .where(
            ResumeVersion.master_resume_id == master_resume.id,
            ResumeVersion.deleted_at.is_(None),
        )
        .order_by(ResumeVersion.created_at.desc())
    )
    result = await db.execute(stmt)
    versions = result.scalars().all()

    return ResumeVersionListResponse(
        items=list(versions),
        total=len(versions),
    )


@router.get(
    "/versions/{version_id}",
    response_model=ResumeVersionResponse,
    summary="Get resume version",
)
async def get_resume_version(
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeVersion:
    """Get a specific resume version by ID."""
    # Get version and verify ownership
    stmt = (
        select(ResumeVersion)
        .join(MasterResume)
        .where(
            ResumeVersion.id == version_id,
            MasterResume.user_id == current_user.id,
            ResumeVersion.deleted_at.is_(None),
            MasterResume.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    version = result.scalar_one_or_none()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume version not found.",
        )

    return version


@router.put(
    "/versions/{version_id}",
    response_model=ResumeVersionResponse,
    summary="Update resume version",
)
async def update_resume_version(
    version_id: UUID,
    version_data: ResumeVersionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeVersion:
    """Update a resume version."""
    # Get version and verify ownership
    stmt = (
        select(ResumeVersion)
        .join(MasterResume)
        .where(
            ResumeVersion.id == version_id,
            MasterResume.user_id == current_user.id,
            ResumeVersion.deleted_at.is_(None),
            MasterResume.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    version = result.scalar_one_or_none()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume version not found.",
        )

    # Update fields
    update_data = version_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(version, field, value)

    await db.commit()
    await db.refresh(version)

    return version


@router.delete(
    "/versions/{version_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete resume version",
)
async def delete_resume_version(
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a resume version (soft delete)."""
    # Get version and verify ownership
    stmt = (
        select(ResumeVersion)
        .join(MasterResume)
        .where(
            ResumeVersion.id == version_id,
            MasterResume.user_id == current_user.id,
            ResumeVersion.deleted_at.is_(None),
            MasterResume.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    version = result.scalar_one_or_none()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume version not found.",
        )

    # Soft delete
    version.deleted_at = datetime.now(timezone.utc)
    await db.commit()


@router.get(
    "/versions/job/{job_posting_id}",
    response_model=ResumeVersionListResponse,
    summary="Get resume versions for job posting",
)
async def get_resume_versions_for_job(
    job_posting_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeVersionListResponse:
    """Get all resume versions associated with a specific job posting."""
    # Get versions for this job
    stmt = (
        select(ResumeVersion)
        .join(MasterResume)
        .where(
            ResumeVersion.job_posting_id == job_posting_id,
            MasterResume.user_id == current_user.id,
            ResumeVersion.deleted_at.is_(None),
            MasterResume.deleted_at.is_(None),
        )
        .order_by(ResumeVersion.created_at.desc())
    )
    result = await db.execute(stmt)
    versions = result.scalars().all()

    return ResumeVersionListResponse(
        items=list(versions),
        total=len(versions),
    )


# ============================================================================
# Phase 4: Advanced Features
# ============================================================================


@router.get(
    "/search",
    response_model=dict,
    summary="Search resumes",
)
async def search_resumes(
    q: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Search across master resume and all structured data."""
    # Get user's master resume
    stmt_master = select(MasterResume).where(
        MasterResume.user_id == current_user.id,
        MasterResume.deleted_at.is_(None),
    )
    result_master = await db.execute(stmt_master)
    master_resume = result_master.scalar_one_or_none()

    if not master_resume:
        return {
            "master_resume": None,
            "work_experiences": [],
            "education": [],
            "skills": [],
            "certifications": [],
            "resume_versions": [],
            "total_results": 0,
        }

    search_term = f"%{q.lower()}%"
    results = {
        "master_resume": None,
        "work_experiences": [],
        "education": [],
        "skills": [],
        "certifications": [],
        "resume_versions": [],
        "total_results": 0,
    }

    # Search in master resume
    if (
        master_resume.full_name and q.lower() in master_resume.full_name.lower()
    ) or (master_resume.summary and q.lower() in master_resume.summary.lower()):
        results["master_resume"] = MasterResumeResponse.model_validate(master_resume)
        results["total_results"] += 1

    # Search work experiences
    stmt_work = (
        select(WorkExperience)
        .where(
            WorkExperience.master_resume_id == master_resume.id,
        )
        .where(
            (WorkExperience.company_name.ilike(search_term))
            | (WorkExperience.job_title.ilike(search_term))
            | (WorkExperience.description.ilike(search_term))
        )
    )
    result_work = await db.execute(stmt_work)
    work_matches = result_work.scalars().all()
    results["work_experiences"] = [
        WorkExperienceResponse.model_validate(w) for w in work_matches
    ]
    results["total_results"] += len(work_matches)

    # Search education
    stmt_edu = (
        select(Education)
        .where(
            Education.master_resume_id == master_resume.id,
        )
        .where(
            (Education.institution.ilike(search_term))
            | (Education.field_of_study.ilike(search_term))
        )
    )
    result_edu = await db.execute(stmt_edu)
    edu_matches = result_edu.scalars().all()
    results["education"] = [EducationResponse.model_validate(e) for e in edu_matches]
    results["total_results"] += len(edu_matches)

    # Search skills
    stmt_skill = (
        select(Skill)
        .where(
            Skill.master_resume_id == master_resume.id,
        )
        .where(Skill.skill_name.ilike(search_term))
    )
    result_skill = await db.execute(stmt_skill)
    skill_matches = result_skill.scalars().all()
    results["skills"] = [SkillResponse.model_validate(s) for s in skill_matches]
    results["total_results"] += len(skill_matches)

    # Search certifications
    stmt_cert = (
        select(Certification)
        .where(
            Certification.master_resume_id == master_resume.id,
        )
        .where(
            (Certification.certification_name.ilike(search_term))
            | (Certification.issuing_organization.ilike(search_term))
        )
    )
    result_cert = await db.execute(stmt_cert)
    cert_matches = result_cert.scalars().all()
    results["certifications"] = [
        CertificationResponse.model_validate(c) for c in cert_matches
    ]
    results["total_results"] += len(cert_matches)

    # Search resume versions
    stmt_version = (
        select(ResumeVersion)
        .where(
            ResumeVersion.master_resume_id == master_resume.id,
            ResumeVersion.deleted_at.is_(None),
        )
        .where(
            (ResumeVersion.version_name.ilike(search_term))
            | (ResumeVersion.target_role.ilike(search_term))
            | (ResumeVersion.target_company.ilike(search_term))
        )
    )
    result_version = await db.execute(stmt_version)
    version_matches = result_version.scalars().all()
    results["resume_versions"] = [
        ResumeVersionResponse.model_validate(v) for v in version_matches
    ]
    results["total_results"] += len(version_matches)

    return results


@router.get(
    "/stats",
    response_model=dict,
    summary="Get resume statistics",
)
async def get_resume_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get comprehensive statistics about resume data."""
    # Get user's master resume
    stmt_master = select(MasterResume).where(
        MasterResume.user_id == current_user.id,
        MasterResume.deleted_at.is_(None),
    )
    result_master = await db.execute(stmt_master)
    master_resume = result_master.scalar_one_or_none()

    if not master_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master resume not found.",
        )

    # Count structured data
    stmt_work = select(WorkExperience).where(
        WorkExperience.master_resume_id == master_resume.id
    )
    result_work = await db.execute(stmt_work)
    work_count = len(result_work.scalars().all())

    stmt_edu = select(Education).where(Education.master_resume_id == master_resume.id)
    result_edu = await db.execute(stmt_edu)
    edu_count = len(result_edu.scalars().all())

    stmt_skill = select(Skill).where(Skill.master_resume_id == master_resume.id)
    result_skill = await db.execute(stmt_skill)
    skill_count = len(result_skill.scalars().all())

    stmt_cert = select(Certification).where(
        Certification.master_resume_id == master_resume.id
    )
    result_cert = await db.execute(stmt_cert)
    cert_count = len(result_cert.scalars().all())

    # Count resume versions
    stmt_versions = select(ResumeVersion).where(
        ResumeVersion.master_resume_id == master_resume.id,
        ResumeVersion.deleted_at.is_(None),
    )
    result_versions = await db.execute(stmt_versions)
    versions = result_versions.scalars().all()
    version_count = len(versions)

    # Calculate version statistics
    total_times_used = sum(v.times_used for v in versions)
    total_applications = sum(v.applications_count for v in versions)
    avg_response_rate = (
        sum(
            float(v.response_rate) for v in versions if v.response_rate is not None
        )
        / len([v for v in versions if v.response_rate is not None])
        if any(v.response_rate is not None for v in versions)
        else 0.0
    )

    # Get most used version
    most_used_version = None
    if versions:
        most_used = max(versions, key=lambda v: v.times_used)
        if most_used.times_used > 0:
            most_used_version = {
                "id": str(most_used.id),
                "version_name": most_used.version_name,
                "times_used": most_used.times_used,
                "applications_count": most_used.applications_count,
                "response_rate": float(most_used.response_rate) if most_used.response_rate else None,
            }

    return {
        "master_resume_id": str(master_resume.id),
        "created_at": master_resume.created_at.isoformat(),
        "structured_data": {
            "work_experiences": work_count,
            "education": edu_count,
            "skills": skill_count,
            "certifications": cert_count,
        },
        "resume_versions": {
            "total_versions": version_count,
            "total_times_used": total_times_used,
            "total_applications": total_applications,
            "avg_response_rate": round(avg_response_rate, 2),
            "most_used_version": most_used_version,
        },
    }


@router.post(
    "/versions/{version_id}/duplicate",
    response_model=ResumeVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate resume version",
)
async def duplicate_resume_version(
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeVersion:
    """Create a copy of an existing resume version."""
    # Get original version and verify ownership
    stmt = (
        select(ResumeVersion)
        .join(MasterResume)
        .where(
            ResumeVersion.id == version_id,
            MasterResume.user_id == current_user.id,
            ResumeVersion.deleted_at.is_(None),
            MasterResume.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    original = result.scalar_one_or_none()

    if not original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume version not found.",
        )

    # Create duplicate
    duplicate = ResumeVersion(
        master_resume_id=original.master_resume_id,
        job_posting_id=None,  # Don't copy job posting link
        version_name=f"{original.version_name} (Copy)",
        target_role=original.target_role,
        target_company=original.target_company,
        modifications=original.modifications.copy() if original.modifications else {},
        prompt_template_id=original.prompt_template_id,
        ai_model_used=original.ai_model_used,
        generation_timestamp=datetime.now(timezone.utc),
        pdf_file_path=None,  # Don't copy file paths
        docx_file_path=None,
    )

    db.add(duplicate)
    await db.commit()
    await db.refresh(duplicate)

    return duplicate
