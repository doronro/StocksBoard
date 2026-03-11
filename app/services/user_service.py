"""User service for user management."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository
from app.models import User, UserPreference
from app.schemas import UserResponse, UserPreferenceResponse
from passlib.context import CryptContext
import logging
import re

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service for user management and authentication."""

    def __init__(self, session: AsyncSession):
        """Initialize user service.

        Args:
            session: AsyncSession instance
        """
        self.session = session
        self.user_repo = UserRepository(session)

    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password meets security requirements.

        Requirements:
        - Minimum 12 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character (!@#$%^&*())

        Args:
            password: Password to validate

        Returns:
            True if password meets requirements

        Raises:
            ValueError: If password does not meet requirements
        """
        if len(password) < 12:
            raise ValueError("Password must be at least 12 characters long")
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one digit")
        if not any(c in '!@#$%^&*()' for c in password):
            raise ValueError("Password must contain at least one special character (!@#$%^&*())")
        return True

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
    ) -> Optional[UserResponse]:
        """Create a new user.

        Args:
            username: Username
            email: Email address
            password: Password (must meet security requirements)
            full_name: Optional full name

        Returns:
            UserResponse or None if user already exists

        Raises:
            ValueError: If password does not meet security requirements
        """
        # Check if user already exists
        if await self.user_repo.user_exists(username=username, email=email):
            logger.warning(f"User already exists: {username} or {email}")
            return None

        # Validate password strength
        self.validate_password(password)

        # Hash password
        hashed_password = self.hash_password(password)

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            is_active=True,
        )
        user = await self.user_repo.create(user)

        # Create user preferences
        preferences = UserPreference(user_id=user.id)
        self.session.add(preferences)

        await self.session.commit()
        logger.info(f"Created user: {username}")
        return self._convert_to_response(user)

    async def get_user(self, user_id: int) -> Optional[UserResponse]:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            UserResponse or None
        """
        user = await self.user_repo.get(user_id)
        if not user:
            return None
        return self._convert_to_response(user)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username (for authentication).

        Args:
            username: Username

        Returns:
            User instance or None
        """
        return await self.user_repo.get_by_username(username)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email.

        Args:
            email: Email address

        Returns:
            User instance or None
        """
        return await self.user_repo.get_by_email(email)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    async def get_user_preferences(self, user_id: int) -> Optional[UserPreferenceResponse]:
        """Get user preferences.

        Args:
            user_id: User ID

        Returns:
            UserPreferenceResponse or None
        """
        user = await self.user_repo.get(user_id)
        if not user or not user.user_preferences:
            return None

        prefs = user.user_preferences[0] if user.user_preferences else None
        if not prefs:
            return None

        return UserPreferenceResponse(
            user_id=user_id,
            theme=prefs.theme,
            currency=prefs.currency,
            date_format=prefs.date_format,
            time_zone=prefs.time_zone,
            notifications_enabled=prefs.notifications_enabled,
            price_alert_enabled=prefs.price_alert_enabled,
            email_notifications=prefs.email_notifications,
            updated_at=prefs.updated_at,
        )

    async def update_user_preferences(
        self,
        user_id: int,
        theme: Optional[str] = None,
        currency: Optional[str] = None,
        date_format: Optional[str] = None,
        time_zone: Optional[str] = None,
        notifications_enabled: Optional[bool] = None,
        price_alert_enabled: Optional[bool] = None,
        email_notifications: Optional[bool] = None,
    ) -> Optional[UserPreferenceResponse]:
        """Update user preferences.

        Args:
            user_id: User ID
            theme: Optional theme
            currency: Optional currency
            date_format: Optional date format
            time_zone: Optional timezone
            notifications_enabled: Optional notifications flag
            price_alert_enabled: Optional price alert flag
            email_notifications: Optional email notifications flag

        Returns:
            Updated UserPreferenceResponse or None
        """
        user = await self.user_repo.get(user_id)
        if not user or not user.user_preferences:
            return None

        prefs = user.user_preferences[0]

        update_data = {}
        if theme is not None:
            update_data["theme"] = theme
        if currency is not None:
            update_data["currency"] = currency
        if date_format is not None:
            update_data["date_format"] = date_format
        if time_zone is not None:
            update_data["time_zone"] = time_zone
        if notifications_enabled is not None:
            update_data["notifications_enabled"] = notifications_enabled
        if price_alert_enabled is not None:
            update_data["price_alert_enabled"] = price_alert_enabled
        if email_notifications is not None:
            update_data["email_notifications"] = email_notifications

        if update_data:
            for key, value in update_data.items():
                setattr(prefs, key, value)
            await self.session.commit()

        return await self.get_user_preferences(user_id)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    def _convert_to_response(self, user: User) -> UserResponse:
        """Convert User model to UserResponse schema.

        Args:
            user: User model instance

        Returns:
            UserResponse object
        """
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
