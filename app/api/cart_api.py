from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from..db.models.cart import Cart, CartItemAdd, CartItemUpdate
from app.repository.cart_repo import CartRepository
from app.db.dbconnect import get_database

router = APIRouter(prefix="/cart", tags=["cart"])

def get_cart_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> CartRepository:
    return CartRepository(db)

@router.get("/{user_id}", response_model=Cart)
async def get_cart(
    user_id: str,
    repository: CartRepository = Depends(get_cart_repository)
):
    """Get user's cart"""
    try:
        return await repository.get_or_create_cart(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

@router.post("/{user_id}/items", response_model=Cart)
async def add_item_to_cart(
    user_id: str,
    cart_item: CartItemAdd,
    repository: CartRepository = Depends(get_cart_repository)
):
    """Add item to cart"""
    cart = await repository.add_item(user_id, cart_item)
    if not cart:
        raise HTTPException(status_code=404, detail="Item not found")
    return cart

@router.put("/{user_id}/items/{item_id}", response_model=Cart)
async def update_cart_item(
    user_id: str,
    item_id: str,
    update_data: CartItemUpdate,
    repository: CartRepository = Depends(get_cart_repository)
):
    """Update item quantity in cart"""
    cart = await repository.update_item_quantity(user_id, item_id, update_data)
    if not cart:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    return cart

@router.delete("/{user_id}/items/{item_id}", response_model=Cart)
async def remove_item_from_cart(
    user_id: str,
    item_id: str,
    repository: CartRepository = Depends(get_cart_repository)
):
    """Remove item from cart"""
    cart = await repository.remove_item(user_id, item_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart

@router.delete("/{user_id}", response_model=Cart)
async def clear_cart(
    user_id: str,
    repository: CartRepository = Depends(get_cart_repository)
):
    """Clear user's cart"""
    cart = await repository.clear_cart(user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart