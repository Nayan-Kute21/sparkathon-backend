from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.models.cart import Cart, CartItem, CartItemAdd, CartItemUpdate
from app.db.models.item import Item

class CartRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.carts
        self.items_collection = database.items

    async def get_or_create_cart(self, user_id: str) -> Cart:
        if not ObjectId.is_valid(user_id):
            raise ValueError("Invalid user ID")
        
        user_obj_id = ObjectId(user_id)
        cart_doc = await self.collection.find_one({"user_id": user_obj_id})
        
        if cart_doc:
            return Cart(**cart_doc)
        
        # Create new cart
        cart_dict = {
            "user_id": user_obj_id,
            "items": [],
            "total_amount": 0.0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        result = await self.collection.insert_one(cart_dict)
        cart_dict["_id"] = result.inserted_id
        return Cart(**cart_dict)

    async def add_item(self, user_id: str, cart_item: CartItemAdd) -> Optional[Cart]:
        # Get item details
        item_doc = await self.items_collection.find_one({"_id": ObjectId(cart_item.item_id)})
        if not item_doc:
            return None
        
        item = Item(**item_doc)
        cart = await self.get_or_create_cart(user_id)
        
        # Check if item already in cart
        existing_item_index = None
        for i, existing_item in enumerate(cart.items):
            if str(existing_item.item_id) == cart_item.item_id:
                existing_item_index = i
                break
        
        if existing_item_index is not None:
            # Update quantity
            cart.items[existing_item_index].quantity += cart_item.quantity
        else:
            # Add new item
            new_cart_item = CartItem(
                item_id=ObjectId(cart_item.item_id),
                quantity=cart_item.quantity,
                price=item.price
            )
            cart.items.append(new_cart_item)
        
        # Recalculate total
        total = sum(item.quantity * item.price for item in cart.items)
        
        # Update cart in database
        await self.collection.update_one(
            {"_id": cart.id},
            {
                "$set": {
                    "items": [item.dict() for item in cart.items],
                    "total_amount": total,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return await self.get_or_create_cart(user_id)

    async def update_item_quantity(self, user_id: str, item_id: str, update_data: CartItemUpdate) -> Optional[Cart]:
        cart = await self.get_or_create_cart(user_id)
        
        # Find and update item
        item_found = False
        for cart_item in cart.items:
            if str(cart_item.item_id) == item_id:
                cart_item.quantity = update_data.quantity
                item_found = True
                break
        
        if not item_found:
            return None
        
        # Recalculate total
        total = sum(item.quantity * item.price for item in cart.items)
        
        # Update cart in database
        await self.collection.update_one(
            {"_id": cart.id},
            {
                "$set": {
                    "items": [item.dict() for item in cart.items],
                    "total_amount": total,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return await self.get_or_create_cart(user_id)

    async def remove_item(self, user_id: str, item_id: str) -> Optional[Cart]:
        cart = await self.get_or_create_cart(user_id)
        
        # Remove item from cart
        cart.items = [item for item in cart.items if str(item.item_id) != item_id]
        
        # Recalculate total
        total = sum(item.quantity * item.price for item in cart.items)
        
        # Update cart in database
        await self.collection.update_one(
            {"_id": cart.id},
            {
                "$set": {
                    "items": [item.dict() for item in cart.items],
                    "total_amount": total,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return await self.get_or_create_cart(user_id)

    async def clear_cart(self, user_id: str) -> Optional[Cart]:
        cart = await self.get_or_create_cart(user_id)
        
        await self.collection.update_one(
            {"_id": cart.id},
            {
                "$set": {
                    "items": [],
                    "total_amount": 0.0,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return await self.get_or_create_cart(user_id)