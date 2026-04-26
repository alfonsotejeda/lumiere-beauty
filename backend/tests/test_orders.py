# backend/tests/test_orders.py
import pytest
from httpx import AsyncClient
from app.db import get_db

ITEMS = [
    {"product_id": "507f1f77bcf86cd799439011", "name": "Beauty Booster Collagen",
     "price": 34.99, "qty": 2, "size": "250g"},
    {"product_id": "507f1f77bcf86cd799439012", "name": "Aloe Glow",
     "price": 18.99, "qty": 1, "size": "450ml"},
]

@pytest.mark.asyncio
async def test_create_order_returns_whatsapp_url(client: AsyncClient):
    resp = await client.post("/orders", json={"items": ITEMS, "total": 88.97})
    assert resp.status_code == 201
    data = resp.json()
    assert "order_id" in data
    assert "whatsapp_url" in data
    assert "wa.me" in data["whatsapp_url"]
    assert data["total"] == 88.97

@pytest.mark.asyncio
async def test_whatsapp_url_contains_product_name(client: AsyncClient):
    resp = await client.post("/orders", json={"items": ITEMS, "total": 88.97})
    url = resp.json()["whatsapp_url"]
    assert "Beauty" in url

@pytest.mark.asyncio
async def test_order_saved_to_db(client: AsyncClient):
    await client.post("/orders", json={"items": ITEMS, "total": 88.97})
    db = get_db()
    count = await db.orders.count_documents({"status": "whatsapp_sent"})
    assert count == 1

@pytest.mark.asyncio
async def test_list_orders_requires_auth(client: AsyncClient):
    resp = await client.get("/orders")
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_list_orders_with_auth(client: AsyncClient, auth_headers):
    await client.post("/orders", json={"items": ITEMS, "total": 88.97})
    resp = await client.get("/orders", headers=auth_headers)
    assert resp.status_code == 200
    orders = resp.json()
    assert len(orders) == 1
    order = orders[0]
    assert order["status"] == "whatsapp_sent"
    assert {"id", "items", "total", "status", "whatsapp_url", "created_at"} <= order.keys()
