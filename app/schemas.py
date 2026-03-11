"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator
import re


# Market Data Schemas
class QuoteBase(BaseModel):
    """Base quote schema."""

    symbol: str
    price: Decimal
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    bid_size: Optional[int] = None
    ask_size: Optional[int] = None
    volume: Optional[int] = None
    previous_close: Optional[Decimal] = None
    open_price: Optional[Decimal] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    change: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None


class QuoteResponse(QuoteBase):
    """Quote response schema."""

    timestamp: datetime
    source: str

    class Config:
        from_attributes = True


class BatchQuoteRequest(BaseModel):
    """Batch quote request."""

    symbols: List[str] = Field(..., min_items=1, max_items=100)


class BatchQuoteResponse(BaseModel):
    """Batch quote response."""

    quotes: List[QuoteResponse]
    timestamp: datetime


class IndexResponse(BaseModel):
    """Market index response."""

    symbol: str
    name: str
    description: Optional[str] = None
    price: Decimal
    change: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class SectorPerformanceResponse(BaseModel):
    """Sector performance data."""

    sector: str
    change_percent: Decimal
    performance_rank: int
    stock_count: int
    timestamp: datetime


class VIXResponse(BaseModel):
    """VIX (volatility index) data."""

    symbol: str = "VIX"
    price: Decimal
    change: Decimal
    change_percent: Decimal
    timestamp: datetime


# Stock Schemas
class StockBase(BaseModel):
    """Base stock schema."""

    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    exchange: str = "NASDAQ"


class StockCreate(StockBase):
    """Stock creation schema."""

    pass


class StockResponse(StockBase):
    """Stock response schema."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Watchlist Schemas
class WatchlistItemResponse(BaseModel):
    """Watchlist item response."""

    id: int
    stock: StockResponse
    added_at: datetime

    class Config:
        from_attributes = True


class WatchlistBase(BaseModel):
    """Base watchlist schema."""

    name: str
    description: Optional[str] = None
    is_default: bool = False


class WatchlistCreate(WatchlistBase):
    """Watchlist creation schema."""

    pass


class WatchlistUpdate(BaseModel):
    """Watchlist update schema."""

    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None


class WatchlistResponse(WatchlistBase):
    """Watchlist response schema."""

    id: int
    user_id: int
    items: List[WatchlistItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AddToWatchlistRequest(BaseModel):
    """Add stock to watchlist request."""

    symbol: str


class RemoveFromWatchlistRequest(BaseModel):
    """Remove stock from watchlist request."""

    stock_id: int


# Portfolio Schemas
class PositionResponse(BaseModel):
    """Portfolio position response."""

    id: int
    stock: StockResponse
    quantity: Decimal
    average_cost: Decimal
    current_price: Decimal
    total_cost: Decimal
    current_value: Decimal
    unrealized_gain_loss: Optional[Decimal] = None
    unrealized_gain_loss_percent: Optional[Decimal] = None
    status: str
    opened_at: datetime
    closed_at: Optional[datetime] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class PortfolioOverviewResponse(BaseModel):
    """Portfolio overview response."""

    total_positions: int
    total_cost: Decimal
    current_value: Decimal
    total_gain_loss: Decimal
    total_gain_loss_percent: Decimal
    open_positions_count: int
    closed_positions_count: int
    timestamp: datetime


class AssetAllocationResponse(BaseModel):
    """Asset allocation breakdown."""

    sector: str
    value: Decimal
    percentage: Decimal
    stock_count: int


class PortfolioAllocationResponse(BaseModel):
    """Portfolio allocation response."""

    total_value: Decimal
    allocations: List[AssetAllocationResponse]
    timestamp: datetime


class PortfolioPerformanceResponse(BaseModel):
    """Portfolio performance response."""

    daily_gain_loss: Decimal
    daily_gain_loss_percent: Decimal
    ytd_gain_loss: Decimal
    ytd_gain_loss_percent: Decimal
    one_month_gain_loss_percent: Optional[Decimal] = None
    three_month_gain_loss_percent: Optional[Decimal] = None
    one_year_gain_loss_percent: Optional[Decimal] = None
    timestamp: datetime


# Position Schemas
class CreatePositionRequest(BaseModel):
    """Create position request with input validation."""

    symbol: str
    quantity: Decimal
    average_cost: Decimal

    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """
        Validate stock symbol format.

        Args:
            v: Symbol to validate

        Returns:
            Uppercase symbol

        Raises:
            ValueError: If symbol is invalid
        """
        if not v:
            raise ValueError('Symbol cannot be empty')
        if len(v) > 10:
            raise ValueError('Symbol cannot exceed 10 characters')
        if not re.match(r'^[A-Za-z\-\.]+$', v):
            raise ValueError('Symbol can only contain letters, hyphens, and periods')
        return v.upper()

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: Decimal) -> Decimal:
        """
        Validate position quantity.

        Args:
            v: Quantity to validate

        Returns:
            Validated quantity

        Raises:
            ValueError: If quantity is invalid
        """
        if v <= Decimal('0'):
            raise ValueError('Quantity must be greater than 0')
        if v < Decimal('0.0001'):
            raise ValueError('Quantity must be at least 0.0001')
        if v > Decimal('999999999.9999'):
            raise ValueError('Quantity exceeds maximum allowed')
        if v.as_tuple().exponent < -4:
            raise ValueError('Quantity cannot have more than 4 decimal places')
        return v

    @field_validator('average_cost')
    @classmethod
    def validate_average_cost(cls, v: Decimal) -> Decimal:
        """
        Validate average cost per share.

        Args:
            v: Average cost to validate

        Returns:
            Validated average cost

        Raises:
            ValueError: If average cost is invalid
        """
        if v <= Decimal('0'):
            raise ValueError('Average cost must be greater than 0')
        if v < Decimal('0.01'):
            raise ValueError('Average cost must be at least 0.01')
        if v > Decimal('9999999.99'):
            raise ValueError('Average cost exceeds maximum allowed')
        if v.as_tuple().exponent < -2:
            raise ValueError('Average cost cannot have more than 2 decimal places')
        return v


class UpdatePositionRequest(BaseModel):
    """Update position request with validation."""

    quantity: Optional[Decimal] = None
    average_cost: Optional[Decimal] = None

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate quantity if provided."""
        if v is None:
            return v
        if v <= Decimal('0'):
            raise ValueError('Quantity must be greater than 0')
        if v > Decimal('999999999.9999'):
            raise ValueError('Quantity exceeds maximum allowed')
        if v.as_tuple().exponent < -4:
            raise ValueError('Quantity cannot have more than 4 decimal places')
        return v

    @field_validator('average_cost')
    @classmethod
    def validate_average_cost(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate average cost if provided."""
        if v is None:
            return v
        if v <= Decimal('0'):
            raise ValueError('Average cost must be greater than 0')
        if v > Decimal('9999999.99'):
            raise ValueError('Average cost exceeds maximum allowed')
        if v.as_tuple().exponent < -2:
            raise ValueError('Average cost cannot have more than 2 decimal places')
        return v


# Order Schemas
class OrderBase(BaseModel):
    """Base order schema."""

    symbol: str
    order_type: str  # market, limit, stop, stop_limit
    side: str  # buy, sell
    quantity: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    idempotency_key: Optional[str] = None  # Prevent duplicate orders from rapid clicks


class CreateOrderRequest(OrderBase):
    """Create order request with comprehensive input validation."""

    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """
        Validate stock symbol format.

        Symbol must be 1-10 characters, contain only letters, hyphens, and periods.
        Examples: AAPL, BRK.A, BRK-B

        Args:
            v: Symbol to validate

        Returns:
            Uppercase symbol

        Raises:
            ValueError: If symbol is invalid
        """
        if not v:
            raise ValueError('Symbol cannot be empty')
        if len(v) > 10:
            raise ValueError('Symbol cannot exceed 10 characters')
        # Only allow letters, hyphens, and periods
        if not re.match(r'^[A-Za-z\-\.]+$', v):
            raise ValueError('Symbol can only contain letters, hyphens, and periods')
        return v.upper()

    @field_validator('order_type')
    @classmethod
    def validate_order_type(cls, v: str) -> str:
        """
        Validate order type.

        Args:
            v: Order type to validate

        Returns:
            Lowercase order type

        Raises:
            ValueError: If order type is invalid
        """
        valid_types = {'market', 'limit', 'stop', 'stop_limit'}
        if v.lower() not in valid_types:
            raise ValueError(f'Order type must be one of: {", ".join(valid_types)}')
        return v.lower()

    @field_validator('side')
    @classmethod
    def validate_side(cls, v: str) -> str:
        """
        Validate order side.

        Args:
            v: Order side to validate

        Returns:
            Lowercase side

        Raises:
            ValueError: If side is invalid
        """
        valid_sides = {'buy', 'sell'}
        if v.lower() not in valid_sides:
            raise ValueError(f'Side must be one of: {", ".join(valid_sides)}')
        return v.lower()

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: Decimal) -> Decimal:
        """
        Validate order quantity with bounds checking.

        Quantity must be between 0.0001 and 999,999,999.9999

        Args:
            v: Quantity to validate

        Returns:
            Validated quantity

        Raises:
            ValueError: If quantity is out of bounds
        """
        if v <= Decimal('0'):
            raise ValueError('Quantity must be greater than 0')
        if v < Decimal('0.0001'):
            raise ValueError('Quantity must be at least 0.0001')
        if v > Decimal('999999999.9999'):
            raise ValueError('Quantity exceeds maximum allowed (999,999,999.9999)')
        # Validate decimal places (max 4)
        if v.as_tuple().exponent < -4:
            raise ValueError('Quantity cannot have more than 4 decimal places')
        return v

    @field_validator('price')
    @classmethod
    def validate_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """
        Validate order price with bounds checking.

        Price must be between 0.01 and 9,999,999.99

        Args:
            v: Price to validate

        Returns:
            Validated price

        Raises:
            ValueError: If price is out of bounds
        """
        if v is None:
            return v
        if v <= Decimal('0'):
            raise ValueError('Price must be greater than 0')
        if v < Decimal('0.01'):
            raise ValueError('Price must be at least 0.01')
        if v > Decimal('9999999.99'):
            raise ValueError('Price exceeds maximum allowed (9,999,999.99)')
        # Validate decimal places (max 2)
        if v.as_tuple().exponent < -2:
            raise ValueError('Price cannot have more than 2 decimal places')
        return v

    @field_validator('stop_price')
    @classmethod
    def validate_stop_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """
        Validate stop price with bounds checking.

        Stop price must be between 0.01 and 9,999,999.99

        Args:
            v: Stop price to validate

        Returns:
            Validated stop price

        Raises:
            ValueError: If stop price is out of bounds
        """
        if v is None:
            return v
        if v <= Decimal('0'):
            raise ValueError('Stop price must be greater than 0')
        if v < Decimal('0.01'):
            raise ValueError('Stop price must be at least 0.01')
        if v > Decimal('9999999.99'):
            raise ValueError('Stop price exceeds maximum allowed (9,999,999.99)')
        # Validate decimal places (max 2)
        if v.as_tuple().exponent < -2:
            raise ValueError('Stop price cannot have more than 2 decimal places')
        return v


class UpdateOrderRequest(BaseModel):
    """Update order request."""

    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    expires_at: Optional[datetime] = None


class OrderResponse(BaseModel):
    """Order response schema."""

    id: int
    stock: StockResponse
    order_type: str
    side: str
    quantity: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    filled_quantity: Decimal
    average_filled_price: Optional[Decimal] = None
    status: str
    expires_at: Optional[datetime] = None
    idempotency_key: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    filled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderStatusResponse(BaseModel):
    """Order status response."""

    order_id: int
    symbol: str
    status: str
    filled_quantity: Decimal
    average_filled_price: Optional[Decimal] = None
    remaining_quantity: Decimal
    updated_at: datetime


# Technical Analysis Schemas
class OHLCDataResponse(BaseModel):
    """OHLC data response."""

    symbol: str
    timeframe: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class CandlestickResponse(BaseModel):
    """Candlestick data response."""

    data: List[OHLCDataResponse]
    symbol: str
    timeframe: str
    count: int
    timestamp: datetime


class TechnicalIndicatorResponse(BaseModel):
    """Technical indicator response."""

    symbol: str
    indicator_name: str
    period: Optional[int] = None
    timeframe: str
    value: Optional[Decimal] = None
    signal_line: Optional[Decimal] = None  # MACD
    histogram: Optional[Decimal] = None  # MACD
    upper_band: Optional[Decimal] = None  # Bollinger Bands
    lower_band: Optional[Decimal] = None  # Bollinger Bands
    timestamp: datetime

    class Config:
        from_attributes = True


class CalculateIndicatorRequest(BaseModel):
    """Calculate indicator request."""

    symbol: str
    indicator: str  # SMA, EMA, RSI, MACD, BB
    period: Optional[int] = 20
    timeframe: str = "1d"


# Screener Schemas
class ScreenerCriteria(BaseModel):
    """Stock screener criteria."""

    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    min_market_cap: Optional[str] = None
    max_market_cap: Optional[str] = None
    sectors: Optional[List[str]] = None
    min_volume: Optional[int] = None
    min_change_percent: Optional[Decimal] = None
    max_change_percent: Optional[Decimal] = None


class CreateScreenerRequest(BaseModel):
    """Create screener request."""

    name: str
    description: Optional[str] = None
    criteria: ScreenerCriteria
    is_public: bool = False


class ScreenerResponse(BaseModel):
    """Screener response."""

    id: int
    name: str
    description: Optional[str] = None
    is_public: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScreenerResultResponse(BaseModel):
    """Screener result response."""

    stock: StockResponse
    matched_at: datetime

    class Config:
        from_attributes = True


class ScreenerExecutionResponse(BaseModel):
    """Screener execution response."""

    screener_id: int
    results: List[ScreenerResultResponse]
    total_matches: int
    executed_at: datetime


# News & Sentiment Schemas
class NewsArticleResponse(BaseModel):
    """News article response."""

    id: str
    title: str
    summary: str
    source: str
    url: str
    published_at: datetime
    image_url: Optional[str] = None


class NewsListResponse(BaseModel):
    """News list response."""

    articles: List[NewsArticleResponse]
    total_count: int
    timestamp: datetime


class SentimentResponse(BaseModel):
    """Sentiment analysis response."""

    symbol: str
    sentiment: str  # bullish, neutral, bearish
    sentiment_score: Decimal  # -1.0 to 1.0
    confidence: Decimal  # 0.0 to 1.0
    articles_count: int
    timestamp: datetime


class EarningsResponse(BaseModel):
    """Earnings calendar entry response."""

    symbol: str
    company_name: str
    earnings_date: datetime
    eps_estimate: Optional[Decimal] = None
    eps_actual: Optional[Decimal] = None
    revenue_estimate: Optional[str] = None
    revenue_actual: Optional[str] = None
    surprise_percent: Optional[Decimal] = None


# User Preferences Schemas
class UserPreferenceResponse(BaseModel):
    """User preference response."""

    user_id: int
    theme: str
    currency: str
    date_format: str
    time_zone: str
    notifications_enabled: bool
    price_alert_enabled: bool
    email_notifications: bool
    updated_at: datetime

    class Config:
        from_attributes = True


class UpdateUserPreferenceRequest(BaseModel):
    """Update user preference request."""

    theme: Optional[str] = None
    currency: Optional[str] = None
    date_format: Optional[str] = None
    time_zone: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    price_alert_enabled: Optional[bool] = None
    email_notifications: Optional[bool] = None


class SetThemeRequest(BaseModel):
    """Set theme request."""

    theme: str  # light, dark


class ThemeResponse(BaseModel):
    """Theme response."""

    theme: str
    updated_at: datetime


# User Authentication Schemas
class UserBase(BaseModel):
    """Base user schema."""

    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""

    password: str


class UserResponse(UserBase):
    """User response schema."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login request."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str


# Error Response Schema
class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str
    message: str
    status_code: int
    timestamp: datetime
