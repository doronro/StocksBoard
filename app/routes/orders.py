"""Order management API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import OrderService
from app.schemas import OrderResponse, CreateOrderRequest, UpdateOrderRequest, OrderStatusResponse
from app.auth import get_current_user_id
from app.exceptions import NotFoundError, BusinessLogicError
from datetime import datetime

router = APIRouter()


@router.post("/orders", response_model=OrderResponse)
async def create_order(
    request: CreateOrderRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Create a new order.

    Args:
        request: Order creation request
        user_id: User ID (from auth)
        session: Database session

    Returns:
        Created OrderResponse
    """
    service = OrderService(session)
    order = await service.create_order(
        user_id=user_id,
        symbol=request.symbol.upper(),
        order_type=request.order_type,
        side=request.side,
        quantity=request.quantity,
        price=request.price,
        stop_price=request.stop_price,
        expires_at=request.expires_at,
        idempotency_key=request.idempotency_key,
    )

    if not order:
        raise BusinessLogicError("Order creation failed - stock may not exist")

    return order


@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    user_id: int = Depends(get_current_user_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
):
    """Get order history.

    Args:
        user_id: User ID (from auth)
        skip: Number of records to skip
        limit: Maximum number of records
        session: Database session

    Returns:
        List of OrderResponse objects
    """
    service = OrderService(session)
    return await service.get_user_orders(user_id, skip, limit)


@router.get("/orders/pending", response_model=List[OrderResponse])
async def get_pending_orders(
    user_id: int = Depends(get_current_user_id),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
):
    """Get pending orders.

    Args:
        user_id: User ID (from auth)
        skip: Number of records to skip
        limit: Maximum number of records
        session: Database session

    Returns:
        List of pending OrderResponse objects
    """
    service = OrderService(session)
    return await service.get_pending_orders(user_id, skip, limit)


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Get order details.

    Args:
        order_id: Order ID
        user_id: User ID (from auth)
        session: Database session

    Returns:
        OrderResponse with details
    """
    service = OrderService(session)
    order = await service.get_order(user_id, order_id)

    if not order:
        raise NotFoundError("Order")

    return order


@router.get("/orders/{order_id}/status", response_model=OrderStatusResponse)
async def get_order_status(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Check order status.

    Args:
        order_id: Order ID
        user_id: User ID (from auth)
        session: Database session

    Returns:
        OrderStatusResponse with current status
    """
    service = OrderService(session)
    order = await service.get_order(user_id, order_id)

    if not order:
        raise NotFoundError("Order")

    remaining = order.quantity - order.filled_quantity

    return OrderStatusResponse(
        order_id=order.id,
        symbol=order.stock.symbol,
        status=order.status,
        filled_quantity=order.filled_quantity,
        average_filled_price=order.average_filled_price,
        remaining_quantity=remaining,
        updated_at=order.updated_at,
    )


@router.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    request: UpdateOrderRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Update an order (for limit orders).

    Args:
        order_id: Order ID
        request: Update request
        user_id: User ID (from auth)
        session: Database session

    Returns:
        Updated OrderResponse
    """
    service = OrderService(session)
    order = await service.update_order(
        user_id=user_id,
        order_id=order_id,
        price=request.price,
        stop_price=request.stop_price,
        expires_at=request.expires_at,
    )

    if not order:
        raise NotFoundError("Order")

    return order


@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    """Cancel an order.

    Args:
        order_id: Order ID
        user_id: User ID (from auth)
        session: Database session

    Returns:
        Success message
    """
    service = OrderService(session)
    success = await service.cancel_order(user_id, order_id)

    if not success:
        raise NotFoundError("Order")

    return {"message": "Order cancelled successfully"}
