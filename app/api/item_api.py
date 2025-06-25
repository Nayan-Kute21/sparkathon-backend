from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..db.models.item import Item, ItemCreate, ItemUpdate
from ..repository.itemrepo import ItemRepository
from ..db.dbconnect import get_database

router = APIRouter(prefix="/items", tags=["items"])

def get_item_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> ItemRepository:
    return ItemRepository(db)

@router.post("/", response_model=Item)
async def create_item(
    item_data: ItemCreate,
    repository: ItemRepository = Depends(get_item_repository)
):
    """Create a new item"""
    return await repository.create(item_data)

@router.get("/{item_id}", response_model=Item)
async def get_item(
    item_id: str,
    repository: ItemRepository = Depends(get_item_repository)
):
    """Get item by ID"""
    item = await repository.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.get("/", response_model=List[Item])
async def get_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    repository: ItemRepository = Depends(get_item_repository)
):
    """Get all items with pagination"""
    return await repository.get_all(skip=skip, limit=limit, is_active=is_active)

@router.get("/category/{category}", response_model=List[Item])
async def get_items_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    repository: ItemRepository = Depends(get_item_repository)
):
    """Get items by category"""
    return await repository.get_by_category(category, skip=skip, limit=limit)

@router.put("/{item_id}", response_model=Item)
async def update_item(
    item_id: str,
    item_data: ItemUpdate,
    repository: ItemRepository = Depends(get_item_repository)
):
    """Update an item"""
    item = await repository.update(item_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.patch("/{item_id}/stock", response_model=Item)
async def update_item_stock(
    item_id: str,
    quantity: int,
    repository: ItemRepository = Depends(get_item_repository)
):
    """Update item stock quantity"""
    if quantity < 0:
        raise HTTPException(status_code=400, detail="Stock quantity cannot be negative")
    
    item = await repository.update_stock(item_id, quantity)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.delete("/{item_id}")
async def delete_item(
    item_id: str,
    repository: ItemRepository = Depends(get_item_repository)
):
    """Delete an item"""
    success = await repository.delete(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}