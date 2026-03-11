"""Watchlist service for watchlist management."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import WatchlistRepository, StockRepository
from app.models import Watchlist, Stock
from app.schemas import WatchlistResponse, WatchlistItemResponse, StockResponse
import logging

logger = logging.getLogger(__name__)


class WatchlistService:
    """Service for managing user watchlists."""

    def __init__(self, session: AsyncSession):
        """Initialize watchlist service.

        Args:
            session: AsyncSession instance
        """
        self.session = session
        self.watchlist_repo = WatchlistRepository(session)
        self.stock_repo = StockRepository(session)

    async def create_watchlist(
        self, user_id: int, name: str, description: Optional[str] = None, is_default: bool = False
    ) -> WatchlistResponse:
        """Create a new watchlist.

        Args:
            user_id: User ID
            name: Watchlist name
            description: Optional description
            is_default: Whether this is the default watchlist

        Returns:
            WatchlistResponse object
        """
        watchlist = Watchlist(
            user_id=user_id,
            name=name,
            description=description,
            is_default=is_default,
        )
        watchlist = await self.watchlist_repo.create(watchlist)
        await self.session.commit()
        logger.info(f"Created watchlist: {watchlist.id} for user: {user_id}")
        return self._convert_to_response(watchlist)

    async def get_user_watchlists(self, user_id: int, skip: int = 0, limit: int = 100) -> List[WatchlistResponse]:
        """Get all watchlists for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of WatchlistResponse objects
        """
        watchlists = await self.watchlist_repo.get_user_watchlists(user_id, skip, limit)
        return [self._convert_to_response(w) for w in watchlists]

    async def get_watchlist(self, user_id: int, watchlist_id: int) -> Optional[WatchlistResponse]:
        """Get specific watchlist.

        Args:
            user_id: User ID
            watchlist_id: Watchlist ID

        Returns:
            WatchlistResponse or None
        """
        watchlist = await self.watchlist_repo.get(watchlist_id)
        if not watchlist or watchlist.user_id != user_id:
            logger.warning(f"Watchlist not found: {watchlist_id}")
            return None
        return self._convert_to_response(watchlist)

    async def add_stock_to_watchlist(
        self, user_id: int, watchlist_id: int, symbol: str
    ) -> Optional[WatchlistResponse]:
        """Add stock to watchlist.

        Args:
            user_id: User ID
            watchlist_id: Watchlist ID
            symbol: Stock symbol

        Returns:
            Updated WatchlistResponse or None
        """
        watchlist = await self.watchlist_repo.get(watchlist_id)
        if not watchlist or watchlist.user_id != user_id:
            logger.warning(f"Watchlist not found: {watchlist_id}")
            return None

        stock = await self.stock_repo.get_by_symbol(symbol)
        if not stock:
            logger.warning(f"Stock not found: {symbol}")
            return None

        # Check if already in watchlist
        is_in = await self.watchlist_repo.is_stock_in_watchlist(watchlist_id, stock.id)
        if is_in:
            logger.info(f"Stock {symbol} already in watchlist {watchlist_id}")
            return self._convert_to_response(watchlist)

        await self.watchlist_repo.add_stock(watchlist_id, stock.id)
        await self.session.commit()
        logger.info(f"Added stock {symbol} to watchlist {watchlist_id}")

        # Refresh and return
        await self.session.refresh(watchlist)
        return self._convert_to_response(watchlist)

    async def remove_stock_from_watchlist(
        self, user_id: int, watchlist_id: int, stock_id: int
    ) -> Optional[WatchlistResponse]:
        """Remove stock from watchlist.

        Args:
            user_id: User ID
            watchlist_id: Watchlist ID
            stock_id: Stock ID

        Returns:
            Updated WatchlistResponse or None
        """
        watchlist = await self.watchlist_repo.get(watchlist_id)
        if not watchlist or watchlist.user_id != user_id:
            logger.warning(f"Watchlist not found: {watchlist_id}")
            return None

        removed = await self.watchlist_repo.remove_stock(watchlist_id, stock_id)
        if not removed:
            logger.warning(f"Stock {stock_id} not in watchlist {watchlist_id}")
            return None

        await self.session.commit()
        logger.info(f"Removed stock {stock_id} from watchlist {watchlist_id}")

        await self.session.refresh(watchlist)
        return self._convert_to_response(watchlist)

    async def update_watchlist(
        self,
        user_id: int,
        watchlist_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_default: Optional[bool] = None,
    ) -> Optional[WatchlistResponse]:
        """Update watchlist details.

        Args:
            user_id: User ID
            watchlist_id: Watchlist ID
            name: Optional new name
            description: Optional new description
            is_default: Optional default flag

        Returns:
            Updated WatchlistResponse or None
        """
        watchlist = await self.watchlist_repo.get(watchlist_id)
        if not watchlist or watchlist.user_id != user_id:
            return None

        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if is_default is not None:
            update_data["is_default"] = is_default

        if update_data:
            watchlist = await self.watchlist_repo.update(watchlist_id, **update_data)
            await self.session.commit()

        return self._convert_to_response(watchlist)

    async def delete_watchlist(self, user_id: int, watchlist_id: int) -> bool:
        """Delete a watchlist.

        Args:
            user_id: User ID
            watchlist_id: Watchlist ID

        Returns:
            True if deleted, False otherwise
        """
        watchlist = await self.watchlist_repo.get(watchlist_id)
        if not watchlist or watchlist.user_id != user_id:
            return False

        await self.watchlist_repo.delete(watchlist_id)
        await self.session.commit()
        logger.info(f"Deleted watchlist {watchlist_id}")
        return True

    def _convert_to_response(self, watchlist: Watchlist) -> WatchlistResponse:
        """Convert Watchlist model to WatchlistResponse schema.

        Args:
            watchlist: Watchlist model instance

        Returns:
            WatchlistResponse object
        """
        items = [
            WatchlistItemResponse(
                id=item.id,
                stock=StockResponse.model_validate(item.stock),
                added_at=item.added_at,
            )
            for item in watchlist.items
        ]
        return WatchlistResponse(
            id=watchlist.id,
            user_id=watchlist.user_id,
            name=watchlist.name,
            description=watchlist.description,
            is_default=watchlist.is_default,
            items=items,
            created_at=watchlist.created_at,
            updated_at=watchlist.updated_at,
        )
