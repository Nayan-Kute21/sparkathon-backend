from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any
from datetime import datetime, timezone
from bson import ObjectId
from enum import Enum
from app.db.models.store import PyObjectId, SeverityLevel

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItem(BaseModel):
    item_name: str = Field(..., description="Name of the item")
    quantity: int = Field(..., gt=0, description="Quantity ordered")
    unit: Optional[str] = Field("pcs", description="Unit of measurement")
    price: Optional[float] = Field(None, ge=0, description="Price per unit")
    category: Optional[str] = Field(None, description="Item category")

class MainStoreItem(BaseModel):
    item_name: str = Field(..., description="Name of the item")
    current_quantity: int = Field(..., ge=0, description="Current quantity in stock")
    max_quantity: int = Field(..., gt=0, description="Maximum quantity capacity")
    unit: Optional[str] = Field("pcs", description="Unit of measurement")
    price: Optional[float] = Field(None, ge=0, description="Price per unit")
    category: Optional[str] = Field(None, description="Item category")

class Order(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    store_id: str = Field(..., description="ID of the store placing the order")
    store_name: str = Field(..., description="Name of the store placing the order")
    items: List[OrderItem] = Field(..., description="List of items ordered")
    total_amount: Optional[float] = Field(0.0, description="Total order amount")
    status: OrderStatus = Field(OrderStatus.PENDING, description="Current status of the order")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = Field(None, description="Additional notes for the order")

class MainStore(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="Name of the main store")
    location: str = Field(..., description="Location of the main store")
    manager: str = Field(..., description="Name of the manager")
    items: List[MainStoreItem] = Field(default_factory=list, description="Inventory of items")
    
    # Economic, Political, and Environmental factors
    economic_conditions: Optional[SeverityLevel] = Field(None, description="Current economic conditions")
    economic_notes: Optional[str] = Field(None, description="Notes about economic conditions")
    political_instability: Optional[SeverityLevel] = Field(None, description="Level of political instability")
    political_notes: Optional[str] = Field(None, description="Notes about political situation")
    environmental_issues: Optional[SeverityLevel] = Field(None, description="Environmental issues")
    environmental_notes: Optional[str] = Field(None, description="Notes about environmental issues")
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OrderCreate(BaseModel):
    store_id: str = Field(..., description="ID of the store placing the order")
    store_name: str = Field(..., description="Name of the store placing the order")
    main_store_id: str = Field(..., description="ID of the main store fulfilling the order")
    items: List[OrderItem]
    notes: Optional[str] = None

class Order(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    store_id: str = Field(..., description="ID of the store placing the order")
    store_name: str = Field(..., description="Name of the store placing the order")
    main_store_id: str = Field(..., description="ID of the main store fulfilling the order")
    items: List[OrderItem] = Field(..., description="List of items ordered")
    total_amount: Optional[float] = Field(0.0, description="Total order amount")
    status: OrderStatus = Field(OrderStatus.PENDING, description="Current status of the order")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = Field(None, description="Additional notes for the order")

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MainStoreCreate(BaseModel):
    name: str
    location: str
    manager: str
    items: List[MainStoreItem] = []
    economic_conditions: Optional[SeverityLevel] = None
    economic_notes: Optional[str] = None
    political_instability: Optional[SeverityLevel] = None
    political_notes: Optional[str] = None
    environmental_issues: Optional[SeverityLevel] = None
    environmental_notes: Optional[str] = None

class MainStoreUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    manager: Optional[str] = None
    economic_conditions: Optional[SeverityLevel] = None
    economic_notes: Optional[str] = None
    political_instability: Optional[SeverityLevel] = None
    political_notes: Optional[str] = None
    environmental_issues: Optional[SeverityLevel] = None
    environmental_notes: Optional[str] = Field(None, description="Notes about environmental issues")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))