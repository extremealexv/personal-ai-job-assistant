"""Cover letter service layer - business logic for cover letter management."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.job import Application, CoverLetter
from app.schemas.cover_letter import (
    CoverLetterCreate,
    CoverLetterSearchParams,
    CoverLetterUpdate,
)


async def create_cover_letter(
    db: AsyncSession, user_id: UUID, data: CoverLetterCreate
) -> CoverLetter:
    """
    Create a new cover letter for an application.
    
    Args:
        db: Database session
        user_id: ID of the user creating the cover letter
        data: Cover letter creation data
        
    Returns:
        Created cover letter object
        
    Raises:
        NotFoundError: If application not found
        ForbiddenError: If application belongs to another user
    """
    # Verify application exists and belongs to user
    result = await db.execute(
        select(Application).where(Application.id == data.application_id)
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise NotFoundError(f"Application {data.application_id} not found")
    
    if application.user_id != user_id:
        raise ForbiddenError("You don't have permission to create cover letters for this application")
    
    # Get the next version number for this application
    version_result = await db.execute(
        select(func.max(CoverLetter.version_number))
        .where(CoverLetter.application_id == data.application_id)
    )
    max_version = version_result.scalar()
    next_version = (max_version or 0) + 1
    
    # If this is version 1, make it active. Otherwise, keep existing active version
    is_active = next_version == 1
    
    # Create cover letter
    cover_letter = CoverLetter(
        application_id=data.application_id,
        content=data.content,
        prompt_template_id=data.prompt_template_id,
        ai_model_used=data.ai_model_used,
        version_number=next_version,
        is_active=is_active,
        generation_timestamp=datetime.utcnow() if data.ai_model_used else None,
    )
    
    db.add(cover_letter)
    await db.commit()
    await db.refresh(cover_letter)
    
    return cover_letter


async def get_cover_letter(
    db: AsyncSession, cover_letter_id: UUID, user_id: UUID
) -> CoverLetter:
    """
    Get cover letter by ID with authorization check.
    
    Args:
        db: Database session
        cover_letter_id: Cover letter ID
        user_id: ID of the requesting user
        
    Returns:
        Cover letter object with eager-loaded application relationship
        
    Raises:
        NotFoundError: If cover letter not found
        ForbiddenError: If cover letter belongs to another user
    """
    result = await db.execute(
        select(CoverLetter)
        .options(joinedload(CoverLetter.application))
        .where(CoverLetter.id == cover_letter_id)
    )
    cover_letter = result.scalar_one_or_none()
    
    if not cover_letter:
        raise NotFoundError(f"Cover letter {cover_letter_id} not found")
    
    # Check if the application belongs to the user
    if cover_letter.application.user_id != user_id:
        raise ForbiddenError("You don't have permission to access this cover letter")
    
    return cover_letter


async def get_cover_letters_by_application(
    db: AsyncSession, application_id: UUID, user_id: UUID
) -> list[CoverLetter]:
    """
    Get all cover letter versions for an application.
    
    Args:
        db: Database session
        application_id: Application ID
        user_id: ID of the requesting user
        
    Returns:
        List of cover letters ordered by version number descending
        
    Raises:
        NotFoundError: If application not found
        ForbiddenError: If application belongs to another user
    """
    # Verify application exists and belongs to user
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise NotFoundError(f"Application {application_id} not found")
    
    if application.user_id != user_id:
        raise ForbiddenError("You don't have permission to access this application")
    
    # Get all cover letters for the application
    result = await db.execute(
        select(CoverLetter)
        .where(CoverLetter.application_id == application_id)
        .order_by(CoverLetter.version_number.desc())
    )
    
    return list(result.scalars().all())


async def get_user_cover_letters(
    db: AsyncSession, user_id: UUID, params: CoverLetterSearchParams
) -> tuple[list[CoverLetter], int]:
    """
    Get paginated and filtered cover letters for a user.
    
    Args:
        db: Database session
        user_id: ID of the requesting user
        params: Search and pagination parameters
        
    Returns:
        Tuple of (cover_letters list, total count)
    """
    # Build base query - join with application to filter by user
    query = (
        select(CoverLetter)
        .join(Application, CoverLetter.application_id == Application.id)
        .where(Application.user_id == user_id)
    )
    
    # Apply filters
    if params.application_id:
        query = query.where(CoverLetter.application_id == params.application_id)
    
    if params.is_active is not None:
        query = query.where(CoverLetter.is_active == params.is_active)
    
    if params.ai_model_used:
        query = query.where(CoverLetter.ai_model_used == params.ai_model_used)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply sorting
    sort_column = getattr(CoverLetter, params.sort_by)
    if params.sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Apply pagination
    offset = (params.page - 1) * params.page_size
    query = query.offset(offset).limit(params.page_size)
    
    # Execute query
    result = await db.execute(query)
    cover_letters = list(result.scalars().all())
    
    return cover_letters, total


async def update_cover_letter(
    db: AsyncSession, cover_letter_id: UUID, user_id: UUID, data: CoverLetterUpdate
) -> CoverLetter:
    """
    Update a cover letter.
    
    Args:
        db: Database session
        cover_letter_id: Cover letter ID
        user_id: ID of the requesting user
        data: Update data
        
    Returns:
        Updated cover letter object
        
    Raises:
        NotFoundError: If cover letter not found
        ForbiddenError: If cover letter belongs to another user
    """
    # Get cover letter with authorization check
    cover_letter = await get_cover_letter(db, cover_letter_id, user_id)
    
    # Update fields
    if data.content is not None:
        cover_letter.content = data.content
    
    if data.is_active is not None:
        # If setting this to active, deactivate other versions for same application
        if data.is_active:
            await db.execute(
                select(CoverLetter)
                .where(
                    and_(
                        CoverLetter.application_id == cover_letter.application_id,
                        CoverLetter.id != cover_letter_id,
                    )
                )
            )
            # Deactivate all other versions
            await db.execute(
                CoverLetter.__table__.update()
                .where(
                    and_(
                        CoverLetter.application_id == cover_letter.application_id,
                        CoverLetter.id != cover_letter_id,
                    )
                )
                .values(is_active=False)
            )
        
        cover_letter.is_active = data.is_active
    
    await db.commit()
    await db.refresh(cover_letter)
    
    return cover_letter


async def delete_cover_letter(
    db: AsyncSession, cover_letter_id: UUID, user_id: UUID
) -> None:
    """
    Delete a cover letter.
    
    Args:
        db: Database session
        cover_letter_id: Cover letter ID
        user_id: ID of the requesting user
        
    Raises:
        NotFoundError: If cover letter not found
        ForbiddenError: If cover letter belongs to another user
    """
    # Get cover letter with authorization check
    cover_letter = await get_cover_letter(db, cover_letter_id, user_id)
    
    await db.delete(cover_letter)
    await db.commit()


async def set_active_version(
    db: AsyncSession, application_id: UUID, version_number: int, user_id: UUID
) -> CoverLetter:
    """
    Set a specific version as the active cover letter for an application.
    
    Args:
        db: Database session
        application_id: Application ID
        version_number: Version number to activate
        user_id: ID of the requesting user
        
    Returns:
        Activated cover letter object
        
    Raises:
        NotFoundError: If application or version not found
        ForbiddenError: If application belongs to another user
    """
    # Verify application exists and belongs to user
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise NotFoundError(f"Application {application_id} not found")
    
    if application.user_id != user_id:
        raise ForbiddenError("You don't have permission to access this application")
    
    # Find the version
    result = await db.execute(
        select(CoverLetter).where(
            and_(
                CoverLetter.application_id == application_id,
                CoverLetter.version_number == version_number,
            )
        )
    )
    cover_letter = result.scalar_one_or_none()
    
    if not cover_letter:
        raise NotFoundError(
            f"Cover letter version {version_number} not found for application {application_id}"
        )
    
    # Deactivate all other versions
    await db.execute(
        CoverLetter.__table__.update()
        .where(
            and_(
                CoverLetter.application_id == application_id,
                CoverLetter.id != cover_letter.id,
            )
        )
        .values(is_active=False)
    )
    
    # Activate this version
    cover_letter.is_active = True
    
    await db.commit()
    await db.refresh(cover_letter)
    
    return cover_letter
