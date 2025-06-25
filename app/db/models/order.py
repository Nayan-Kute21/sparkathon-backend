from datetime import datetime, timezone
from typing import Optional, List, Annotated
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator
from bson import ObjectId
from enum import Enum

# Custom ObjectId validator
def validate_object_id(v):
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError('Invalid ObjectId')

PyObjectId = Annotated[ObjectId, BeforeValidator(validate_object_id)]

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItem(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True
    )
    
    item_id: PyObjectId
    name: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    total: float = Field(..., gt=0)

class Order(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True
    )
    
    id: Optional[PyObjectId] = Field(default_factory=ObjectId, alias="_id")
    user_id: PyObjectId
    items: List[OrderItem]
    total_amount: float = Field(..., gt=0)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    shipping_address: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OrderCreate(BaseModel):
    shipping_address: str = Field(..., min_length=10)

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = Field(None, min_length=10)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))