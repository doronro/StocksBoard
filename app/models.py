"""
SQLAlchemy ORM models for the stock exchange application.
"""
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum, Numeric, Index, UniqueConstraint, Text, JSON, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_superuser = Column(Boolean, default=False)
    cash_balance = Column(Numeric(15, 2), default=Decimal("10000.00"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    user_preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_user_email", "email"),)


class Stock(Base):
    """Stock symbol and metadata model."""

    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    sector = Column(String(100), index=True)
    industry = Column(String(100))
    exchange = Column(String(10), index=True, default="NASDAQ")
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    quotes = relationship("Quote", back_populates="stock", cascade="all, delete-orphan")
    watchlist_items = relationship("WatchlistItem", back_populates="stock", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="stock", cascade="all, delete-orphan")
    ohlc_data = relationship("OHLCData", back_populates="stock", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("symbol", "exchange", name="uq_symbol_exchange"),)


class Quote(Base):
    """Real-time stock quote data model."""

    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    bid = Column(Numeric(10, 2))
    ask = Column(Numeric(10, 2))
    bid_size = Column(Integer)
    ask_size = Column(Integer)
    volume = Column(Integer)
    previous_close = Column(Numeric(10, 2))
    open_price = Column(Numeric(10, 2))
    high = Column(Numeric(10, 2))
    low = Column(Numeric(10, 2))
    change = Column(Numeric(10, 2))
    change_percent = Column(Numeric(5, 2))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source = Column(String(50), default="market_data")

    # Relationships
    stock = relationship("Stock", back_populates="quotes")

    __table_args__ = (
        Index("idx_quote_stock_timestamp", "stock_id", "timestamp"),
        UniqueConstraint("stock_id", "timestamp", name="uq_stock_timestamp"),
    )


class Watchlist(Base):
    """User watchlist model."""

    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="watchlists")
    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_watchlist_user", "user_id"),)


class WatchlistItem(Base):
    """Individual stock in a watchlist."""

    __tablename__ = "watchlist_items"

    id = Column(Integer, primary_key=True, index=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id"), nullable=False, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    watchlist = relationship("Watchlist", back_populates="items")
    stock = relationship("Stock", back_populates="watchlist_items")

    __table_args__ = (
        UniqueConstraint("watchlist_id", "stock_id", name="uq_watchlist_stock"),
        Index("idx_watchlist_item_stock", "stock_id"),
    )


class PositionStatus(str, enum.Enum):
    """Position status enumeration."""

    OPEN = "open"
    CLOSED = "closed"
    PARTIALLY_CLOSED = "partially_closed"


class Position(Base):
    """User portfolio position model."""

    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    quantity = Column(Numeric(12, 4), nullable=False)
    average_cost = Column(Numeric(10, 2), nullable=False)
    current_price = Column(Numeric(10, 2), nullable=False)
    total_cost = Column(Numeric(15, 2), nullable=False)
    current_value = Column(Numeric(15, 2), nullable=False)
    unrealized_gain_loss = Column(Numeric(15, 2))
    unrealized_gain_loss_percent = Column(Numeric(6, 2))
    status = Column(Enum(PositionStatus), default=PositionStatus.OPEN, index=True)
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="positions")
    stock = relationship("Stock", back_populates="positions")

    __table_args__ = (
        Index("idx_position_user_status", "user_id", "status"),
        UniqueConstraint("user_id", "stock_id", name="uq_user_stock_position"),
    )


class OrderStatus(str, enum.Enum):
    """Order status enumeration."""

    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class OrderType(str, enum.Enum):
    """Order type enumeration."""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(str, enum.Enum):
    """Order side enumeration."""

    BUY = "buy"
    SELL = "sell"


class Order(Base):
    """Order management model."""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    order_type = Column(Enum(OrderType), nullable=False)
    side = Column(Enum(OrderSide), nullable=False, index=True)
    quantity = Column(Numeric(12, 4), nullable=False)
    price = Column(Numeric(10, 2))  # For limit/stop orders
    stop_price = Column(Numeric(10, 2))  # For stop/stop_limit orders
    filled_quantity = Column(Numeric(12, 4), default=0)
    average_filled_price = Column(Numeric(10, 2))
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, index=True)
    expires_at = Column(DateTime)
    idempotency_key = Column(String(255), unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    filled_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="orders")

    __table_args__ = (
        Index("idx_order_user_status", "user_id", "status"),
        Index("idx_order_created_at", "created_at"),
    )


class OHLCData(Base):
    """OHLC (candlestick) data for technical analysis."""

    __tablename__ = "ohlc_data"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)  # 1m, 5m, 15m, 30m, 1h, 1d
    open_price = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(Integer)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    stock = relationship("Stock", back_populates="ohlc_data")

    __table_args__ = (
        UniqueConstraint("stock_id", "timeframe", "timestamp", name="uq_ohlc_data"),
        Index("idx_ohlc_stock_timeframe_timestamp", "stock_id", "timeframe", "timestamp"),
    )


class TechnicalIndicator(Base):
    """Technical indicator values (SMA, EMA, RSI, MACD, Bollinger Bands)."""

    __tablename__ = "technical_indicators"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    indicator_name = Column(String(50), nullable=False, index=True)  # SMA, EMA, RSI, MACD, BB
    period = Column(Integer)  # Period for the indicator
    timeframe = Column(String(10), nullable=False)  # 1m, 5m, 15m, 30m, 1h, 1d
    value = Column(Numeric(10, 4))
    signal_line = Column(Numeric(10, 4))  # For MACD
    histogram = Column(Numeric(10, 4))  # For MACD
    upper_band = Column(Numeric(10, 4))  # For Bollinger Bands
    lower_band = Column(Numeric(10, 4))  # For Bollinger Bands
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("stock_id", "indicator_name", "period", "timeframe", "timestamp",
                        name="uq_technical_indicator"),
        Index("idx_indicator_stock_timestamp", "stock_id", "timestamp"),
    )


class Screener(Base):
    """Stock screener configurations."""

    __tablename__ = "screeners"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    is_public = Column(Boolean, default=False)
    criteria = Column(String(5000))  # JSON string with screening criteria
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (Index("idx_screener_user", "user_id"),)


class ScreenerResult(Base):
    """Results from screener execution."""

    __tablename__ = "screener_results"

    id = Column(Integer, primary_key=True, index=True)
    screener_id = Column(Integer, ForeignKey("screeners.id"), nullable=False, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    matched_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        UniqueConstraint("screener_id", "stock_id", "matched_at", name="uq_screener_result"),
    )


class MarketIndex(Base):
    """Market index definitions (S&P 500, NASDAQ-100, etc.)."""

    __tablename__ = "market_indices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    quotes = relationship("IndexQuote", back_populates="index", cascade="all, delete-orphan")


class IndexQuote(Base):
    """Real-time index quote data."""

    __tablename__ = "index_quotes"

    id = Column(Integer, primary_key=True, index=True)
    index_id = Column(Integer, ForeignKey("market_indices.id"), nullable=False, index=True)
    price = Column(Numeric(12, 2), nullable=False)
    change = Column(Numeric(10, 2))
    change_percent = Column(Numeric(5, 2))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    index = relationship("MarketIndex", back_populates="quotes")

    __table_args__ = (
        UniqueConstraint("index_id", "timestamp", name="uq_index_quote_timestamp"),
    )


class UserPreference(Base):
    """User preferences and settings."""

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    theme = Column(String(20), default="light")  # light, dark
    currency = Column(String(10), default="USD")
    date_format = Column(String(20), default="YYYY-MM-DD")
    time_zone = Column(String(50), default="UTC")
    notifications_enabled = Column(Boolean, default=True)
    price_alert_enabled = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_preferences")

    __table_args__ = (Index("idx_user_preference_user", "user_id"),)


class AuditLog(Base):
    """Audit log for tracking financial operations and user actions."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer, nullable=True)
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)
    status = Column(String(20), default="success")
    error_message = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    __table_args__ = (
        Index("idx_audit_user_id_action_created_at", "user_id", "action", "created_at"),
        Index("idx_audit_resource_type_id", "resource_type", "resource_id"),
    )
