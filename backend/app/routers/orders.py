# backend/app/routers/orders.py
import urllib.parse
from datetime import datetime, timezone
from fastapi import APIRouter, Depends

from app.db import get_db
from app.models.order import OrderCreate, OrderOut, OrderItem, OrderListItem
from app.dependencies import verify_token
from app.config import settings

router = APIRouter()

def _build_whatsapp_url(items: list[OrderItem], total: float) -> str:
    lines = ["Hola Lumière Beauty!", "", "Quisiera hacer el siguiente pedido:", ""]
    for item in items:
        subtotal = item.price * item.qty
        lines.append(f"• {item.qty}x {item.name} ({item.size}) — ${subtotal:.2f}")
    lines.extend(["", f"Total estimado: ${total:.2f}", "", "Gracias!"])
    message = "\n".join(lines)
    encoded = urllib.parse.quote(message)
    return f"https://wa.me/{settings.whatsapp_number}?text={encoded}"

@router.post("", response_model=OrderOut, status_code=201)
async def create_order(data: OrderCreate):
    db = get_db()
    whatsapp_url = _build_whatsapp_url(data.items, data.total)
    doc = {
        "items": [i.model_dump() for i in data.items],
        "total": data.total,
        "status": "whatsapp_sent",
        "whatsapp_url": whatsapp_url,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.orders.insert_one(doc)
    return OrderOut(
        order_id=str(result.inserted_id),
        whatsapp_url=whatsapp_url,
        total=data.total,
    )

@router.get("", response_model=list[OrderListItem])
async def list_orders(_: str = Depends(verify_token)):
    db = get_db()
    docs = await db.orders.find().sort("created_at", -1).to_list(length=50)
    result = []
    for doc in docs:
        doc["id"] = str(doc.pop("_id"))
        result.append(OrderListItem(**doc))
    return result
