"""Unit tests for service layer."""
import pytest
from decimal import Decimal
from app.models import Stock, Quote, User, Watchlist, Position, Order
from app.services import QuoteService, WatchlistService, PortfolioService, OrderService
from datetime import datetime


@pytest.mark.asyncio
async def test_quote_service_get_quote(async_session):
    """Test getting a stock quote."""
    # Setup
    stock = Stock(symbol="AAPL", name="Apple", exchange="NASDAQ")
    async_session.add(stock)
    await async_session.flush()

    quote = Quote(
        stock_id=stock.id,
        price=Decimal("150.00"),
        change=Decimal("2.50"),
        change_percent=Decimal("1.69"),
    )
    async_session.add(quote)
    await async_session.commit()

    # Test
    service = QuoteService(async_session)
    result = await service.get_quote("AAPL")

    assert result is not None
    assert result.symbol == "AAPL"
    assert result.price == Decimal("150.00")


@pytest.mark.asyncio
async def test_quote_service_get_quotes(async_session):
    """Test getting multiple quotes."""
    # Setup
    symbols = ["AAPL", "GOOGL", "MSFT"]
    for i, symbol in enumerate(symbols):
        stock = Stock(symbol=symbol, name=f"Stock {i}", exchange="NASDAQ")
        async_session.add(stock)
        await async_session.flush()

        quote = Quote(
            stock_id=stock.id,
            price=Decimal(f"{100 + i * 10}"),
        )
        async_session.add(quote)
    await async_session.commit()

    # Test
    service = QuoteService(async_session)
    results = await service.get_quotes(symbols)

    assert len(results) == 3
    result_symbols = {r.symbol for r in results}
    assert result_symbols == {"AAPL", "GOOGL", "MSFT"}


@pytest.mark.asyncio
async def test_watchlist_service_create_and_get(async_session):
    """Test creating and getting watchlist."""
    service = WatchlistService(async_session)

    # Create
    watchlist = await service.create_watchlist(
        user_id=1,
        name="Tech Stocks",
        description="My tech watchlist",
    )

    assert watchlist is not None
    assert watchlist.id is not None
    assert watchlist.name == "Tech Stocks"

    # Get
    retrieved = await service.get_watchlist(1, watchlist.id)
    assert retrieved is not None
    assert retrieved.name == "Tech Stocks"


@pytest.mark.asyncio
async def test_watchlist_service_add_stock(async_session):
    """Test adding stock to watchlist."""
    # Setup
    stock = Stock(symbol="AAPL", name="Apple")
    async_session.add(stock)
    await async_session.commit()

    service = WatchlistService(async_session)

    # Create watchlist
    watchlist = await service.create_watchlist(user_id=1, name="My Watchlist")

    # Add stock
    updated = await service.add_stock_to_watchlist(1, watchlist.id, "AAPL")

    assert updated is not None
    assert len(updated.items) == 1
    assert updated.items[0].stock.symbol == "AAPL"


@pytest.mark.asyncio
async def test_portfolio_service_create_position(async_session):
    """Test creating a portfolio position."""
    # Setup
    stock = Stock(symbol="TSLA", name="Tesla")
    quote = Quote(stock_id=1, price=Decimal("250.00"))
    async_session.add(stock)
    await async_session.flush()
    async_session.add(quote)
    await async_session.commit()

    # Create position
    service = PortfolioService(async_session)
    position = await service.create_position(
        user_id=1,
        symbol="TSLA",
        quantity=Decimal("10"),
        average_cost=Decimal("240.00"),
    )

    assert position is not None
    assert position.id is not None
    assert position.quantity == Decimal("10")
    assert position.average_cost == Decimal("240.00")
    assert position.total_cost == Decimal("2400.00")


@pytest.mark.asyncio
async def test_portfolio_service_get_user_positions(async_session):
    """Test getting user positions."""
    # Setup
    stock = Stock(symbol="AAPL", name="Apple")
    async_session.add(stock)
    await async_session.flush()

    position = Position(
        user_id=1,
        stock_id=stock.id,
        quantity=Decimal("5"),
        average_cost=Decimal("150.00"),
        current_price=Decimal("155.00"),
        total_cost=Decimal("750.00"),
        current_value=Decimal("775.00"),
        status="open",
    )
    async_session.add(position)
    await async_session.commit()

    # Get positions
    service = PortfolioService(async_session)
    positions = await service.get_user_positions(1)

    assert len(positions) == 1
    assert positions[0].stock.symbol == "AAPL"


@pytest.mark.asyncio
async def test_order_service_create_market_order(async_session):
    """Test creating a market order."""
    # Setup
    stock = Stock(symbol="GOOGL", name="Google")
    async_session.add(stock)
    await async_session.commit()

    # Create order
    service = OrderService(async_session)
    order = await service.create_order(
        user_id=1,
        symbol="GOOGL",
        order_type="market",
        side="buy",
        quantity=Decimal("5"),
    )

    assert order is not None
    assert order.id is not None
    assert order.order_type == "market"
    assert order.side == "buy"
    assert order.quantity == Decimal("5")
    assert order.status == "pending"


@pytest.mark.asyncio
async def test_order_service_create_limit_order(async_session):
    """Test creating a limit order."""
    # Setup
    stock = Stock(symbol="MSFT", name="Microsoft")
    async_session.add(stock)
    await async_session.commit()

    # Create order
    service = OrderService(async_session)
    order = await service.create_order(
        user_id=1,
        symbol="MSFT",
        order_type="limit",
        side="sell",
        quantity=Decimal("10"),
        price=Decimal("350.00"),
    )

    assert order is not None
    assert order.order_type == "limit"
    assert order.price == Decimal("350.00")


@pytest.mark.asyncio
async def test_order_service_cancel_order(async_session):
    """Test cancelling an order."""
    # Setup
    stock = Stock(symbol="AMZN", name="Amazon")
    order = Order(
        user_id=1,
        stock_id=1,
        order_type="market",
        side="buy",
        quantity=Decimal("5"),
        status="pending",
    )
    async_session.add(stock)
    await async_session.flush()
    order.stock_id = stock.id
    async_session.add(order)
    await async_session.commit()

    # Cancel order
    service = OrderService(async_session)
    success = await service.cancel_order(1, order.id)

    assert success is True

    # Verify cancelled
    cancelled = await service.get_order(1, order.id)
    assert cancelled.status == "cancelled"


@pytest.mark.asyncio
async def test_order_service_get_pending_orders(async_session):
    """Test getting pending orders."""
    # Setup
    stock = Stock(symbol="NFLX", name="Netflix")
    orders_data = [
        ("market", "buy", "pending"),
        ("limit", "sell", "pending"),
        ("market", "buy", "filled"),
    ]
    async_session.add(stock)
    await async_session.flush()

    for order_type, side, status in orders_data:
        order = Order(
            user_id=1,
            stock_id=stock.id,
            order_type=order_type,
            side=side,
            quantity=Decimal("5"),
            status=status,
        )
        async_session.add(order)
    await async_session.commit()

    # Get pending
    service = OrderService(async_session)
    pending = await service.get_pending_orders(1)

    assert len(pending) == 2
    assert all(o.status == "pending" for o in pending)
