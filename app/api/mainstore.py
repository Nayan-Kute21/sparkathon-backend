from fastapi import APIRouter, HTTPException, Depends
from app.db.models.mainstore import (
    MainStore, MainStoreCreate, MainStoreUpdate,
    MainStoreItem, Order, OrderCreate, OrderUpdate
)
from app.repository.mainstore import MainStoreOperations
from app.db.dbconnect import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List

app = APIRouter()

def get_mainstore_operations(db: AsyncIOMotorDatabase = Depends(get_database)) -> MainStoreOperations:
    """Dependency to get MainStoreOperations instance"""
    return MainStoreOperations(db)

# Main Store endpoints
@app.post("/mainstore/", response_model=dict)
async def create_main_store(store: MainStoreCreate, mainstore_ops: MainStoreOperations = Depends(get_mainstore_operations)):
    """Create a new main store"""
    store_id = await mainstore_ops.create_main_store(store)
    return {"store_id": store_id, "message": "Main store created successfully"}

@app.get("/mainstore/{store_id}")
async def get_main_store(store_id: str, mainstore_ops: MainStoreOperations = Depends(get_mainstore_operations)):
    """Get main store by ID"""
    store = await mainstore_ops.get_main_store(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Main store not found")
    return store

@app.get("/mainstore/")
async def get_all_main_stores(mainstore_ops: MainStoreOperations = Depends(get_mainstore_operations)):
    """Get all main stores"""
    stores = await mainstore_ops.get_all_main_stores()
    return {"stores": stores}

@app.put("/mainstore/{store_id}")
async def update_main_store(store_id: str, store_data: MainStoreUpdate, mainstore_ops: MainStoreOperations = Depends(get_mainstore_operations)):
    """Update main store information"""
    success = await mainstore_ops.update_main_store(store_id, store_data)
    if not success:
        raise HTTPException(status_code=404, detail="Main store not found")
    return {"message": "Main store updated successfully"}

@app.post("/mainstore/{store_id}/items/")
async def add_item_to_main_store(store_id: str, item: MainStoreItem, mainstore_ops: MainStoreOperations = Depends(get_mainstore_operations)):
    """Add or update item in main store inventory"""
    success = await mainstore_ops.add_item_to_main_store(store_id, item)
    if not success:
        raise HTTPException(status_code=404, detail="Main store not found or item not added")
    return {"message": "Item added to main store successfully"}

@app.put("/mainstore/{store_id}/items/{item_name}/quantity/")
async def update_main_store_item_quantity(store_id: str, item_name: str, new_quantity: int, mainstore_ops: MainStoreOperations = Depends(get_mainstore_operations)):
    """Update item quantity in main store"""
    success = await mainstore_ops.update_item_quantity(store_id, item_name, new_quantity)
    if not success:
        raise HTTPException(status_code=404, detail="Main store or item not found")
    return {"message": "Item quantity updated successfully"}

# Order endpoints
@app.post("/orders/", response_model=dict)
async def create_order(order: OrderCreate, mainstore_ops: MainStoreOperations = Depends(get_mainstore_operations)):
    """Create a new order from store to a specific main store"""
    order_id = await mainstore_ops.create_order(order)
    if not order_id:
        raise HTTPException(status_code=404, detail="Main store not found or invalid")
    return {"order_id": order_id, "message": "Order created successfully"}

@app.get("/orders/{order_id}")
async def get_order(order_id: str, mainstore_ops: MainStoreOperations = Depends(get_mainstore_operations)):
    """Get order by ID"""
    order = await mainstore_ops.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/orders/")
async def get_all_orders(mainstore_ops: MainStoreOperations = Depends(get_mainstore_operations)):
    """Get all orders"""
    orders = await mainstore_ops.get_all_orders()
    return {"orders": orders}

@app.get("/stores/{store_id}/orders/")
async def get_store_orders(store_id: str, mainstore_ops: MainStoreOperations = Depends(get_mainstore_operations)):
    """Get all orders for a specific store"""
    orders = await mainstore_ops.get_store_orders(store_id)
    return {"orders": orders}

@app.put("/orders/{order_id}/status/")
async def update_order_status(order_id: str, update_data: OrderUpdate, mainstore_ops: MainStoreOperations = Depends(get_mainstore_operations)):
    """Update order status"""
    success = await mainstore_ops.update_order_status(order_id, update_data)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order status updated successfully"}

@app.post("/orders/{order_id}/process/")
async def process_order(order_id: str, mainstore_ops: MainStoreOperations = Depends(get_mainstore_operations)):
    """Process an order and update inventory"""
    success = await mainstore_ops.process_order(order_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not process order. Check inventory or order status.")
    return {"message": "Order processed successfully"}

@app.get("/mainstore/{main_store_id}/orders/")
async def get_main_store_orders(main_store_id: str, mainstore_ops: MainStoreOperations = Depends(get_mainstore_operations)):
    """Get all orders for a specific main store"""
    orders = await mainstore_ops.get_main_store_orders(main_store_id)
    return {"orders": orders}