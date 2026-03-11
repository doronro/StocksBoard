"""Indicator service for technical analysis."""
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import TechnicalIndicatorRepository, OHLCRepository, StockRepository
from app.models import TechnicalIndicator, OHLCData
from app.schemas import TechnicalIndicatorResponse
import logging

logger = logging.getLogger(__name__)


class IndicatorService:
    """Service for calculating and managing technical indicators."""

    def __init__(self, session: AsyncSession):
        """Initialize indicator service.

        Args:
            session: AsyncSession instance
        """
        self.session = session
        self.indicator_repo = TechnicalIndicatorRepository(session)
        self.ohlc_repo = OHLCRepository(session)
        self.stock_repo = StockRepository(session)

    async def calculate_sma(
        self,
        symbol: str,
        period: int = 20,
        timeframe: str = "1d",
    ) -> Optional[TechnicalIndicatorResponse]:
        """Calculate Simple Moving Average (SMA).

        Args:
            symbol: Stock symbol
            period: Period for the SMA (default 20)
            timeframe: Timeframe (1d, 1h, etc.)

        Returns:
            TechnicalIndicatorResponse or None
        """
        stock = await self.stock_repo.get_by_symbol(symbol)
        if not stock:
            logger.warning(f"Stock not found: {symbol}")
            return None

        candlesticks = await self.ohlc_repo.get_candlesticks(stock.id, timeframe, period)
        if len(candlesticks) < period:
            logger.warning(f"Not enough data for SMA calculation: {symbol}")
            return None

        # Calculate SMA
        closes = [Decimal(str(c.close)) for c in candlesticks]
        sma = sum(closes[-period:]) / period

        # Save indicator
        indicator = TechnicalIndicator(
            stock_id=stock.id,
            indicator_name="SMA",
            period=period,
            timeframe=timeframe,
            value=sma,
            timestamp=datetime.utcnow(),
        )
        indicator = await self.indicator_repo.create(indicator)
        await self.session.commit()

        return self._convert_to_response(indicator, symbol)

    async def calculate_ema(
        self,
        symbol: str,
        period: int = 20,
        timeframe: str = "1d",
    ) -> Optional[TechnicalIndicatorResponse]:
        """Calculate Exponential Moving Average (EMA).

        Args:
            symbol: Stock symbol
            period: Period for the EMA (default 20)
            timeframe: Timeframe

        Returns:
            TechnicalIndicatorResponse or None
        """
        stock = await self.stock_repo.get_by_symbol(symbol)
        if not stock:
            return None

        candlesticks = await self.ohlc_repo.get_candlesticks(stock.id, timeframe, period * 2)
        if len(candlesticks) < period:
            logger.warning(f"Not enough data for EMA calculation: {symbol}")
            return None

        # Calculate EMA
        closes = [Decimal(str(c.close)) for c in candlesticks]
        multiplier = 2 / (period + 1)

        ema = closes[0]
        for close in closes[1:]:
            ema = close * Decimal(str(multiplier)) + ema * Decimal(str(1 - multiplier))

        indicator = TechnicalIndicator(
            stock_id=stock.id,
            indicator_name="EMA",
            period=period,
            timeframe=timeframe,
            value=ema,
            timestamp=datetime.utcnow(),
        )
        indicator = await self.indicator_repo.create(indicator)
        await self.session.commit()

        return self._convert_to_response(indicator, symbol)

    async def calculate_rsi(
        self,
        symbol: str,
        period: int = 14,
        timeframe: str = "1d",
    ) -> Optional[TechnicalIndicatorResponse]:
        """Calculate Relative Strength Index (RSI).

        Args:
            symbol: Stock symbol
            period: Period for the RSI (default 14)
            timeframe: Timeframe

        Returns:
            TechnicalIndicatorResponse or None
        """
        stock = await self.stock_repo.get_by_symbol(symbol)
        if not stock:
            return None

        candlesticks = await self.ohlc_repo.get_candlesticks(stock.id, timeframe, period + 1)
        if len(candlesticks) < period + 1:
            logger.warning(f"Not enough data for RSI calculation: {symbol}")
            return None

        # Calculate RSI
        closes = [Decimal(str(c.close)) for c in candlesticks]
        deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]

        gains = [max(d, 0) for d in deltas]
        losses = [max(-d, 0) for d in deltas]

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            rsi = Decimal("100")
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        indicator = TechnicalIndicator(
            stock_id=stock.id,
            indicator_name="RSI",
            period=period,
            timeframe=timeframe,
            value=rsi,
            timestamp=datetime.utcnow(),
        )
        indicator = await self.indicator_repo.create(indicator)
        await self.session.commit()

        return self._convert_to_response(indicator, symbol)

    async def calculate_macd(
        self,
        symbol: str,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        timeframe: str = "1d",
    ) -> Optional[TechnicalIndicatorResponse]:
        """Calculate MACD (Moving Average Convergence Divergence).

        Args:
            symbol: Stock symbol
            fast_period: Fast EMA period (default 12)
            slow_period: Slow EMA period (default 26)
            signal_period: Signal line period (default 9)
            timeframe: Timeframe

        Returns:
            TechnicalIndicatorResponse or None
        """
        stock = await self.stock_repo.get_by_symbol(symbol)
        if not stock:
            return None

        candlesticks = await self.ohlc_repo.get_candlesticks(stock.id, timeframe, slow_period * 2)
        if len(candlesticks) < slow_period:
            logger.warning(f"Not enough data for MACD calculation: {symbol}")
            return None

        closes = [Decimal(str(c.close)) for c in candlesticks]

        # Calculate fast and slow EMAs
        fast_ema = self._calculate_ema_values(closes, fast_period)
        slow_ema = self._calculate_ema_values(closes, slow_period)

        # MACD line
        macd_line = fast_ema[-1] - slow_ema[-1]

        # Signal line (EMA of MACD)
        macd_lines = [fast_ema[i] - slow_ema[i] for i in range(len(closes))]
        signal_line = self._calculate_ema_values(macd_lines, signal_period)[-1]

        # Histogram
        histogram = macd_line - signal_line

        indicator = TechnicalIndicator(
            stock_id=stock.id,
            indicator_name="MACD",
            timeframe=timeframe,
            value=macd_line,
            signal_line=signal_line,
            histogram=histogram,
            timestamp=datetime.utcnow(),
        )
        indicator = await self.indicator_repo.create(indicator)
        await self.session.commit()

        return self._convert_to_response(indicator, symbol)

    async def calculate_bollinger_bands(
        self,
        symbol: str,
        period: int = 20,
        std_dev: Decimal = Decimal("2"),
        timeframe: str = "1d",
    ) -> Optional[TechnicalIndicatorResponse]:
        """Calculate Bollinger Bands.

        Args:
            symbol: Stock symbol
            period: Period for the bands (default 20)
            std_dev: Standard deviation multiplier (default 2)
            timeframe: Timeframe

        Returns:
            TechnicalIndicatorResponse or None
        """
        stock = await self.stock_repo.get_by_symbol(symbol)
        if not stock:
            return None

        candlesticks = await self.ohlc_repo.get_candlesticks(stock.id, timeframe, period)
        if len(candlesticks) < period:
            logger.warning(f"Not enough data for Bollinger Bands calculation: {symbol}")
            return None

        closes = [Decimal(str(c.close)) for c in candlesticks]

        # Middle band (SMA)
        middle_band = sum(closes[-period:]) / period

        # Standard deviation
        variance = sum((x - middle_band) ** 2 for x in closes[-period:]) / period
        std_deviation = variance.sqrt()

        # Bands
        upper_band = middle_band + (std_deviation * std_dev)
        lower_band = middle_band - (std_deviation * std_dev)

        indicator = TechnicalIndicator(
            stock_id=stock.id,
            indicator_name="BB",
            period=period,
            timeframe=timeframe,
            value=middle_band,
            upper_band=upper_band,
            lower_band=lower_band,
            timestamp=datetime.utcnow(),
        )
        indicator = await self.indicator_repo.create(indicator)
        await self.session.commit()

        return self._convert_to_response(indicator, symbol)

    async def get_latest_indicator(
        self,
        symbol: str,
        indicator_name: str,
        period: Optional[int] = None,
        timeframe: str = "1d",
    ) -> Optional[TechnicalIndicatorResponse]:
        """Get latest indicator value.

        Args:
            symbol: Stock symbol
            indicator_name: Indicator name
            period: Optional period
            timeframe: Timeframe

        Returns:
            TechnicalIndicatorResponse or None
        """
        stock = await self.stock_repo.get_by_symbol(symbol)
        if not stock:
            return None

        indicator = await self.indicator_repo.get_latest_indicator(
            stock.id, indicator_name, period, timeframe
        )
        if not indicator:
            return None

        return self._convert_to_response(indicator, symbol)

    async def get_indicator_history(
        self,
        symbol: str,
        indicator_name: str,
        period: Optional[int] = None,
        timeframe: str = "1d",
        limit: int = 100,
    ) -> List[TechnicalIndicatorResponse]:
        """Get indicator history.

        Args:
            symbol: Stock symbol
            indicator_name: Indicator name
            period: Optional period
            timeframe: Timeframe
            limit: Maximum number of records

        Returns:
            List of TechnicalIndicatorResponse objects
        """
        stock = await self.stock_repo.get_by_symbol(symbol)
        if not stock:
            return []

        indicators = await self.indicator_repo.get_indicator_history(
            stock.id, indicator_name, period, timeframe, limit
        )

        return [self._convert_to_response(i, symbol) for i in indicators]

    @staticmethod
    def _calculate_ema_values(values: List[Decimal], period: int) -> List[Decimal]:
        """Calculate EMA values for a list.

        Args:
            values: List of values
            period: EMA period

        Returns:
            List of EMA values
        """
        if len(values) < period:
            return values

        multiplier = 2 / (period + 1)
        ema_values = []
        ema = values[0]
        ema_values.append(ema)

        for value in values[1:]:
            ema = value * Decimal(str(multiplier)) + ema * Decimal(str(1 - multiplier))
            ema_values.append(ema)

        return ema_values

    def _convert_to_response(
        self, indicator: TechnicalIndicator, symbol: str
    ) -> TechnicalIndicatorResponse:
        """Convert TechnicalIndicator model to response schema.

        Args:
            indicator: TechnicalIndicator model instance
            symbol: Stock symbol

        Returns:
            TechnicalIndicatorResponse object
        """
        return TechnicalIndicatorResponse(
            symbol=symbol,
            indicator_name=indicator.indicator_name,
            period=indicator.period,
            timeframe=indicator.timeframe,
            value=indicator.value,
            signal_line=indicator.signal_line,
            histogram=indicator.histogram,
            upper_band=indicator.upper_band,
            lower_band=indicator.lower_band,
            timestamp=indicator.timestamp,
        )
