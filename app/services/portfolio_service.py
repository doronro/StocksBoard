"""Portfolio service for portfolio management."""
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import PositionRepository, StockRepository, QuoteRepository
from app.models import Position, Stock, PositionStatus
from app.schemas import PositionResponse, PortfolioOverviewResponse, PortfolioAllocationResponse, AssetAllocationResponse
import logging

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service for managing user portfolio and positions."""

    def __init__(self, session: AsyncSession):
        """Initialize portfolio service.

        Args:
            session: AsyncSession instance
        """
        self.session = session
        self.position_repo = PositionRepository(session)
        self.stock_repo = StockRepository(session)
        self.quote_repo = QuoteRepository(session)

    async def create_position(
        self,
        user_id: int,
        symbol: str,
        quantity: Decimal,
        average_cost: Decimal,
    ) -> Optional[PositionResponse]:
        """Create a new position.

        Args:
            user_id: User ID
            symbol: Stock symbol
            quantity: Number of shares
            average_cost: Average cost per share

        Returns:
            PositionResponse or None
        """
        stock = await self.stock_repo.get_by_symbol(symbol)
        if not stock:
            logger.warning(f"Stock not found: {symbol}")
            return None

        # Check if position already exists
        existing = await self.position_repo.get_user_position_by_stock(user_id, stock.id)
        if existing:
            logger.warning(f"Position already exists for user {user_id} and stock {stock.id}")
            return None

        # Get current price
        quote = await self.quote_repo.get_latest_by_stock_id(stock.id)
        current_price = quote.price if quote else average_cost

        total_cost = quantity * average_cost
        current_value = quantity * current_price
        unrealized_gain_loss = current_value - total_cost

        position = Position(
            user_id=user_id,
            stock_id=stock.id,
            quantity=quantity,
            average_cost=average_cost,
            current_price=current_price,
            total_cost=total_cost,
            current_value=current_value,
            unrealized_gain_loss=unrealized_gain_loss,
            unrealized_gain_loss_percent=(
                (unrealized_gain_loss / total_cost * 100) if total_cost else Decimal("0")
            ),
            status=PositionStatus.OPEN,
        )
        position = await self.position_repo.create(position)
        await self.session.commit()
        logger.info(f"Created position for user {user_id}: {symbol}")
        return self._convert_to_response(position)

    async def get_user_positions(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[PositionResponse]:
        """Get all positions for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of PositionResponse objects
        """
        positions = await self.position_repo.get_user_positions(user_id, skip=skip, limit=limit)
        return [self._convert_to_response(p) for p in positions]

    async def get_portfolio_overview(self, user_id: int) -> PortfolioOverviewResponse:
        """Get portfolio overview with metrics.

        Args:
            user_id: User ID

        Returns:
            PortfolioOverviewResponse object
        """
        metrics = await self.position_repo.get_portfolio_metrics(user_id)

        if metrics is None:
            return PortfolioOverviewResponse(
                total_positions=0,
                total_cost=Decimal("0"),
                current_value=Decimal("0"),
                total_gain_loss=Decimal("0"),
                total_gain_loss_percent=Decimal("0"),
                open_positions_count=0,
                closed_positions_count=0,
                timestamp=datetime.utcnow(),
            )

        # Count open and closed positions
        open_positions_count = await self.position_repo.count_by_user_and_status(
            user_id, PositionStatus.OPEN
        )
        closed_positions_count = await self.position_repo.count_by_user_and_status(
            user_id, PositionStatus.CLOSED
        )

        return PortfolioOverviewResponse(
            total_positions=metrics["total_positions"],
            total_cost=metrics["total_cost"],
            current_value=metrics["current_value"],
            total_gain_loss=metrics["total_gain_loss"],
            total_gain_loss_percent=metrics["total_gain_loss_percent"],
            open_positions_count=open_positions_count,
            closed_positions_count=closed_positions_count,
            timestamp=datetime.utcnow(),
        )

    async def get_portfolio_allocation(self, user_id: int) -> PortfolioAllocationResponse:
        """Get portfolio allocation by sector.

        Args:
            user_id: User ID

        Returns:
            PortfolioAllocationResponse object
        """
        allocations_data = await self.position_repo.get_sector_allocation(user_id)

        # Calculate total value
        total_value = sum(
            (a["value"] or Decimal("0")) for a in allocations_data
        )

        allocations = []
        if total_value > 0:
            for a in allocations_data:
                value = a["value"] or Decimal("0")
                percentage = (value / total_value * 100) if total_value else Decimal("0")
                allocations.append(
                    AssetAllocationResponse(
                        sector=a["sector"] or "Unknown",
                        value=value,
                        percentage=percentage,
                        stock_count=a["stock_count"],
                    )
                )

        return PortfolioAllocationResponse(
            total_value=total_value,
            allocations=allocations,
            timestamp=datetime.utcnow(),
        )

    async def update_position(
        self,
        user_id: int,
        position_id: int,
        quantity: Optional[Decimal] = None,
        average_cost: Optional[Decimal] = None,
    ) -> Optional[PositionResponse]:
        """Update a position.

        Args:
            user_id: User ID
            position_id: Position ID
            quantity: Optional new quantity
            average_cost: Optional new average cost

        Returns:
            Updated PositionResponse or None
        """
        position = await self.position_repo.get(position_id)
        if not position or position.user_id != user_id:
            return None

        update_data = {}
        if quantity is not None:
            update_data["quantity"] = quantity
        if average_cost is not None:
            update_data["average_cost"] = average_cost

        if update_data:
            # Recalculate values
            quote = await self.quote_repo.get_latest_by_stock_id(position.stock_id)
            current_price = quote.price if quote else position.current_price

            new_quantity = quantity if quantity is not None else position.quantity
            new_avg_cost = average_cost if average_cost is not None else position.average_cost

            total_cost = new_quantity * new_avg_cost
            current_value = new_quantity * current_price
            unrealized_gain_loss = current_value - total_cost

            update_data["current_price"] = current_price
            update_data["total_cost"] = total_cost
            update_data["current_value"] = current_value
            update_data["unrealized_gain_loss"] = unrealized_gain_loss
            update_data["unrealized_gain_loss_percent"] = (
                (unrealized_gain_loss / total_cost * 100) if total_cost else Decimal("0")
            )

            # Mark position as closed if quantity becomes 0
            if new_quantity <= 0:
                update_data["status"] = PositionStatus.CLOSED
                update_data["closed_at"] = datetime.utcnow()

            position = await self.position_repo.update(position_id, **update_data)
            await self.session.commit()

        return self._convert_to_response(position)

    async def delete_position(self, user_id: int, position_id: int) -> bool:
        """Delete a position.

        Args:
            user_id: User ID
            position_id: Position ID

        Returns:
            True if deleted, False otherwise
        """
        position = await self.position_repo.get(position_id)
        if not position or position.user_id != user_id:
            return False

        await self.position_repo.delete(position_id)
        await self.session.commit()
        logger.info(f"Deleted position {position_id}")
        return True

    async def revalue_position(self, position_id: int) -> Optional[PositionResponse]:
        """Revalue a position with current market price.

        Args:
            position_id: Position ID

        Returns:
            Updated PositionResponse or None
        """
        position = await self.position_repo.get(position_id)
        if not position:
            return None

        quote = await self.quote_repo.get_latest_by_stock_id(position.stock_id)
        if not quote:
            return self._convert_to_response(position)

        current_value = position.quantity * quote.price
        unrealized_gain_loss = current_value - position.total_cost

        update_data = {
            "current_price": quote.price,
            "current_value": current_value,
            "unrealized_gain_loss": unrealized_gain_loss,
            "unrealized_gain_loss_percent": (
                (unrealized_gain_loss / position.total_cost * 100)
                if position.total_cost
                else Decimal("0")
            ),
        }

        position = await self.position_repo.update(position_id, **update_data)
        await self.session.commit()
        return self._convert_to_response(position)

    def _convert_to_response(self, position: Position) -> PositionResponse:
        """Convert Position model to PositionResponse schema.

        Args:
            position: Position model instance

        Returns:
            PositionResponse object
        """
        return PositionResponse(
            id=position.id,
            stock=self._stock_to_response(position.stock),
            quantity=position.quantity,
            average_cost=position.average_cost,
            current_price=position.current_price,
            total_cost=position.total_cost,
            current_value=position.current_value,
            unrealized_gain_loss=position.unrealized_gain_loss,
            unrealized_gain_loss_percent=position.unrealized_gain_loss_percent,
            status=position.status.value,
            opened_at=position.opened_at,
            closed_at=position.closed_at,
            updated_at=position.updated_at,
        )

    @staticmethod
    def _stock_to_response(stock: Stock):
        """Convert Stock model to StockResponse schema."""
        from app.schemas import StockResponse

        return StockResponse(
            id=stock.id,
            symbol=stock.symbol,
            name=stock.name,
            sector=stock.sector,
            industry=stock.industry,
            exchange=stock.exchange,
            is_active=stock.is_active,
            created_at=stock.created_at,
            updated_at=stock.updated_at,
        )
