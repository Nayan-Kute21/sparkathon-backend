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

class Item(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True
    )
    
    id: Optional[PyObjectId] = Field(default_factory=ObjectId, alias="_id")
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=1000)
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=1)
    brand: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    stock_quantity: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=1000)
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=1)
    brand: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    stock_quantity: int = Field(default=0, ge=0)

class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1)
    brand: Optional[str] = None
    images: Optional[List[str]] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))