from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.models.item import Item, ItemCreate, ItemUpdate

class ItemRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.items

    async def create(self, item_data: ItemCreate) -> Item:
        item_dict = item_data.dict()
        item_dict["created_at"] = datetime.now(timezone.utc)
        item_dict["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.collection.insert_one(item_dict)
        item_dict["_id"] = result.inserted_id
        return Item(**item_dict)

    async def get_by_id(self, item_id: str) -> Optional[Item]:
        if not ObjectId.is_valid(item_id):
            return None
        
        item_doc = await self.collection.find_one({"_id": ObjectId(item_id)})
        if item_doc:
            return Item(**item_doc)
        return None

    async def get_all(self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> List[Item]:
        filter_dict = {}
        if is_active is not None:
            filter_dict["is_active"] = is_active
        
        cursor = self.collection.find(filter_dict).skip(skip).limit(limit)
        items = []
        async for item_doc in cursor:
            items.append(Item(**item_doc))
        return items

    async def get_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[Item]:
        cursor = self.collection.find({"category": category, "is_active": True}).skip(skip).limit(limit)
        items = []
        async for item_doc in cursor:
            items.append(Item(**item_doc))
        return items

    async def update(self, item_id: str, item_data: ItemUpdate) -> Optional[Item]:
        if not ObjectId.is_valid(item_id):
            return None
        
        update_dict = {k: v for k, v in item_data.dict().items() if v is not None}
        if not update_dict:
            return await self.get_by_id(item_id)
        
        update_dict["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": update_dict}
        )
        
        if result.modified_count:
            return await self.get_by_id(item_id)
        return None

    async def delete(self, item_id: str) -> bool:
        if not ObjectId.is_valid(item_id):
            return False
        
        result = await self.collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count > 0

    async def update_stock(self, item_id: str, quantity: int) -> Optional[Item]:
        if not ObjectId.is_valid(item_id):
            return None
        
        result = await self.collection.update_one(
            {"_id": ObjectId(item_id)},
            {
                "$set": {
                    "stock_quantity": quantity,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.modified_count:
            return await self.get_by_id(item_id)
        return None