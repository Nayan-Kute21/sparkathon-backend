from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.models.order import Order, OrderCreate, OrderUpdate, OrderStatus
from app.repository.order_repo import OrderRepository
from app.db.dbconnect import get_database

router = APIRouter(prefix="/orders", tags=["orders"])

def get_order_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> OrderRepository:
    return OrderRepository(db)

@router.post("/{user_id}", response_model=Order)
async def create_order(
    user_id: str,
    order_data: OrderCreate,
    repository: OrderRepository = Depends(get_order_repository)
):
    """Create order from user's cart"""
    order = await repository.create_from_cart(user_id, order_data)
    if not order:
        raise HTTPException(status_code=400, detail="Cannot create order. Cart is empty or user not found")
    return order

@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    repository: OrderRepository = Depends(get_order_repository)
):
    """Get order by ID"""
    order = await repository.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/user/{user_id}", response_model=List[Order])
async def get_user_orders(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    repository: OrderRepository = Depends(get_order_repository)
):
    """Get all orders for a user"""
    return await repository.get_user_orders(user_id, skip=skip, limit=limit)

@router.get("/", response_model=List[Order])
async def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[OrderStatus] = Query(None),
    repository: OrderRepository = Depends(get_order_repository)
):
    """Get all orders with pagination and optional status filter"""
    return await repository.get_all_orders(skip=skip, limit=limit, status=status)

@router.put("/{order_id}", response_model=Order)
async def update_order(
    order_id: str,
    order_data: OrderUpdate,
    repository: OrderRepository = Depends(get_order_repository)
):
    """Update an order"""
    order = await repository.update(order_id, order_data)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.delete("/{order_id}")
async def delete_order(
    order_id: str,
    repository: OrderRepository = Depends(get_order_repository)
):
    """Delete an order"""
    success = await repository.delete(order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}