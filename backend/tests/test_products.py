import pytest
from httpx import AsyncClient

PRODUCT = {
    "name": "Test Collagen",
    "brand": "Nutriplus",
    "category": "salud",
    "description": "Colágeno hidrolizado de prueba",
    "price": 29.99,
    "size": "250g",
    "badge": "bestseller",
    "in_stock": True,
    "image_url": "http://localhost:8000/static/images/test.jpg",
}

@pytest.mark.asyncio
async def test_list_products_empty(client: AsyncClient):
    resp = await client.get("/products")
    assert resp.status_code == 200
    assert resp.json() == []

@pytest.mark.asyncio
async def test_create_product_without_auth_returns_403(client: AsyncClient):
    resp = await client.post("/products", json=PRODUCT)
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_create_product(client: AsyncClient, auth_headers):
    resp = await client.post("/products", json=PRODUCT, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Collagen"
    assert data["price"] == 29.99
    assert "id" in data

@pytest.mark.asyncio
async def test_list_products_returns_created(client: AsyncClient, auth_headers):
    await client.post("/products", json=PRODUCT, headers=auth_headers)
    resp = await client.get("/products")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "Test Collagen"

@pytest.mark.asyncio
async def test_get_product_by_id(client: AsyncClient, auth_headers):
    create_resp = await client.post("/products", json=PRODUCT, headers=auth_headers)
    pid = create_resp.json()["id"]
    resp = await client.get(f"/products/{pid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == pid

@pytest.mark.asyncio
async def test_get_product_not_found(client: AsyncClient):
    resp = await client.get("/products/000000000000000000000000")
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_update_product(client: AsyncClient, auth_headers):
    create_resp = await client.post("/products", json=PRODUCT, headers=auth_headers)
    pid = create_resp.json()["id"]
    updated = {**PRODUCT, "price": 39.99, "badge": "oferta"}
    resp = await client.put(f"/products/{pid}", json=updated, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["price"] == 39.99

@pytest.mark.asyncio
async def test_delete_product(client: AsyncClient, auth_headers):
    create_resp = await client.post("/products", json=PRODUCT, headers=auth_headers)
    pid = create_resp.json()["id"]
    resp = await client.delete(f"/products/{pid}", headers=auth_headers)
    assert resp.status_code == 204
    assert (await client.get(f"/products/{pid}")).status_code == 404
