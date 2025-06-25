from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.models.user import User, UserCreate, UserUpdate

class UserRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.users

    async def create(self, user_data: UserCreate) -> User:
        user_dict = user_data.dict()
        user_dict["created_at"] = datetime.now(timezone.utc)
        user_dict["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        return User(**user_dict)

    async def get_by_id(self, user_id: str) -> Optional[User]:
        if not ObjectId.is_valid(user_id):
            return None
        
        user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user_doc:
            return User(**user_doc)
        return None

    async def get_by_email(self, email: str) -> Optional[User]:
        user_doc = await self.collection.find_one({"email": email})
        if user_doc:
            return User(**user_doc)
        return None

    async def get_by_username(self, username: str) -> Optional[User]:
        user_doc = await self.collection.find_one({"username": username})
        if user_doc:
            return User(**user_doc)
        return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        cursor = self.collection.find().skip(skip).limit(limit)
        users = []
        async for user_doc in cursor:
            users.append(User(**user_doc))
        return users

    async def update(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        if not ObjectId.is_valid(user_id):
            return None
        
        update_dict = {k: v for k, v in user_data.dict().items() if v is not None}
        if not update_dict:
            return await self.get_by_id(user_id)
        
        update_dict["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_dict}
        )
        
        if result.modified_count:
            return await self.get_by_id(user_id)
        return None

    async def delete(self, user_id: str) -> bool:
        if not ObjectId.is_valid(user_id):
            return False
        
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0