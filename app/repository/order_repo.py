from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.models.order import Order, OrderCreate, OrderUpdate, OrderItem, OrderStatus
from app.db.models.cart import Cart
from app.db.models.item import Item

class OrderRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.orders
        self.carts_collection = database.carts
        self.items_collection = database.items

    async def create_from_cart(self, user_id: str, order_data: OrderCreate) -> Optional[Order]:
        if not ObjectId.is_valid(user_id):
            return None
        
        user_obj_id = ObjectId(user_id)
        
        # Get user's cart
        cart_doc = await self.carts_collection.find_one({"user_id": user_obj_id})
        if not cart_doc or not cart_doc.get("items"):
            return None
        
        cart = Cart(**cart_doc)
        
        # Create order items with item details
        order_items = []
        for cart_item in cart.items:
            item_doc = await self.items_collection.find_one({"_id": cart_item.item_id})
            if item_doc:
                item = Item(**item_doc)
                order_item = OrderItem(
                    item_id=cart_item.item_id,
                    name=item.name,
                    quantity=cart_item.quantity,
                    price=cart_item.price,
                    total=cart_item.quantity * cart_item.price
                )
                order_items.append(order_item)
        
        if not order_items:
            return None
        
        # Create order
        order_dict = {
            "user_id": user_obj_id,
            "items": [item.dict() for item in order_items],
            "total_amount": cart.total_amount,
            "status": OrderStatus.PENDING,
            "shipping_address": order_data.shipping_address,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        result = await self.collection.insert_one(order_dict)
        order_dict["_id"] = result.inserted_id
        
        # Clear cart after successful order
        await self.carts_collection.update_one(
            {"_id": cart.id},
            {
                "$set": {
                    "items": [],
                    "total_amount": 0.0,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return Order(**order_dict)

    async def get_by_id(self, order_id: str) -> Optional[Order]:
        if not ObjectId.is_valid(order_id):
            return None
        
        order_doc = await self.collection.find_one({"_id": ObjectId(order_id)})
        if order_doc:
            return Order(**order_doc)
        return None

    async def get_user_orders(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Order]:
        if not ObjectId.is_valid(user_id):
            return []
        
        cursor = self.collection.find({"user_id": ObjectId(user_id)}).sort("created_at", -1).skip(skip).limit(limit)
        orders = []
        async for order_doc in cursor:
            orders.append(Order(**order_doc))
        return orders

    async def get_all_orders(self, skip: int = 0, limit: int = 100, status: Optional[OrderStatus] = None) -> List[Order]:
        filter_dict = {}
        if status:
            filter_dict["status"] = status
        
        cursor = self.collection.find(filter_dict).sort("created_at", -1).skip(skip).limit(limit)
        orders = []
        async for order_doc in cursor:
            orders.append(Order(**order_doc))
        return orders

    async def update(self, order_id: str, order_data: OrderUpdate) -> Optional[Order]:
        if not ObjectId.is_valid(order_id):
            return None
        
        update_dict = {k: v for k, v in order_data.dict().items() if v is not None}
        if not update_dict:
            return await self.get_by_id(order_id)
        
        update_dict["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": update_dict}
        )
        
        if result.modified_count:
            return await self.get_by_id(order_id)
        return None

    async def delete(self, order_id: str) -> bool:
        if not ObjectId.is_valid(order_id):
            return False
        
        result = await self.collection.delete_one({"_id": ObjectId(order_id)})
        return result.deleted_count > 0