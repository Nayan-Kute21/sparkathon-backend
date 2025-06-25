from datetime import datetime, timezone
from typing import Optional, List, Annotated
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator
from bson import ObjectId

# Custom ObjectId validator
def validate_object_id(v):
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError('Invalid ObjectId')

PyObjectId = Annotated[ObjectId, BeforeValidator(validate_object_id)]

class CartItem(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True
    )
    
    item_id: PyObjectId
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

class Cart(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True
    )
    
    id: Optional[PyObjectId] = Field(default_factory=ObjectId, alias="_id")
    user_id: PyObjectId
    items: List[CartItem] = Field(default_factory=list)
    total_amount: float = Field(default=0.0, ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CartItemAdd(BaseModel):
    item_id: str
    quantity: int = Field(..., gt=0)

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)