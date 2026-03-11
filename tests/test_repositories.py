"""Unit tests for repository layer."""
import pytest
from decimal import Decimal
from app.models import Stock, Quote, Watchlist, WatchlistItem, User, Position
from app.repositories import StockRepository, QuoteRepository, WatchlistRepository
from datetime import datetime


@pytest.mark.asyncio
async def test_stock_repository_create_and_get(async_session):
    """Test creating and retrieving a stock."""
    repo = StockRepository(async_session)

    # Create stock
    stock = Stock(
        symbol="AAPL",
        name="Apple Inc.",
        sector="Technology",
        exchange="NASDAQ",
        is_active=True,
    )
    stock = await repo.create(stock)
    await async_session.commit()

    # Retrieve stock
    retrieved = await repo.get(stock.id)
    assert retrieved is not None
    assert retrieved.symbol == "AAPL"
    assert retrieved.name == "Apple Inc."


@pytest.mark.asyncio
async def test_stock_repository_get_by_symbol(async_session):
    """Test retrieving stock by symbol."""
    repo = StockRepository(async_session)

    # Create stock
    stock = Stock(symbol="GOOGL", name="Google", exchange="NASDAQ")
    stock = await repo.create(stock)
    await async_session.commit()

    # Retrieve by symbol
    retrieved = await repo.get_by_symbol("GOOGL")
    assert retrieved is not None
    assert retrieved.id == stock.id


@pytest.mark.asyncio
async def test_stock_repository_get_by_symbols(async_session):
    """Test retrieving multiple stocks by symbols."""
    repo = StockRepository(async_session)

    # Create stocks
    stocks_data = [
        ("AAPL", "Apple"),
        ("GOOGL", "Google"),
        ("MSFT", "Microsoft"),
    ]
    for symbol, name in stocks_data:
        stock = Stock(symbol=symbol, name=name, exchange="NASDAQ")
        await repo.create(stock)
    await async_session.commit()

    # Retrieve multiple
    symbols = ["AAPL", "MSFT"]
    retrieved = await repo.get_by_symbols(symbols)
    assert len(retrieved) == 2
    retrieved_symbols = {s.symbol for s in retrieved}
    assert retrieved_symbols == {"AAPL", "MSFT"}


@pytest.mark.asyncio
async def test_quote_repository_create_and_get_latest(async_session):
    """Test creating and retrieving latest quote."""
    stock_repo = StockRepository(async_session)
    quote_repo = QuoteRepository(async_session)

    # Create stock
    stock = Stock(symbol="TSLA", name="Tesla", exchange="NASDAQ")
    stock = await stock_repo.create(stock)
    await async_session.commit()

    # Create quote
    quote = Quote(
        stock_id=stock.id,
        price=Decimal("150.50"),
        bid=Decimal("150.45"),
        ask=Decimal("150.55"),
        change=Decimal("2.50"),
        change_percent=Decimal("1.69"),
    )
    quote = await quote_repo.create(quote)
    await async_session.commit()

    # Retrieve latest
    retrieved = await quote_repo.get_latest_by_stock_id(stock.id)
    assert retrieved is not None
    assert retrieved.price == Decimal("150.50")


@pytest.mark.asyncio
async def test_watchlist_repository_create_and_get(async_session):
    """Test watchlist creation and retrieval."""
    repo = WatchlistRepository(async_session)

    # Create watchlist
    watchlist = Watchlist(
        user_id=1,
        name="My Watchlist",
        is_default=True,
    )
    watchlist = await repo.create(watchlist)
    await async_session.commit()

    # Retrieve
    retrieved = await repo.get(watchlist.id)
    assert retrieved is not None
    assert retrieved.name == "My Watchlist"
    assert retrieved.is_default is True


@pytest.mark.asyncio
async def test_watchlist_repository_add_and_remove_stock(async_session):
    """Test adding and removing stocks from watchlist."""
    stock_repo = StockRepository(async_session)
    watchlist_repo = WatchlistRepository(async_session)

    # Create stock and watchlist
    stock = Stock(symbol="AMZN", name="Amazon")
    stock = await stock_repo.create(stock)

    watchlist = Watchlist(user_id=1, name="Tech Stocks")
    watchlist = await watchlist_repo.create(watchlist)
    await async_session.commit()

    # Add stock
    item = await watchlist_repo.add_stock(watchlist.id, stock.id)
    assert item is not None
    await async_session.commit()

    # Verify stock is in watchlist
    is_in = await watchlist_repo.is_stock_in_watchlist(watchlist.id, stock.id)
    assert is_in is True

    # Remove stock
    removed = await watchlist_repo.remove_stock(watchlist.id, stock.id)
    assert removed is True
    await async_session.commit()

    # Verify stock is removed
    is_in = await watchlist_repo.is_stock_in_watchlist(watchlist.id, stock.id)
    assert is_in is False


@pytest.mark.asyncio
async def test_stock_repository_get_by_sector(async_session):
    """Test retrieving stocks by sector."""
    repo = StockRepository(async_session)

    # Create stocks in different sectors
    stocks_data = [
        ("AAPL", "Apple", "Technology"),
        ("JNJ", "Johnson & Johnson", "Healthcare"),
        ("MSFT", "Microsoft", "Technology"),
    ]
    for symbol, name, sector in stocks_data:
        stock = Stock(symbol=symbol, name=name, sector=sector, exchange="NASDAQ")
        await repo.create(stock)
    await async_session.commit()

    # Retrieve technology stocks
    tech_stocks = await repo.get_by_sector("Technology")
    assert len(tech_stocks) == 2
    symbols = {s.symbol for s in tech_stocks}
    assert symbols == {"AAPL", "MSFT"}


@pytest.mark.asyncio
async def test_stock_repository_search_by_name(async_session):
    """Test searching stocks by name."""
    repo = StockRepository(async_session)

    # Create stocks
    stocks_data = [
        ("AAPL", "Apple Inc."),
        ("APPL", "Apple Pie Co."),
        ("GOOG", "Google"),
    ]
    for symbol, name in stocks_data:
        stock = Stock(symbol=symbol, name=name, exchange="NASDAQ")
        await repo.create(stock)
    await async_session.commit()

    # Search for Apple
    results = await repo.search_by_name("Apple")
    assert len(results) == 2
    symbols = {s.symbol for s in results}
    assert symbols == {"AAPL", "APPL"}
