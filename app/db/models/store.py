from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any
from datetime import datetime, timezone
from bson import ObjectId
from enum import Enum

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema: dict[str, Any]) -> dict[str, Any]:
        field_schema.update(type="string")
        return field_schema

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class StoreItem(BaseModel):
    item_name: str = Field(..., description="Name of the item")
    current_quantity: int = Field(..., ge=0, description="Current quantity in stock")
    max_quantity: int = Field(..., gt=0, description="Maximum quantity capacity")
    unit: Optional[str] = Field("pcs", description="Unit of measurement")
    price: Optional[float] = Field(None, ge=0, description="Price per unit")
    category: Optional[str] = Field(None, description="Item category")

class Store(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    store_name: str = Field(..., description="Name of the store")
    store_address: str = Field(..., description="Store address")
    store_phone: Optional[str] = Field(None, description="Store contact number")
    store_email: Optional[str] = Field(None, description="Store email")
    owner_name: str = Field(..., description="Store owner name")
    store_type: Optional[str] = Field("General", description="Type of store")
    items: List[StoreItem] = Field(default_factory=list, description="List of store items")
    is_active: bool = Field(True, description="Store status")
    
    # Economic, Political, and Environmental factors
    economic_conditions: Optional[SeverityLevel] = Field(None, description="Current economic conditions affecting the store")
    economic_notes: Optional[str] = Field(None, description="Additional notes about economic conditions")
    political_instability: Optional[SeverityLevel] = Field(None, description="Level of political instability in the area")
    political_notes: Optional[str] = Field(None, description="Additional notes about political situation")
    environmental_issues: Optional[SeverityLevel] = Field(None, description="Environmental issues affecting the store")
    environmental_notes: Optional[str] = Field(None, description="Additional notes about environmental issues")
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StoreCreate(BaseModel):
    store_name: str
    store_address: str
    store_phone: Optional[str] = None
    store_email: Optional[str] = None
    owner_name: str
    store_type: Optional[str] = "General"
    items: List[StoreItem] = []
    economic_conditions: Optional[SeverityLevel] = None
    economic_notes: Optional[str] = None
    political_instability: Optional[SeverityLevel] = None
    political_notes: Optional[str] = None
    environmental_issues: Optional[SeverityLevel] = None
    environmental_notes: Optional[str] = None

class StoreUpdate(BaseModel):
    store_name: Optional[str] = None
    store_address: Optional[str] = None
    store_phone: Optional[str] = None
    store_email: Optional[str] = None
    owner_name: Optional[str] = None
    store_type: Optional[str] = None
    items: Optional[List[StoreItem]] = None
    is_active: Optional[bool] = None
    economic_conditions: Optional[SeverityLevel] = None
    economic_notes: Optional[str] = None
    political_instability: Optional[SeverityLevel] = None
    political_notes: Optional[str] = None
    environmental_issues: Optional[SeverityLevel] = None
    environmental_notes: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ItemCreate(BaseModel):
    item_name: str
    current_quantity: int = Field(..., ge=0)
    max_quantity: int = Field(..., gt=0)
    unit: Optional[str] = "pcs"
    price: Optional[float] = Field(None, ge=0)
    category: Optional[str] = None