# backend/app/models/order.py
from pydantic import BaseModel
from datetime import datetime

class OrderItem(BaseModel):
    product_id: str
    name: str
    price: float
    qty: int
    size: str

class OrderCreate(BaseModel):
    items: list[OrderItem]
    total: float

class OrderOut(BaseModel):
    order_id: str
    whatsapp_url: str
    total: float

class OrderListItem(BaseModel):
    id: str
    items: list[OrderItem]
    total: float
    status: str
    whatsapp_url: str
    created_at: datetime
