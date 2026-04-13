"""API endpoints for secure credential management."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.credential import (
    CredentialCreate,
    CredentialResponse,
    CredentialUpdate,
)
from app.services.credential_service import CredentialService

router = APIRouter()


@router.post("", response_model=CredentialResponse, status_code=status.HTTP_201_CREATED)
async def create_credential(
    cred_data: CredentialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CredentialResponse:
    """
    Create a new encrypted credential.
    
    The plaintext password provided will be encrypted before storage.
    """
    credential = await CredentialService.create_credential(db, current_user.id, cred_data)
    return CredentialResponse.model_validate(credential)


@router.get("", response_model=list[CredentialResponse])
async def list_credentials(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CredentialResponse]:
    """
    List credentials. Passwords are not returned in the list.
    """
    credentials = await CredentialService.list_credentials(
        db, current_user.id, platform=platform, is_active=is_active, skip=skip, limit=limit
    )
    return [CredentialResponse.model_validate(c) for c in credentials]


@router.get("/{cred_id}", response_model=CredentialResponse)
async def get_credential(
    cred_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CredentialResponse:
    """
    Get credential details by ID. The password is not included in this response.
    """
    credential = await CredentialService.get_credential(db, cred_id, current_user.id)
    return CredentialResponse.model_validate(credential)


@router.get("/{cred_id}/reveal")
async def reveal_credential_password(
    cred_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Securely reveal the decrypted password for a given credential.
    
    This endpoint is intended for use by the browser extension during auto-fill.
    It updates the last_used timestamp on the credential.
    """
    password = await CredentialService.reveal_password(db, cred_id, current_user.id)
    return {"password": password}


@router.put("/{cred_id}", response_model=CredentialResponse)
async def update_credential(
    cred_id: UUID,
    cred_data: CredentialUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CredentialResponse:
    """
    Update a credential. If the password field is provided, it will be securely re-encrypted.
    """
    credential = await CredentialService.update_credential(
        db, cred_id, current_user.id, cred_data
    )
    return CredentialResponse.model_validate(credential)


@router.delete("/{cred_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credential(
    cred_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a credential.
    """
    await CredentialService.delete_credential(db, cred_id, current_user.id)
