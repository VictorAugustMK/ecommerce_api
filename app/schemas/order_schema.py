from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    client_id: int
    items: List[OrderItemCreate]

class OrderItemOut(OrderItemCreate):
    id: UUID
    unit_price: float

    model_config = ConfigDict(from_attributes=True)

class OrderOut(BaseModel):
    id: UUID
    client_id: int
    status: OrderStatus
    created_at: datetime
    items: List[OrderItemOut]
    total_price: float

    model_config = ConfigDict(from_attributes=True)

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None

    model_config = ConfigDict(from_attributes=True)
