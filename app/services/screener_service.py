"""Screener service for stock screening."""
from typing import List, Optional
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import ScreenerRepository, StockRepository
from app.models import Screener, Stock
from app.schemas import ScreenerResponse, ScreenerCriteria, ScreenerExecutionResponse, ScreenerResultResponse, StockResponse
import logging

logger = logging.getLogger(__name__)


class ScreenerService:
    """Service for stock screening."""

    def __init__(self, session: AsyncSession):
        """Initialize screener service.

        Args:
            session: AsyncSession instance
        """
        self.session = session
        self.screener_repo = ScreenerRepository(session)
        self.stock_repo = StockRepository(session)

    async def create_screener(
        self,
        user_id: int,
        name: str,
        criteria: ScreenerCriteria,
        description: Optional[str] = None,
        is_public: bool = False,
    ) -> ScreenerResponse:
        """Create a new screener.

        Args:
            user_id: User ID
            name: Screener name
            criteria: Screening criteria
            description: Optional description
            is_public: Whether screener is public

        Returns:
            ScreenerResponse object
        """
        # Convert criteria to JSON string
        criteria_json = json.dumps(criteria.model_dump())

        screener = Screener(
            user_id=user_id,
            name=name,
            description=description,
            is_public=is_public,
            criteria=criteria_json,
        )
        screener = await self.screener_repo.create(screener)
        await self.session.commit()
        logger.info(f"Created screener {screener.id} for user {user_id}")
        return self._convert_to_response(screener)

    async def get_user_screeners(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[ScreenerResponse]:
        """Get all screeners for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ScreenerResponse objects
        """
        screeners = await self.screener_repo.get_user_screeners(user_id, skip, limit)
        return [self._convert_to_response(s) for s in screeners]

    async def get_screener(self, user_id: int, screener_id: int) -> Optional[ScreenerResponse]:
        """Get specific screener.

        Args:
            user_id: User ID
            screener_id: Screener ID

        Returns:
            ScreenerResponse or None
        """
        screener = await self.screener_repo.get_user_screener(user_id, screener_id)
        if not screener:
            return None
        return self._convert_to_response(screener)

    async def execute_screener(
        self, user_id: int, screener_id: int
    ) -> Optional[ScreenerExecutionResponse]:
        """Execute a screener to find matching stocks.

        Args:
            user_id: User ID
            screener_id: Screener ID

        Returns:
            ScreenerExecutionResponse or None
        """
        screener = await self.screener_repo.get_user_screener(user_id, screener_id)
        if not screener:
            return None

        # Parse criteria
        criteria_dict = json.loads(screener.criteria)
        criteria = ScreenerCriteria(**criteria_dict)

        # Clear previous results
        await self.screener_repo.clear_results(screener_id)

        # Get all active stocks
        all_stocks = await self.stock_repo.get_active_stocks(limit=10000)

        # Filter based on criteria
        matching_stocks = await self._filter_stocks(all_stocks, criteria)

        # Save results
        results = []
        for stock in matching_stocks:
            await self.screener_repo.add_result(screener_id, stock.id)
            results.append(
                ScreenerResultResponse(
                    stock=StockResponse(
                        id=stock.id,
                        symbol=stock.symbol,
                        name=stock.name,
                        sector=stock.sector,
                        industry=stock.industry,
                        exchange=stock.exchange,
                        is_active=stock.is_active,
                        created_at=stock.created_at,
                        updated_at=stock.updated_at,
                    ),
                    matched_at=None,
                )
            )

        await self.session.commit()
        logger.info(f"Screener {screener_id} found {len(results)} matching stocks")

        return ScreenerExecutionResponse(
            screener_id=screener_id,
            results=results,
            total_matches=len(results),
            executed_at=None,
        )

    async def update_screener(
        self,
        user_id: int,
        screener_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        criteria: Optional[ScreenerCriteria] = None,
        is_public: Optional[bool] = None,
    ) -> Optional[ScreenerResponse]:
        """Update a screener.

        Args:
            user_id: User ID
            screener_id: Screener ID
            name: Optional new name
            description: Optional new description
            criteria: Optional new criteria
            is_public: Optional public flag

        Returns:
            Updated ScreenerResponse or None
        """
        screener = await self.screener_repo.get_user_screener(user_id, screener_id)
        if not screener:
            return None

        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if criteria is not None:
            update_data["criteria"] = json.dumps(criteria.model_dump())
        if is_public is not None:
            update_data["is_public"] = is_public

        if update_data:
            screener = await self.screener_repo.update(screener_id, **update_data)
            await self.session.commit()

        return self._convert_to_response(screener)

    async def delete_screener(self, user_id: int, screener_id: int) -> bool:
        """Delete a screener.

        Args:
            user_id: User ID
            screener_id: Screener ID

        Returns:
            True if deleted, False otherwise
        """
        screener = await self.screener_repo.get_user_screener(user_id, screener_id)
        if not screener:
            return False

        await self.screener_repo.delete(screener_id)
        await self.session.commit()
        logger.info(f"Deleted screener {screener_id}")
        return True

    async def _filter_stocks(self, stocks: List[Stock], criteria: ScreenerCriteria) -> List[Stock]:
        """Filter stocks based on criteria.

        Args:
            stocks: List of stocks to filter
            criteria: Screening criteria

        Returns:
            List of filtered stocks
        """
        # TODO: Implement actual filtering logic with price, market cap, volume, etc.
        # This would require fetching real-time quote data

        filtered = stocks

        # Filter by sector if specified
        if criteria.sectors:
            filtered = [s for s in filtered if s.sector in criteria.sectors]

        # Filter by price range if specified
        # TODO: Add quote lookup here

        return filtered

    def _convert_to_response(self, screener: Screener) -> ScreenerResponse:
        """Convert Screener model to ScreenerResponse schema.

        Args:
            screener: Screener model instance

        Returns:
            ScreenerResponse object
        """
        return ScreenerResponse(
            id=screener.id,
            name=screener.name,
            description=screener.description,
            is_public=screener.is_public,
            created_at=screener.created_at,
            updated_at=screener.updated_at,
        )
