"""Unit tests for credential service."""

import pytest
from datetime import datetime
from uuid import uuid4

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.credential import Credential
from app.schemas.credential import CredentialCreate, CredentialUpdate
from app.services.credential_service import CredentialService


@pytest.fixture
async def user_id(test_user):
    return test_user.id


@pytest.fixture
async def other_user_id(other_user):
    return other_user.id


@pytest.mark.asyncio
async def test_create_credential(db_session, user_id):
    """Test creating a credential seamlessly encrypts password."""
    cred_data = CredentialCreate(
        platform="workday",
        username="testuser",
        password="TopSecretPassword123",
        additional_data={"url": "https://workday.com"}
    )
    
    credential = await CredentialService.create_credential(db_session, user_id, cred_data)
    
    assert credential.id is not None
    assert credential.user_id == user_id
    assert credential.platform == "workday"
    assert credential.username == "testuser"
    assert credential.additional_data == {"url": "https://workday.com"}
    assert credential.is_active is True
    assert credential.password_encrypted != "TopSecretPassword123".encode()
    
    # Test decryption internally
    from app.core.encryption import decrypt_password
    assert decrypt_password(credential.password_encrypted) == "TopSecretPassword123"


@pytest.mark.asyncio
async def test_get_credential(db_session, user_id):
    """Test getting credential by ID."""
    cred_data = CredentialCreate(
        platform="greenhouse", password="pwd"
    )
    credential = await CredentialService.create_credential(db_session, user_id, cred_data)
    
    fetched = await CredentialService.get_credential(db_session, credential.id, user_id)
    
    assert fetched.id == credential.id
    assert fetched.platform == "greenhouse"


@pytest.mark.asyncio
async def test_get_credential_not_found(db_session, user_id):
    """Test getting non-existent credential raises NotFoundError."""
    with pytest.raises(NotFoundError):
        await CredentialService.get_credential(db_session, uuid4(), user_id)


@pytest.mark.asyncio
async def test_get_credential_forbidden(db_session, user_id, other_user_id):
    """Test getting another user's credential raises ForbiddenError."""
    cred_data = CredentialCreate(
        platform="greenhouse", password="pwd"
    )
    credential = await CredentialService.create_credential(db_session, user_id, cred_data)
    
    with pytest.raises(ForbiddenError):
        await CredentialService.get_credential(db_session, credential.id, other_user_id)


@pytest.mark.asyncio
async def test_list_credentials(db_session, user_id):
    """Test listing credentials with filters."""
    # Create multiple credentials
    await CredentialService.create_credential(
        db_session, user_id, CredentialCreate(platform="workday", password="1")
    )
    await CredentialService.create_credential(
        db_session, user_id, CredentialCreate(platform="greenhouse", password="2")
    )
    
    # List all
    all_creds = await CredentialService.list_credentials(db_session, user_id)
    assert len(all_creds) >= 2
    
    # Filter by platform
    workday_creds = await CredentialService.list_credentials(db_session, user_id, platform="workday")
    assert len(workday_creds) == 1
    assert workday_creds[0].platform == "workday"


@pytest.mark.asyncio
async def test_update_credential(db_session, user_id):
    """Test updating a credential, focusing on password encryption."""
    credential = await CredentialService.create_credential(
        db_session, user_id, CredentialCreate(platform="workday", password="original")
    )
    
    update_data = CredentialUpdate(
        username="newuser",
        password="newpassword"
    )
    
    updated = await CredentialService.update_credential(db_session, credential.id, user_id, update_data)
    
    assert updated.username == "newuser"
    
    from app.core.encryption import decrypt_password
    assert decrypt_password(updated.password_encrypted) == "newpassword"


@pytest.mark.asyncio
async def test_delete_credential(db_session, user_id):
    """Test deleting a credential securely."""
    credential = await CredentialService.create_credential(
        db_session, user_id, CredentialCreate(platform="workday", password="del")
    )
    
    await CredentialService.delete_credential(db_session, credential.id, user_id)
    
    with pytest.raises(NotFoundError):
        await CredentialService.get_credential(db_session, credential.id, user_id)


@pytest.mark.asyncio
async def test_reveal_password(db_session, user_id):
    """Test revealing the plaintext password and updating last_used."""
    credential = await CredentialService.create_credential(
        db_session, user_id, CredentialCreate(platform="workday", password="RealPassword123")
    )
    
    assert credential.last_used is None
    
    revealed_password = await CredentialService.reveal_password(db_session, credential.id, user_id)
    
    assert revealed_password == "RealPassword123"
    assert credential.last_used is not None
    assert isinstance(credential.last_used, datetime)
