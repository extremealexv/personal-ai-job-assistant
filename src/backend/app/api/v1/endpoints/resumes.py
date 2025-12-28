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
