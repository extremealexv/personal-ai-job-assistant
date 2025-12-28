"""Resume management endpoints."""
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.resume import MasterResume
from app.models.user import User
from app.schemas.resume import MasterResumeResponse, ResumeUploadResponse
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
