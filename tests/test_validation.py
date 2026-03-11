"""
Comprehensive tests for input validation in order and position schemas.

Tests cover:
- Symbol validation (length, format, special characters)
- Quantity validation (bounds, decimal places)
- Price validation (bounds, decimal places)
- Stop price validation
- Order type and side validation
"""
import pytest
from decimal import Decimal
from pydantic import ValidationError
from app.schemas import CreateOrderRequest, CreatePositionRequest, UpdatePositionRequest


class TestSymbolValidation:
    """Tests for stock symbol validation."""

    def test_valid_symbol_uppercase(self):
        """Test that uppercase symbols are accepted."""
        order = CreateOrderRequest(
            symbol="AAPL",
            order_type="market",
            side="buy",
            quantity=Decimal("100.0000"),
            price=Decimal("150.00"),
        )
        assert order.symbol == "AAPL"

    def test_valid_symbol_lowercase(self):
        """Test that lowercase symbols are converted to uppercase."""
        order = CreateOrderRequest(
            symbol="aapl",
            order_type="market",
            side="buy",
            quantity=Decimal("100.0000"),
            price=Decimal("150.00"),
        )
        assert order.symbol == "AAPL"

    def test_valid_symbol_with_hyphen(self):
        """Test that symbols with hyphens are accepted."""
        order = CreateOrderRequest(
            symbol="BRK-B",
            order_type="market",
            side="buy",
            quantity=Decimal("100.0000"),
            price=Decimal("150.00"),
        )
        assert order.symbol == "BRK-B"

    def test_valid_symbol_with_period(self):
        """Test that symbols with periods are accepted."""
        order = CreateOrderRequest(
            symbol="BRK.A",
            order_type="market",
            side="buy",
            quantity=Decimal("100.0000"),
            price=Decimal("150.00"),
        )
        assert order.symbol == "BRK.A"

    def test_invalid_symbol_empty(self):
        """Test that empty symbol is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="",
                order_type="market",
                side="buy",
                quantity=Decimal("100.0000"),
                price=Decimal("150.00"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "symbol" in str(errors[0])

    def test_invalid_symbol_too_long(self):
        """Test that symbols longer than 10 characters are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="VERYLONGSYMBOL",
                order_type="market",
                side="buy",
                quantity=Decimal("100.0000"),
                price=Decimal("150.00"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_invalid_symbol_with_numbers(self):
        """Test that symbols with numbers are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AAL1",
                order_type="market",
                side="buy",
                quantity=Decimal("100.0000"),
                price=Decimal("150.00"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_invalid_symbol_with_special_chars(self):
        """Test that symbols with invalid special characters are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AA&PL",
                order_type="market",
                side="buy",
                quantity=Decimal("100.0000"),
                price=Decimal("150.00"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_invalid_symbol_with_spaces(self):
        """Test that symbols with spaces are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AA PL",
                order_type="market",
                side="buy",
                quantity=Decimal("100.0000"),
                price=Decimal("150.00"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0


class TestQuantityValidation:
    """Tests for order quantity validation."""

    def test_valid_quantity_whole_number(self):
        """Test that whole number quantities are accepted."""
        order = CreateOrderRequest(
            symbol="AAPL",
            order_type="market",
            side="buy",
            quantity=Decimal("100"),
            price=Decimal("150.00"),
        )
        assert order.quantity == Decimal("100")

    def test_valid_quantity_with_decimals(self):
        """Test that quantities with up to 4 decimal places are accepted."""
        order = CreateOrderRequest(
            symbol="AAPL",
            order_type="market",
            side="buy",
            quantity=Decimal("100.1234"),
            price=Decimal("150.00"),
        )
        assert order.quantity == Decimal("100.1234")

    def test_valid_quantity_minimum(self):
        """Test that minimum quantity (0.0001) is accepted."""
        order = CreateOrderRequest(
            symbol="AAPL",
            order_type="market",
            side="buy",
            quantity=Decimal("0.0001"),
            price=Decimal("150.00"),
        )
        assert order.quantity == Decimal("0.0001")

    def test_valid_quantity_maximum(self):
        """Test that maximum quantity is accepted."""
        order = CreateOrderRequest(
            symbol="AAPL",
            order_type="market",
            side="buy",
            quantity=Decimal("999999999.9999"),
            price=Decimal("150.00"),
        )
        assert order.quantity == Decimal("999999999.9999")

    def test_invalid_quantity_zero(self):
        """Test that zero quantity is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AAPL",
                order_type="market",
                side="buy",
                quantity=Decimal("0"),
                price=Decimal("150.00"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_invalid_quantity_negative(self):
        """Test that negative quantity is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AAPL",
                order_type="market",
                side="buy",
                quantity=Decimal("-100"),
                price=Decimal("150.00"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_invalid_quantity_below_minimum(self):
        """Test that quantity below minimum (0.0001) is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AAPL",
                order_type="market",
                side="buy",
                quantity=Decimal("0.00001"),
                price=Decimal("150.00"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_invalid_quantity_exceeds_maximum(self):
        """Test that quantity exceeding maximum is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AAPL",
                order_type="market",
                side="buy",
                quantity=Decimal("1000000000"),
                price=Decimal("150.00"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_invalid_quantity_too_many_decimals(self):
        """Test that quantities with more than 4 decimal places are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AAPL",
                order_type="market",
                side="buy",
                quantity=Decimal("100.12345"),
                price=Decimal("150.00"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0


class TestPriceValidation:
    """Tests for order price validation."""

    def test_valid_price_whole_number(self):
        """Test that whole number prices are accepted."""
        order = CreateOrderRequest(
            symbol="AAPL",
            order_type="limit",
            side="buy",
            quantity=Decimal("100"),
            price=Decimal("150"),
        )
        assert order.price == Decimal("150")

    def test_valid_price_with_decimals(self):
        """Test that prices with up to 2 decimal places are accepted."""
        order = CreateOrderRequest(
            symbol="AAPL",
            order_type="limit",
            side="buy",
            quantity=Decimal("100"),
            price=Decimal("150.25"),
        )
        assert order.price == Decimal("150.25")

    def test_valid_price_minimum(self):
        """Test that minimum price (0.01) is accepted."""
        order = CreateOrderRequest(
            symbol="AAPL",
            order_type="limit",
            side="buy",
            quantity=Decimal("100"),
            price=Decimal("0.01"),
        )
        assert order.price == Decimal("0.01")

    def test_valid_price_maximum(self):
        """Test that maximum price is accepted."""
        order = CreateOrderRequest(
            symbol="AAPL",
            order_type="limit",
            side="buy",
            quantity=Decimal("100"),
            price=Decimal("9999999.99"),
        )
        assert order.price == Decimal("9999999.99")

    def test_invalid_price_zero(self):
        """Test that zero price is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AAPL",
                order_type="limit",
                side="buy",
                quantity=Decimal("100"),
                price=Decimal("0"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_invalid_price_negative(self):
        """Test that negative price is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AAPL",
                order_type="limit",
                side="buy",
                quantity=Decimal("100"),
                price=Decimal("-50"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_invalid_price_below_minimum(self):
        """Test that price below minimum (0.01) is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AAPL",
                order_type="limit",
                side="buy",
                quantity=Decimal("100"),
                price=Decimal("0.001"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_invalid_price_exceeds_maximum(self):
        """Test that price exceeding maximum is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AAPL",
                order_type="limit",
                side="buy",
                quantity=Decimal("100"),
                price=Decimal("10000000"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_invalid_price_too_many_decimals(self):
        """Test that prices with more than 2 decimal places are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AAPL",
                order_type="limit",
                side="buy",
                quantity=Decimal("100"),
                price=Decimal("150.255"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0


class TestStopPriceValidation:
    """Tests for stop price validation."""

    def test_valid_stop_price(self):
        """Test that valid stop prices are accepted."""
        order = CreateOrderRequest(
            symbol="AAPL",
            order_type="stop",
            side="sell",
            quantity=Decimal("100"),
            stop_price=Decimal("140.00"),
        )
        assert order.stop_price == Decimal("140.00")

    def test_valid_stop_limit_order(self):
        """Test that stop-limit orders can have both prices."""
        order = CreateOrderRequest(
            symbol="AAPL",
            order_type="stop_limit",
            side="sell",
            quantity=Decimal("100"),
            price=Decimal("139.00"),
            stop_price=Decimal("140.00"),
        )
        assert order.price == Decimal("139.00")
        assert order.stop_price == Decimal("140.00")

    def test_invalid_stop_price_zero(self):
        """Test that zero stop price is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AAPL",
                order_type="stop",
                side="sell",
                quantity=Decimal("100"),
                stop_price=Decimal("0"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_invalid_stop_price_negative(self):
        """Test that negative stop price is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AAPL",
                order_type="stop",
                side="sell",
                quantity=Decimal("100"),
                stop_price=Decimal("-50"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_invalid_stop_price_exceeds_maximum(self):
        """Test that stop price exceeding maximum is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AAPL",
                order_type="stop",
                side="sell",
                quantity=Decimal("100"),
                stop_price=Decimal("10000000"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0


class TestOrderTypeAndSideValidation:
    """Tests for order type and side validation."""

    def test_valid_order_types(self):
        """Test that all valid order types are accepted."""
        valid_types = ["market", "limit", "stop", "stop_limit"]
        for order_type in valid_types:
            order = CreateOrderRequest(
                symbol="AAPL",
                order_type=order_type,
                side="buy",
                quantity=Decimal("100"),
                price=Decimal("150.00") if order_type in ["limit", "stop_limit"] else None,
                stop_price=Decimal("140.00") if order_type in ["stop", "stop_limit"] else None,
            )
            assert order.order_type == order_type.lower()

    def test_valid_order_sides(self):
        """Test that both valid order sides are accepted."""
        valid_sides = ["buy", "sell"]
        for side in valid_sides:
            order = CreateOrderRequest(
                symbol="AAPL",
                order_type="market",
                side=side,
                quantity=Decimal("100"),
                price=Decimal("150.00"),
            )
            assert order.side == side.lower()

    def test_invalid_order_type(self):
        """Test that invalid order types are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AAPL",
                order_type="invalid",
                side="buy",
                quantity=Decimal("100"),
                price=Decimal("150.00"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_invalid_order_side(self):
        """Test that invalid order sides are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreateOrderRequest(
                symbol="AAPL",
                order_type="market",
                side="invalid",
                quantity=Decimal("100"),
                price=Decimal("150.00"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0


class TestPositionValidation:
    """Tests for position-specific validation."""

    def test_valid_position_creation(self):
        """Test that valid position creation requests are accepted."""
        position = CreatePositionRequest(
            symbol="AAPL",
            quantity=Decimal("100.1234"),
            average_cost=Decimal("150.25"),
        )
        assert position.symbol == "AAPL"
        assert position.quantity == Decimal("100.1234")
        assert position.average_cost == Decimal("150.25")

    def test_invalid_position_quantity_zero(self):
        """Test that zero quantity is rejected for positions."""
        with pytest.raises(ValidationError) as exc_info:
            CreatePositionRequest(
                symbol="AAPL",
                quantity=Decimal("0"),
                average_cost=Decimal("150.25"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_invalid_position_average_cost_zero(self):
        """Test that zero average cost is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreatePositionRequest(
                symbol="AAPL",
                quantity=Decimal("100"),
                average_cost=Decimal("0"),
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_valid_position_update_quantity(self):
        """Test that valid quantity updates are accepted."""
        update = UpdatePositionRequest(quantity=Decimal("200.1234"))
        assert update.quantity == Decimal("200.1234")

    def test_valid_position_update_average_cost(self):
        """Test that valid average cost updates are accepted."""
        update = UpdatePositionRequest(average_cost=Decimal("160.50"))
        assert update.average_cost == Decimal("160.50")

    def test_valid_position_update_both(self):
        """Test that both fields can be updated together."""
        update = UpdatePositionRequest(
            quantity=Decimal("200.1234"),
            average_cost=Decimal("160.50"),
        )
        assert update.quantity == Decimal("200.1234")
        assert update.average_cost == Decimal("160.50")

    def test_invalid_position_update_quantity(self):
        """Test that invalid quantity updates are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UpdatePositionRequest(quantity=Decimal("-100"))
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_valid_position_update_optional(self):
        """Test that all fields are optional in update."""
        update = UpdatePositionRequest()
        assert update.quantity is None
        assert update.average_cost is None
