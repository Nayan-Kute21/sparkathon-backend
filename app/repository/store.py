from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional
from app.db.models.store import Store, StoreCreate, StoreItem, ItemCreate, StoreUpdate
from datetime import datetime, timezone

class StoreOperations:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.stores

    async def create_store(self, store_data: StoreCreate) -> str:
        """Create a new store"""
        store_dict = store_data.model_dump()
        store_dict["created_at"] = datetime.now(timezone.utc)
        store_dict["updated_at"] = datetime.now(timezone.utc)
        store_dict["is_active"] = True
        
        result = await self.collection.insert_one(store_dict)
        return str(result.inserted_id)
    
    async def delete_store(self, store_id: str) -> bool:
        """Delete a store by its ID"""
        result = await self.db["stores"].delete_one({"_id": ObjectId(store_id)})
        return result.deleted_count == 1

    async def get_store(self, store_id: str) -> Optional[dict]:
        """Get store by ID"""
        if not ObjectId.is_valid(store_id):
            return None
        
        store = await self.collection.find_one({"_id": ObjectId(store_id)})
        if store:
            store["_id"] = str(store["_id"])
        return store

    async def add_item_to_store(self, store_id: str, item: ItemCreate) -> bool:
        """Add a single item to store"""
        if not ObjectId.is_valid(store_id):
            return False
        
        item_dict = item.model_dump()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(store_id)},
            {
                "$push": {"items": item_dict},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
        return result.modified_count > 0

    async def add_multiple_items_to_store(self, store_id: str, items: List[ItemCreate]) -> bool:
        """Add multiple items to store"""
        if not ObjectId.is_valid(store_id):
            return False
        
        items_dict = [item.model_dump() for item in items]
        
        result = await self.collection.update_one(
            {"_id": ObjectId(store_id)},
            {
                "$push": {"items": {"$each": items_dict}},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
        return result.modified_count > 0

    async def update_item_quantity(self, store_id: str, item_name: str, new_quantity: int) -> bool:
        """Update item quantity in store"""
        if not ObjectId.is_valid(store_id):
            return False
        
        result = await self.collection.update_one(
            {
                "_id": ObjectId(store_id),
                "items.item_name": item_name
            },
            {
                "$set": {
                    "items.$.current_quantity": new_quantity,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        return result.modified_count > 0

    async def remove_item_from_store(self, store_id: str, item_name: str) -> bool:
        """Remove item from store"""
        if not ObjectId.is_valid(store_id):
            return False
        
        result = await self.collection.update_one(
            {"_id": ObjectId(store_id)},
            {
                "$pull": {"items": {"item_name": item_name}},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
        return result.modified_count > 0

    async def get_all_stores(self) -> List[dict]:
        """Get all stores"""
        stores = []
        async for store in self.collection.find({"is_active": True}):
            store["_id"] = str(store["_id"])
            stores.append(store)
        return stores

    async def update_store_conditions(self, store_id: str, update_data: StoreUpdate) -> bool:
        """Update store conditions (economic, political, environmental)"""
        if not ObjectId.is_valid(store_id):
            return False
        
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        update_dict["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.collection.update_one(
            {"_id": ObjectId(store_id)},
            {"$set": update_dict}
        )
        return result.modified_count > 0