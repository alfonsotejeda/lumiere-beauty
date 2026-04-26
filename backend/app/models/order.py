# backend/app/models/order.py
from pydantic import BaseModel
from typing import Literal
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
