"""Base repository class with common CRUD operations."""
from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Base repository class with common CRUD operations."""

    def __init__(self, model: Type[T], session: AsyncSession):
        """Initialize repository.

        Args:
            model: SQLAlchemy model class
            session: AsyncSession instance
        """
        self.model = model
        self.session = session

    async def create(self, obj: T) -> T:
        """Create a new record.

        Args:
            obj: Model instance to create

        Returns:
            Created model instance
        """
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def get(self, id: int) -> Optional[T]:
        """Get a record by ID.

        Args:
            id: Record ID

        Returns:
            Model instance or None if not found
        """
        return await self.session.get(self.model, id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        query = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, id: int, **kwargs) -> Optional[T]:
        """Update a record.

        Args:
            id: Record ID
            **kwargs: Fields to update

        Returns:
            Updated model instance or None if not found
        """
        query = update(self.model).where(self.model.id == id).values(**kwargs)
        await self.session.execute(query)
        return await self.get(id)

    async def delete(self, id: int) -> bool:
        """Delete a record.

        Args:
            id: Record ID

        Returns:
            True if deleted, False if not found
        """
        query = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.rowcount > 0

    async def count(self) -> int:
        """Count total records.

        Returns:
            Total number of records
        """
        query = select(self.model)
        result = await self.session.execute(query)
        return len(result.scalars().all())

    async def commit(self):
        """Commit changes to database."""
        await self.session.commit()

    async def rollback(self):
        """Rollback changes."""
        await self.session.rollback()
