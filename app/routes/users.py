"""User management, authentication, and preferences API routes."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import UserService
from app.rate_limit import limiter
from app.schemas import (
    UserCreate,
    UserResponse,
    UserPreferenceResponse,
    UpdateUserPreferenceRequest,
    SetThemeRequest,
    ThemeResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
)
from app.auth import (
    get_current_user_id,
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from datetime import datetime, timedelta

router = APIRouter()


@router.post("/auth/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: LoginRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_db),
):
    """Authenticate user and return JWT tokens.

    Args:
        request: Login request with username and password
        http_request: HTTP request (required for rate limiting)
        session: Database session

    Returns:
        TokenResponse with access_token and refresh_token

    Raises:
        HTTPException: If credentials are invalid
    """
    service = UserService(session)
    user = await service.get_user_by_username(request.username)

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=30 * 60,  # 30 minutes in seconds
    )


@router.post("/auth/refresh", response_model=TokenResponse)
@limiter.limit("20/minute")
async def refresh_token(
    request: RefreshTokenRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_db),
):
    """Refresh an expired access token using a refresh token.

    Args:
        request: Refresh token request
        http_request: HTTP request (required for rate limiting)
        session: Database session

    Returns:
        TokenResponse with new access_token

    Raises:
        HTTPException: If refresh token is invalid, expired, or user is inactive
    """
    from jose import JWTError, jwt
    from app.auth import SECRET_KEY, ALGORITHM

    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Verify user still exists and is active
    service = UserService(session)
    user = await service.get_user(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new access token
    access_token = create_access_token(data={"sub": user_id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,  # Return same refresh token
        token_type="bearer",
        expires_in=30 * 60,
    )


@router.post("/users/register", response_model=UserResponse)
@limiter.limit("5/minute")
async def register_user(
    request: UserCreate,
    http_request: Request,
    session: AsyncSession = Depends(get_db),
):
    """Register a new user.

    Args:
        request: User registration request
        http_request: HTTP request (required for rate limiting)
        session: Database session

    Returns:
        Created UserResponse
    """
    service = UserService(session)
    user = await service.create_user(
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
    )

    if not user:
        raise HTTPException(status_code=400, detail="User already exists")

    return user


@router.get("/users/me", response_model=UserResponse)
@limiter.limit("1000/minute")
async def get_authenticated_user(
    user_id: int = Depends(get_current_user_id),
    http_request: Request = None,
    session: AsyncSession = Depends(get_db),
):
    """Get current user profile.

    Args:
        user_id: User ID (from auth)
        http_request: HTTP request (required for rate limiting)
        session: Database session

    Returns:
        UserResponse with user data
    """
    service = UserService(session)
    user = await service.get_user(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/user/preferences", response_model=UserPreferenceResponse)
@limiter.limit("1000/minute")
async def get_user_preferences(
    user_id: int = Depends(get_current_user_id),
    http_request: Request = None,
    session: AsyncSession = Depends(get_db),
):
    """Get user preferences and settings.

    Args:
        user_id: User ID (from auth)
        http_request: HTTP request (required for rate limiting)
        session: Database session

    Returns:
        UserPreferenceResponse with user settings
    """
    service = UserService(session)
    preferences = await service.get_user_preferences(user_id)

    if not preferences:
        raise HTTPException(status_code=404, detail="User preferences not found")

    return preferences


@router.put("/user/preferences", response_model=UserPreferenceResponse)
@limiter.limit("1000/minute")
async def update_user_preferences(
    request: UpdateUserPreferenceRequest,
    user_id: int = Depends(get_current_user_id),
    http_request: Request = None,
    session: AsyncSession = Depends(get_db),
):
    """Update user preferences.

    Args:
        request: Update request
        user_id: User ID (from auth)
        http_request: HTTP request (required for rate limiting)
        session: Database session

    Returns:
        Updated UserPreferenceResponse
    """
    service = UserService(session)
    preferences = await service.update_user_preferences(
        user_id=user_id,
        theme=request.theme,
        currency=request.currency,
        date_format=request.date_format,
        time_zone=request.time_zone,
        notifications_enabled=request.notifications_enabled,
        price_alert_enabled=request.price_alert_enabled,
        email_notifications=request.email_notifications,
    )

    if not preferences:
        raise HTTPException(status_code=404, detail="User preferences not found")

    return preferences


@router.get("/user/theme", response_model=ThemeResponse)
@limiter.limit("100/minute")
async def get_user_theme(
    user_id: int = Depends(get_current_user_id),
    http_request: Request = None,
    session: AsyncSession = Depends(get_db),
):
    """Get user's theme preference.

    Args:
        user_id: User ID (from auth)
        http_request: HTTP request (required for rate limiting)
        session: Database session

    Returns:
        ThemeResponse with theme setting
    """
    service = UserService(session)
    preferences = await service.get_user_preferences(user_id)

    if not preferences:
        raise HTTPException(status_code=404, detail="User preferences not found")

    return ThemeResponse(
        theme=preferences.theme,
        updated_at=preferences.updated_at,
    )


@router.post("/user/theme", response_model=ThemeResponse)
@limiter.limit("100/minute")
async def set_user_theme(
    request: SetThemeRequest,
    user_id: int = Depends(get_current_user_id),
    http_request: Request = None,
    session: AsyncSession = Depends(get_db),
):
    """Set user's theme preference.

    Args:
        request: Theme setting request
        user_id: User ID (from auth)
        http_request: HTTP request (required for rate limiting)
        session: Database session

    Returns:
        ThemeResponse with updated theme
    """
    service = UserService(session)
    preferences = await service.update_user_preferences(
        user_id=user_id,
        theme=request.theme,
    )

    if not preferences:
        raise HTTPException(status_code=404, detail="User preferences not found")

    return ThemeResponse(
        theme=preferences.theme,
        updated_at=preferences.updated_at,
    )
