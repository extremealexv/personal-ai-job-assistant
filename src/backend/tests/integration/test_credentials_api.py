"""Integration tests for the credentials API."""

import pytest
from httpx import AsyncClient
from typing import Any


@pytest.fixture
def credential_payload() -> dict[str, Any]:
    return {
        "platform": "Lever",
        "username": "testuser@example.com",
        "password": "MySecurePassword123"
    }


@pytest.mark.asyncio
async def test_create_credential_api(async_client: AsyncClient, auth_headers: dict[str, str], credential_payload: dict[str, Any]):
    """Test creating a new credential via API."""
    response = await async_client.post(
        "/api/v1/credentials",
        headers=auth_headers,
        json=credential_payload,
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["platform"] == "Lever"
    assert "password" not in data
    assert "password_encrypted" not in data


@pytest.mark.asyncio
async def test_reveal_credential_password_api(async_client: AsyncClient, auth_headers: dict[str, str], credential_payload: dict[str, Any]):
    """Test creating and then revealing a credential's password via API."""
    # 1. Create
    response = await async_client.post(
        "/api/v1/credentials",
        headers=auth_headers,
        json=credential_payload,
    )
    assert response.status_code == 201
    cred_id = response.json()["id"]
    
    # 2. Reveal
    reveal_response = await async_client.get(
        f"/api/v1/credentials/{cred_id}/reveal",
        headers=auth_headers,
    )
    
    assert reveal_response.status_code == 200
    reveal_data = reveal_response.json()
    assert "password" in reveal_data
    assert reveal_data["password"] == credential_payload["password"]


@pytest.mark.asyncio
async def test_list_credentials_api(async_client: AsyncClient, auth_headers: dict[str, str], credential_payload: dict[str, Any]):
    """Test list credentials API."""
    # Create two
    await async_client.post("/api/v1/credentials", headers=auth_headers, json=credential_payload)
    await async_client.post("/api/v1/credentials", headers=auth_headers, json={"platform": "Workday", "password": "abc"})
    
    response = await async_client.get(
        "/api/v1/credentials",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    # Ensure password is not leaked in lists
    assert "password" not in data[0]


@pytest.mark.asyncio
async def test_get_credential_api(async_client: AsyncClient, auth_headers: dict[str, str], credential_payload: dict[str, Any]):
    """Test get single credential."""
    create_resp = await async_client.post("/api/v1/credentials", headers=auth_headers, json=credential_payload)
    cred_id = create_resp.json()["id"]
    
    response = await async_client.get(
        f"/api/v1/credentials/{cred_id}",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == cred_id
    assert "password" not in data


@pytest.mark.asyncio
async def test_update_credential_api(async_client: AsyncClient, auth_headers: dict[str, str], credential_payload: dict[str, Any]):
    """Test updating a credential."""
    create_resp = await async_client.post("/api/v1/credentials", headers=auth_headers, json=credential_payload)
    cred_id = create_resp.json()["id"]
    
    update_resp = await async_client.put(
        f"/api/v1/credentials/{cred_id}",
        headers=auth_headers,
        json={"username": "updated@example.com"}
    )
    
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["username"] == "updated@example.com"
    
    # Update password
    await async_client.put(
        f"/api/v1/credentials/{cred_id}",
        headers=auth_headers,
        json={"password": "NewRevealedPassword"}
    )
    
    reveal_resp = await async_client.get(f"/api/v1/credentials/{cred_id}/reveal", headers=auth_headers)
    assert reveal_resp.json()["password"] == "NewRevealedPassword"


@pytest.mark.asyncio
async def test_delete_credential_api(async_client: AsyncClient, auth_headers: dict[str, str], credential_payload: dict[str, Any]):
    """Test deleting a credential."""
    create_resp = await async_client.post("/api/v1/credentials", headers=auth_headers, json=credential_payload)
    cred_id = create_resp.json()["id"]
    
    delete_resp = await async_client.delete(f"/api/v1/credentials/{cred_id}", headers=auth_headers)
    assert delete_resp.status_code == 204
    
    # Ensure it's deleted
    get_resp = await async_client.get(f"/api/v1/credentials/{cred_id}", headers=auth_headers)
    assert get_resp.status_code == 404
