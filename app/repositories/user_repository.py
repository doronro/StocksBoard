"""User repository for data access."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self, session: AsyncSession):
        """Initialize user repository."""
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username.

        Args:
            username: Username

        Returns:
            User instance or None
        """
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email.

        Args:
            email: Email address

        Returns:
            User instance or None
        """
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> list:
        """Get all active users.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active User instances
        """
        query = select(User).where(User.is_active == True).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def user_exists(self, username: str = None, email: str = None) -> bool:
        """Check if user exists.

        Args:
            username: Optional username
            email: Optional email

        Returns:
            True if user exists, False otherwise
        """
        if username:
            query = select(User).where(User.username == username)
            result = await self.session.execute(query)
            if result.scalars().first():
                return True
        if email:
            query = select(User).where(User.email == email)
            result = await self.session.execute(query)
            if result.scalars().first():
                return True
        return False
