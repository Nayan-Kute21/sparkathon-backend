from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional
from app.db.models.mainstore import (
    MainStore, MainStoreCreate, MainStoreUpdate, 
    MainStoreItem, Order, OrderCreate, OrderUpdate
)
from datetime import datetime, timezone

class MainStoreOperations:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.mainstore_collection = db.mainstore
        self.orders_collection = db.orders

    # Main Store Operations
    async def create_main_store(self, store_data: MainStoreCreate) -> str:
        """Create a new main store"""
        store_dict = store_data.model_dump()
        store_dict["created_at"] = datetime.now(timezone.utc)
        store_dict["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.mainstore_collection.insert_one(store_dict)
        return str(result.inserted_id)

    async def get_main_store(self, store_id: str) -> Optional[dict]:
        """Get main store by ID"""
        if not ObjectId.is_valid(store_id):
            return None
        
        store = await self.mainstore_collection.find_one({"_id": ObjectId(store_id)})
        if store:
            store["_id"] = str(store["_id"])
        return store

    async def get_all_main_stores(self) -> List[dict]:
        """Get all main stores"""
        stores = []
        async for store in self.mainstore_collection.find():
            store["_id"] = str(store["_id"])
            stores.append(store)
        return stores

    async def update_main_store(self, store_id: str, update_data: MainStoreUpdate) -> bool:
        """Update main store information"""
        if not ObjectId.is_valid(store_id):
            return False
        
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        update_dict["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.mainstore_collection.update_one(
            {"_id": ObjectId(store_id)},
            {"$set": update_dict}
        )
        return result.modified_count > 0

    async def add_item_to_main_store(self, store_id: str, item: MainStoreItem) -> bool:
        """Add a single item to main store inventory"""
        if not ObjectId.is_valid(store_id):
            return False
        
        # Check if item already exists
        existing = await self.mainstore_collection.find_one(
            {
                "_id": ObjectId(store_id),
                "items.item_name": item.item_name
            }
        )
        
        if existing:
            # Update existing item
            result = await self.mainstore_collection.update_one(
                {
                    "_id": ObjectId(store_id),
                    "items.item_name": item.item_name
                },
                {
                    "$set": {
                        "items.$": item.model_dump(),
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
        else:
            # Add new item
            result = await self.mainstore_collection.update_one(
                {"_id": ObjectId(store_id)},
                {
                    "$push": {"items": item.model_dump()},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
            )
            
        return result.modified_count > 0

    async def update_item_quantity(self, store_id: str, item_name: str, new_quantity: int) -> bool:
        """Update item quantity in main store"""
        if not ObjectId.is_valid(store_id):
            return False
        
        result = await self.mainstore_collection.update_one(
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

    # Order Operations
    async def create_order(self, order_data: OrderCreate) -> str:
        """Create a new order from a store to a specific main store"""
        order_dict = order_data.model_dump()
        
        # Verify the main store exists
        if not ObjectId.is_valid(order_data.main_store_id):
            return None
            
        main_store = await self.mainstore_collection.find_one({"_id": ObjectId(order_data.main_store_id)})
        if not main_store:
            return None
        
        # Calculate total amount if prices are available
        total_amount = 0.0
        for item in order_data.items:
            # Check if item exists in main store and get price
            for store_item in main_store.get("items", []):
                if store_item["item_name"] == item.item_name and store_item.get("price") is not None:
                    item_price = store_item["price"]
                    if item.price is None:  # Use main store price if not provided in order
                        item.price = item_price
                    total_amount += item.price * item.quantity
                    break
        
        order_dict["total_amount"] = total_amount
        order_dict["created_at"] = datetime.now(timezone.utc)
        order_dict["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.orders_collection.insert_one(order_dict)
        return str(result.inserted_id)

    async def get_order(self, order_id: str) -> Optional[dict]:
        """Get order by ID"""
        if not ObjectId.is_valid(order_id):
            return None
        
        order = await self.orders_collection.find_one({"_id": ObjectId(order_id)})
        if order:
            order["_id"] = str(order["_id"])
        return order

    async def get_all_orders(self) -> List[dict]:
        """Get all orders"""
        orders = []
        async for order in self.orders_collection.find():
            order["_id"] = str(order["_id"])
            orders.append(order)
        return orders

    async def get_store_orders(self, store_id: str) -> List[dict]:
        """Get all orders for a specific store"""
        orders = []
        async for order in self.orders_collection.find({"store_id": store_id}):
            order["_id"] = str(order["_id"])
            orders.append(order)
        return orders

    async def update_order_status(self, order_id: str, update_data: OrderUpdate) -> bool:
        """Update order status"""
        if not ObjectId.is_valid(order_id):
            return False
        
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        update_dict["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.orders_collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": update_dict}
        )
        return result.modified_count > 0

    async def process_order(self, order_id: str) -> bool:
        """Process an order and update inventory"""
        if not ObjectId.is_valid(order_id):
            return False
        
        # Get the order
        order = await self.orders_collection.find_one({"_id": ObjectId(order_id)})
        if not order or not ObjectId.is_valid(order.get("main_store_id", "")):
            return False
        
        # Get the specified main store
        main_store = await self.mainstore_collection.find_one({"_id": ObjectId(order["main_store_id"])})
        if not main_store:
            return False
        
        # Check if we have enough inventory for all items
        insufficient_items = []
        for order_item in order["items"]:
            item_found = False
            for store_item in main_store["items"]:
                if store_item["item_name"] == order_item["item_name"]:
                    item_found = True
                    if store_item["current_quantity"] < order_item["quantity"]:
                        insufficient_items.append(order_item["item_name"])
                    break
            
            if not item_found:
                insufficient_items.append(order_item["item_name"])
        
        if insufficient_items:
            # Update order with a note about insufficient inventory
            await self.orders_collection.update_one(
                {"_id": ObjectId(order_id)},
                {
                    "$set": {
                        "status": "cancelled",
                        "notes": f"Insufficient inventory for items: {', '.join(insufficient_items)}",
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            return False
        for order_item in order["items"]:
            for i, store_item in enumerate(main_store["items"]):
                if store_item["item_name"] == order_item["item_name"]:
                    new_quantity = store_item["current_quantity"] - order_item["quantity"]
                    
                    await self.mainstore_collection.update_one(
                        {
                            "_id": ObjectId(main_store["_id"]),
                            "items.item_name": order_item["item_name"]
                        },
                        {
                            "$set": {
                                "items.$.current_quantity": new_quantity,
                                "updated_at": datetime.now(timezone.utc)
                            }
                        }
                    )
                    break
        
        # Update order status to processing
        await self.orders_collection.update_one(
            {"_id": ObjectId(order_id)},
            {
                "$set": {
                    "status": "processing",
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return True
    
    async def get_main_store_orders(self, main_store_id: str) -> List[dict]:
        """Get all orders for a specific main store"""
        orders = []
        async for order in self.orders_collection.find({"main_store_id": main_store_id}):
            order["_id"] = str(order["_id"])
            orders.append(order)
        return orders