from fastapi import APIRouter, HTTPException, Depends
from app.db.models.store import Store, StoreCreate, ItemCreate, StoreUpdate
from app.repository.store import StoreOperations
from app.db.dbconnect import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List

app = APIRouter()

def get_store_operations(db: AsyncIOMotorDatabase = Depends(get_database)) -> StoreOperations:
    """Dependency to get StoreOperations instance"""
    return StoreOperations(db)

@app.post("/stores/", response_model=dict)
async def create_store(store: StoreCreate, store_ops: StoreOperations = Depends(get_store_operations)):
    """Create a new store"""
    store_id = await store_ops.create_store(store)
    return {"store_id": store_id, "message": "Store created successfully"}

@app.get("/stores/{store_id}")
async def get_store(store_id: str, store_ops: StoreOperations = Depends(get_store_operations)):
    """Get store by ID"""
    store = await store_ops.get_store(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store

@app.post("/stores/{store_id}/items/")
async def add_item_to_store(store_id: str, item: ItemCreate, store_ops: StoreOperations = Depends(get_store_operations)):
    """Add single item to store"""
    success = await store_ops.add_item_to_store(store_id, item)
    if not success:
        raise HTTPException(status_code=404, detail="Store not found or item not added")
    return {"message": "Item added successfully"}

@app.post("/stores/{store_id}/items/bulk/")
async def add_multiple_items(store_id: str, items: List[ItemCreate], store_ops: StoreOperations = Depends(get_store_operations)):
    """Add multiple items to store"""
    success = await store_ops.add_multiple_items_to_store(store_id, items)
    if not success:
        raise HTTPException(status_code=404, detail="Store not found or items not added")
    return {"message": f"{len(items)} items added successfully"}

@app.put("/stores/{store_id}/items/{item_name}/quantity/")
async def update_item_quantity(store_id: str, item_name: str, new_quantity: int, store_ops: StoreOperations = Depends(get_store_operations)):
    """Update item quantity"""
    success = await store_ops.update_item_quantity(store_id, item_name, new_quantity)
    if not success:
        raise HTTPException(status_code=404, detail="Store or item not found")
    return {"message": "Item quantity updated successfully"}

@app.get("/stores/")
async def get_all_stores(store_ops: StoreOperations = Depends(get_store_operations)):
    """Get all stores"""
    stores = await store_ops.get_all_stores()
    return {"stores": stores}

@app.put("/stores/{store_id}/conditions/")
async def update_store_conditions(store_id: str, conditions: StoreUpdate, store_ops: StoreOperations = Depends(get_store_operations)):
    """Update store economic, political, and environmental conditions"""
    success = await store_ops.update_store_conditions(store_id, conditions)
    if not success:
        raise HTTPException(status_code=404, detail="Store not found")
    return {"message": "Store conditions updated successfully"}