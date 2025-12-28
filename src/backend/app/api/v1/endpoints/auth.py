"""Authentication endpoints for user registration, login, and token management."""
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.deps import get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.db import get_db
from app.models.user import User
from app.schemas.auth import (
    LogoutRequest,
    PasswordChange,
    TokenRefresh,
    TokenResponse,
    UserLogin,
    UserRegister,
)
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Register a new user account.
    
    **Requirements:**
    - Valid email address
    - Password meeting strength requirements (8+ chars, upper/lower/number/special)
    - Full name
    
    **Returns:**
    - Created user object (without password)
    
    **Errors:**
    - 409: Email already registered
    - 422: Validation error (weak password, invalid email)
    """
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email, User.deleted_at.is_(None))
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        email_verified=False,
    )
    
    db.add(user)
    
    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate user and return access/refresh tokens.
    
    **Requirements:**
    - Valid email and password
    - Account must be active
    - Account not locked due to failed attempts
    
    **Returns:**
    - Access token (30 min expiration)
    - Refresh token (7 day expiration)
    
    **Errors:**
    - 401: Invalid credentials
    - 423: Account locked (too many failed attempts)
    """
    # Get user
    result = await db.execute(
        select(User).where(User.email == credentials.email, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    
    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        minutes_left = int((user.locked_until - datetime.utcnow()).total_seconds() / 60)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked due to too many failed attempts. Try again in {minutes_left} minutes.",
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        # Increment failed login attempts
        await db.execute(
            update(User)
            .where(User.id == user.id)
            .values(failed_login_attempts=User.failed_login_attempts + 1)
        )
        
        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 4:  # Will be 5 after this attempt
            lock_until = datetime.utcnow() + timedelta(minutes=15)
            await db.execute(
                update(User)
                .where(User.id == user.id)
                .values(locked_until=lock_until)
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account locked due to too many failed attempts. Try again in 15 minutes.",
            )
        
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    
    # Reset failed login attempts and update last login
    await db.execute(
        update(User)
        .where(User.id == user.id)
        .values(
            failed_login_attempts=0,
            locked_until=None,
            last_login=datetime.utcnow(),
        )
    )
    await db.commit()
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": str(user.id)}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Refresh access token using refresh token.
    
    **Requirements:**
    - Valid refresh token
    
    **Returns:**
    - New access token (30 min expiration)
    - Same refresh token (reusable until expiration)
    
    **Errors:**
    - 401: Invalid or expired refresh token
    """
    # Verify refresh token
    payload = verify_token(token_data.refresh_token, token_type="refresh")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    email = payload.get("sub")
    user_id = payload.get("user_id")
    
    if not email or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    # Verify user still exists and is active
    result = await db.execute(
        select(User).where(User.email == email, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Create new access token
    access_token = create_access_token(
        data={"sub": email, "user_id": user_id}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=token_data.refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current authenticated user's profile.
    
    **Requires:** Valid access token
    
    **Returns:**
    - Current user object (without password)
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: Annotated[dict, Depends()],
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Update current user's profile.
    
    **Requires:** Valid access token
    
    **Allowed fields:**
    - full_name
    - phone
    - location
    - linkedin_url
    - github_url
    - portfolio_url
    
    **Returns:**
    - Updated user object
    """
    # TODO: Implement profile update logic
    # This is a placeholder for future implementation
    return current_user


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChange,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Change current user's password.
    
    **Requires:** Valid access token
    
    **Requirements:**
    - Current password must be correct
    - New password must meet strength requirements
    
    **Returns:**
    - Success message
    
    **Errors:**
    - 401: Current password incorrect
    - 422: New password doesn't meet requirements
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )
    
    # Update password
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(password_hash=get_password_hash(password_data.new_password))
    )
    await db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    logout_data: LogoutRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """
    Logout user (invalidate refresh token).
    
    **Requires:** Valid access token
    
    **Note:** In this implementation, tokens are stateless (JWT).
    For full token revocation, implement a token blacklist in Redis.
    
    **Returns:**
    - Success message
    """
    # TODO: Implement token blacklist in Redis for true revocation
    # For now, just return success (client should discard tokens)
    return {"message": "Logged out successfully"}
