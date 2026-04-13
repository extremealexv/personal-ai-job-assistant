"""Service layer for credential management operations."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.encryption import encrypt_password, decrypt_password
from app.models.credential import Credential
from app.schemas.credential import CredentialCreate, CredentialUpdate


class CredentialService:
    """Service for encrypted credential management."""

    @staticmethod
    async def create_credential(
        db: AsyncSession, user_id: UUID, cred_data: CredentialCreate
    ) -> Credential:
        """
        Create a new encrypted credential.

        Args:
            db: Database session
            user_id: User ID for ownership
            cred_data: Credential creation data containing plaintext password

        Returns:
            Created credential (password is stored encrypted)
        """
        # Encrypt the password before storing
        encrypted_pwd = encrypt_password(cred_data.password)
        
        credential = Credential(
            user_id=user_id,
            platform=cred_data.platform,
            username=cred_data.username,
            password_encrypted=encrypted_pwd,
            additional_data=cred_data.additional_data,
            is_active=True,
        )

        db.add(credential)
        await db.commit()
        await db.refresh(credential)
        return credential

    @staticmethod
    async def get_credential(
        db: AsyncSession, cred_id: UUID, user_id: UUID
    ) -> Credential:
        """
        Get a credential by ID without revealing the password.

        Args:
            db: Database session
            cred_id: Credential ID
            user_id: User ID for authorization

        Returns:
            Credential model instance

        Raises:
            NotFoundError: If credential not found
            ForbiddenError: If user doesn't own the credential
        """
        stmt = select(Credential).where(Credential.id == cred_id)
        result = await db.execute(stmt)
        credential = result.scalar_one_or_none()

        if not credential:
            raise NotFoundError(f"Credential {cred_id} not found")

        if credential.user_id != user_id:
            raise ForbiddenError("Cannot access credential owned by another user")

        return credential

    @staticmethod
    async def list_credentials(
        db: AsyncSession,
        user_id: UUID,
        platform: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Credential]:
        """
        List credentials for a user with optional filters.

        Args:
            db: Database session
            user_id: User ID for authorization
            platform: Filter by platform name
            is_active: Filter by active status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of credentials
        """
        stmt = select(Credential).where(Credential.user_id == user_id)

        if platform is not None:
            stmt = stmt.where(Credential.platform == platform)
        if is_active is not None:
            stmt = stmt.where(Credential.is_active == is_active)

        # Pagination
        stmt = stmt.offset(skip).limit(limit)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_credential(
        db: AsyncSession,
        cred_id: UUID,
        user_id: UUID,
        cred_data: CredentialUpdate,
    ) -> Credential:
        """
        Update an existing credential.

        Args:
            db: Database session
            cred_id: Credential ID
            user_id: User ID for authorization
            cred_data: Update payload (password handled securely if provided)

        Returns:
            Updated credential instance
        """
        credential = await CredentialService.get_credential(db, cred_id, user_id)

        # Prepare update dictionary omitting None values
        update_data = cred_data.model_dump(exclude_unset=True)
        
        if "password" in update_data:
            # Re-encrypt if password is updated
            pwd = update_data.pop("password")
            if pwd is not None:
                credential.password_encrypted = encrypt_password(pwd)
            
        for field, value in update_data.items():
            setattr(credential, field, value)

        await db.commit()
        await db.refresh(credential)
        return credential

    @staticmethod
    async def delete_credential(
        db: AsyncSession, cred_id: UUID, user_id: UUID
    ) -> None:
        """
        Delete a credential permanently.

        Args:
            db: Database session
            cred_id: Credential ID
            user_id: User ID for authorization
        """
        credential = await CredentialService.get_credential(db, cred_id, user_id)

        await db.delete(credential)
        await db.commit()
        
    @staticmethod
    async def reveal_password(
        db: AsyncSession, cred_id: UUID, user_id: UUID
    ) -> str:
        """
        Get the decrypted password for a credential and update last_used.
        
        Args:
            db: Database session
            cred_id: Credential ID
            user_id: User ID for authorization
            
        Returns:
            Decrypted plaintext password
        """
        credential = await CredentialService.get_credential(db, cred_id, user_id)
        
        # Update last_used
        credential.last_used = datetime.now(timezone.utc)
        await db.commit()
        
        # Return decrypted
        return decrypt_password(credential.password_encrypted)
