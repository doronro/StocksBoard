"""Quote service for market data operations."""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import QuoteRepository, StockRepository
from app.models import Quote, Stock
from app.schemas import QuoteResponse, BatchQuoteResponse
import logging

logger = logging.getLogger(__name__)


class QuoteService:
    """Service for handling market quotes and stock price data."""

    def __init__(self, session: AsyncSession):
        """Initialize quote service.

        Args:
            session: AsyncSession instance
        """
        self.session = session
        self.quote_repo = QuoteRepository(session)
        self.stock_repo = StockRepository(session)

    async def get_quote(self, symbol: str) -> Optional[QuoteResponse]:
        """Get latest quote for a stock.

        Args:
            symbol: Stock symbol

        Returns:
            QuoteResponse or None if not found
        """
        stock = await self.stock_repo.get_by_symbol(symbol)
        if not stock:
            logger.warning(f"Stock not found: {symbol}")
            return None

        quote = await self.quote_repo.get_latest_by_stock_id(stock.id)
        if not quote:
            logger.warning(f"No quote found for stock: {symbol}")
            return None

        return self._convert_to_response(quote, symbol)

    async def get_quotes(self, symbols: List[str]) -> List[QuoteResponse]:
        """Get latest quotes for multiple stocks.

        Args:
            symbols: List of stock symbols

        Returns:
            List of QuoteResponse objects
        """
        stocks = await self.stock_repo.get_by_symbols(symbols)
        if not stocks:
            return []

        stock_ids = [s.id for s in stocks]
        stock_map = {s.id: s.symbol for s in stocks}

        quotes = await self.quote_repo.get_latest_by_stock_ids(stock_ids)

        return [self._convert_to_response(q, stock_map[q.stock_id]) for q in quotes]

    async def create_or_update_quote(
        self,
        symbol: str,
        price: Decimal,
        bid: Optional[Decimal] = None,
        ask: Optional[Decimal] = None,
        bid_size: Optional[int] = None,
        ask_size: Optional[int] = None,
        volume: Optional[int] = None,
        previous_close: Optional[Decimal] = None,
        open_price: Optional[Decimal] = None,
        high: Optional[Decimal] = None,
        low: Optional[Decimal] = None,
        change: Optional[Decimal] = None,
        change_percent: Optional[Decimal] = None,
        source: str = "market_data",
    ) -> Quote:
        """Create or update a quote for a stock.

        Args:
            symbol: Stock symbol
            price: Current price
            bid: Bid price
            ask: Ask price
            bid_size: Bid size
            ask_size: Ask size
            volume: Volume
            previous_close: Previous close price
            open_price: Open price
            high: High price
            low: Low price
            change: Price change
            change_percent: Percent change
            source: Data source

        Returns:
            Created or updated Quote instance
        """
        stock = await self.stock_repo.get_by_symbol(symbol)
        if not stock:
            # Create stock if it doesn't exist
            stock = Stock(
                symbol=symbol,
                name=symbol,  # Placeholder
                exchange="NASDAQ",  # Default exchange
                is_active=True,
            )
            stock = await self.stock_repo.create(stock)

        quote = Quote(
            stock_id=stock.id,
            price=price,
            bid=bid,
            ask=ask,
            bid_size=bid_size,
            ask_size=ask_size,
            volume=volume,
            previous_close=previous_close,
            open_price=open_price,
            high=high,
            low=low,
            change=change,
            change_percent=change_percent,
            source=source,
            timestamp=datetime.utcnow(),
        )
        quote = await self.quote_repo.create(quote)
        await self.session.commit()
        return quote

    async def get_daily_change(self, symbol: str) -> Optional[dict]:
        """Get daily change metrics for a stock.

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with daily metrics or None
        """
        stock = await self.stock_repo.get_by_symbol(symbol)
        if not stock:
            return None

        return await self.quote_repo.get_daily_change(stock.id)

    async def get_quotes_with_performance(self, symbols: List[str]) -> List[dict]:
        """Get quotes with performance metrics.

        Args:
            symbols: List of stock symbols

        Returns:
            List of quote data with performance
        """
        quotes = await self.get_quotes(symbols)
        return [q.model_dump() for q in quotes]

    def _convert_to_response(self, quote: Quote, symbol: str) -> QuoteResponse:
        """Convert Quote model to QuoteResponse schema.

        Args:
            quote: Quote model instance
            symbol: Stock symbol

        Returns:
            QuoteResponse object
        """
        return QuoteResponse(
            symbol=symbol,
            price=quote.price,
            bid=quote.bid,
            ask=quote.ask,
            bid_size=quote.bid_size,
            ask_size=quote.ask_size,
            volume=quote.volume,
            previous_close=quote.previous_close,
            open_price=quote.open_price,
            high=quote.high,
            low=quote.low,
            change=quote.change,
            change_percent=quote.change_percent,
            timestamp=quote.timestamp,
            source=quote.source,
        )
