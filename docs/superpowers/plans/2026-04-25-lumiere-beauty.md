# Lumière Beauty — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir el catálogo web completo de Lumière Beauty con FastAPI, React+Vite, MongoDB y Valkey — ejecutable localmente con Docker Compose, diseñado para producción.

**Architecture:** FastAPI sirve productos (cacheados en Valkey 10 min) y guarda pedidos WhatsApp en MongoDB. React tiene un carrito Zustand en memoria; al hacer checkout llama al backend y abre wa.me. El admin gestiona productos con Bearer token.

**Tech Stack:** Python 3.12 · FastAPI · Motor (async MongoDB) · redis-py (Valkey) · React 18 · Vite 5 · Zustand · Docker Compose · GitHub CLI

---

## Mapa de archivos

```
lumiere-beauty/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py          ← pydantic-settings: MONGO_URL, ADMIN_TOKEN, etc.
│   │   ├── main.py            ← FastAPI app, CORS, lifespan, rutas montadas
│   │   ├── db.py              ← Motor client (connect/close/get_db)
│   │   ├── cache.py           ← Valkey client (get/set/delete)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── product.py     ← ProductCreate, ProductOut, product_from_doc()
│   │   │   └── order.py       ← OrderItem, OrderCreate, OrderOut
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── products.py    ← GET/POST/PUT/DELETE /products
│   │   │   └── orders.py      ← POST /orders, GET /orders (admin)
│   │   └── seed.py            ← Script de datos iniciales
│   ├── static/
│   │   └── images/
│   │       └── .gitkeep
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py        ← fixtures: client, auth_headers, clean_collections
│       ├── test_products.py
│       └── test_orders.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── index.css              ← Variables CSS, reset, fuentes
        ├── store/
        │   └── cartStore.js       ← Zustand: items, addItem, removeItem, updateQty, clearCart
        ├── api/
        │   ├── products.js        ← fetchProducts(), fetchProduct(id)
        │   └── orders.js          ← createOrder(items, total)
        ├── hooks/
        │   └── useCartWarning.js  ← beforeunload cuando carrito tiene items
        ├── components/
        │   ├── ProductCard.jsx
        │   ├── Cart.jsx           ← Panel lateral deslizante
        │   ├── CartButton.jsx     ← Botón flotante con contador
        │   └── CheckoutButton.jsx ← Llama a POST /orders, abre wa.me
        └── pages/
            └── Catalog.jsx        ← Tabs por categoría + grid de productos
```

---

## Task 1: GitHub repo + estructura inicial del proyecto

**Files:**
- Create: `.gitignore`
- Create: `README.md` (mínimo)
- Create: estructura de directorios

- [ ] **Step 1: Crear el repositorio en GitHub**

```bash
cd /Users/alfonso/Documents/mama/lumiere-beauty
gh repo create alfonsotejeda/lumiere-beauty --public --source=. --remote=origin
```

- [ ] **Step 2: Crear .gitignore**

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
.venv/
*.egg-info/
.pytest_cache/
.coverage

# Node
node_modules/
dist/
.vite/

# Env
.env
*.env.local

# OS
.DS_Store

# Docker
*.log
EOF
```

- [ ] **Step 3: Crear estructura de directorios**

```bash
mkdir -p backend/app/models backend/app/routers backend/tests backend/static/images
mkdir -p frontend/src/store frontend/src/api frontend/src/hooks
mkdir -p frontend/src/components frontend/src/pages
touch backend/app/__init__.py backend/app/models/__init__.py
touch backend/app/routers/__init__.py backend/tests/__init__.py
touch backend/static/images/.gitkeep
```

- [ ] **Step 4: Commit inicial**

```bash
git add .
git commit -m "chore: initial project structure"
git push -u origin main
```

Expected: repo visible en github.com/alfonsotejeda/lumiere-beauty

---

## Task 2: Docker Compose con MongoDB y Valkey

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`

- [ ] **Step 1: Crear docker-compose.yml**

```yaml
# docker-compose.yml
version: '3.9'

services:
  mongodb:
    image: mongo:7
    container_name: lumiere-mongodb
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    restart: unless-stopped

  valkey:
    image: valkey/valkey:7
    container_name: lumiere-valkey
    ports:
      - "6379:6379"
    restart: unless-stopped

  backend:
    build: ./backend
    container_name: lumiere-backend
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - mongodb
      - valkey
    volumes:
      - ./backend:/app
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: lumiere-frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    restart: unless-stopped

volumes:
  mongo_data:
```

- [ ] **Step 2: Crear .env.example**

```bash
cat > .env.example << 'EOF'
MONGO_URL=mongodb://mongodb:27017
MONGO_DB=lumiere
VALKEY_URL=redis://valkey:6379
ADMIN_TOKEN=cambia-este-token-secreto
WHATSAPP_NUMBER=+1XXXXXXXXXX
CACHE_TTL_SECONDS=600
IMAGES_BASE_URL=http://localhost:8000/static/images
EOF
```

- [ ] **Step 3: Crear .env real (no va al repo)**

```bash
cp .env.example .env
# Editar .env con el número de WhatsApp real y el token deseado
```

- [ ] **Step 4: Arrancar los servicios de infraestructura y verificar**

```bash
docker compose up mongodb valkey -d
docker compose ps
```

Expected output:
```
NAME                STATUS
lumiere-mongodb     running
lumiere-valkey      running
```

- [ ] **Step 5: Verificar conectividad**

```bash
# MongoDB
docker exec lumiere-mongodb mongosh --eval "db.adminCommand('ping')"
# Expected: { ok: 1 }

# Valkey
docker exec lumiere-valkey valkey-cli ping
# Expected: PONG
```

- [ ] **Step 6: Commit**

```bash
git add docker-compose.yml .env.example
git commit -m "feat: add docker-compose with MongoDB and Valkey"
git push
```

---

## Task 3: Backend — Dockerfile, requirements y skeleton FastAPI

**Files:**
- Create: `backend/Dockerfile`
- Create: `backend/requirements.txt`
- Create: `backend/pytest.ini`
- Create: `backend/app/config.py`
- Create: `backend/app/db.py`
- Create: `backend/app/cache.py`
- Create: `backend/app/main.py`

- [ ] **Step 1: Crear requirements.txt**

```
# backend/requirements.txt
fastapi==0.111.0
uvicorn[standard]==0.29.0
motor==3.4.0
redis==5.0.4
pydantic==2.7.1
pydantic-settings==2.2.1
python-dotenv==1.0.1
httpx==0.27.0
pytest==8.2.0
pytest-asyncio==0.23.6
```

- [ ] **Step 2: Crear Dockerfile**

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

- [ ] **Step 3: Crear pytest.ini**

```ini
# backend/pytest.ini
[pytest]
asyncio_mode = auto
```

- [ ] **Step 4: Crear app/config.py**

```python
# backend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db: str = "lumiere"
    valkey_url: str = "redis://localhost:6379"
    admin_token: str = "dev-token-change-me"
    whatsapp_number: str = "+1XXXXXXXXXX"
    cache_ttl_seconds: int = 600
    images_base_url: str = "http://localhost:8000/static/images"

    class Config:
        env_file = ".env"

settings = Settings()
```

- [ ] **Step 5: Crear app/db.py**

```python
# backend/app/db.py
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

_client: AsyncIOMotorClient | None = None

async def connect_db() -> None:
    global _client
    _client = AsyncIOMotorClient(settings.mongo_url)

async def close_db() -> None:
    global _client
    if _client:
        _client.close()
        _client = None

def get_db() -> AsyncIOMotorDatabase:
    return _client[settings.mongo_db]
```

- [ ] **Step 6: Crear app/cache.py**

```python
# backend/app/cache.py
import json
import redis.asyncio as redis
from app.config import settings

_redis: redis.Redis | None = None

async def connect_cache() -> None:
    global _redis
    _redis = redis.from_url(settings.valkey_url, decode_responses=True)

async def close_cache() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None

async def cache_get(key: str) -> dict | list | None:
    if not _redis:
        return None
    value = await _redis.get(key)
    return json.loads(value) if value else None

async def cache_set(key: str, value: dict | list, ttl: int | None = None) -> None:
    if not _redis:
        return
    await _redis.set(key, json.dumps(value, default=str), ex=ttl or settings.cache_ttl_seconds)

async def cache_delete(key: str) -> None:
    if not _redis:
        return
    await _redis.delete(key)
```

- [ ] **Step 7: Crear app/main.py (skeleton sin routers aún)**

```python
# backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db import connect_db, close_db
from app.cache import connect_cache, close_cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    await connect_cache()
    yield
    await close_db()
    await close_cache()

app = FastAPI(title="Lumière Beauty API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 8: Instalar dependencias localmente para el IDE**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- [ ] **Step 9: Verificar que el servidor arranca**

```bash
# Asegúrate de que MongoDB y Valkey corren (docker compose up mongodb valkey -d)
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload
# En otro terminal:
curl http://localhost:8000/health
```

Expected: `{"status":"ok"}`

- [ ] **Step 10: Commit**

```bash
git add backend/
git commit -m "feat: FastAPI skeleton with MongoDB Motor and Valkey cache"
git push
```

---

## Task 4: Backend — Modelo de producto + tests + router

**Files:**
- Create: `backend/app/models/product.py`
- Create: `backend/app/routers/products.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_products.py`
- Modify: `backend/app/main.py` (agregar router)

- [ ] **Step 1: Crear app/models/product.py**

```python
# backend/app/models/product.py
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

Badge = Literal["bestseller", "nuevo", "oferta", "popular", "recomendado"]
Category = Literal["skincare", "cabello", "corporal", "maquillaje", "salud"]

class ProductCreate(BaseModel):
    name: str
    brand: str
    category: Category
    description: str
    price: float
    size: str
    badge: Optional[Badge] = None
    in_stock: bool = True
    image_url: str

class ProductOut(ProductCreate):
    id: str
    created_at: datetime

def product_from_doc(doc: dict) -> ProductOut:
    """Convierte un documento MongoDB a ProductOut."""
    doc = dict(doc)
    doc["id"] = str(doc.pop("_id"))
    return ProductOut(**doc)
```

- [ ] **Step 2: Crear tests/conftest.py**

```python
# backend/tests/conftest.py
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Setear variables antes de importar la app
os.environ["MONGO_DB"] = "lumiere_test"
os.environ["ADMIN_TOKEN"] = "test-token"
os.environ["WHATSAPP_NUMBER"] = "+1234567890"
os.environ["MONGO_URL"] = "mongodb://localhost:27017"
os.environ["VALKEY_URL"] = "redis://localhost:6379"

from app.main import app
from app.db import connect_db, get_db
from app.cache import connect_cache, close_cache

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_services():
    await connect_db()
    await connect_cache()
    yield
    await close_cache()

@pytest_asyncio.fixture(autouse=True)
async def clean_collections():
    yield
    db = get_db()
    await db.products.drop()
    await db.orders.drop()

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

@pytest_asyncio.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}
```

- [ ] **Step 3: Escribir tests/test_products.py (primero los tests)**

```python
# backend/tests/test_products.py
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
```

- [ ] **Step 4: Ejecutar tests — deben fallar**

```bash
cd backend && source .venv/bin/activate
pytest tests/test_products.py -v
```

Expected: `ImportError` o `404` (routers no existen aún)

- [ ] **Step 5: Crear app/routers/products.py**

```python
# backend/app/routers/products.py
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
from app.db import get_db
from app.cache import cache_get, cache_set, cache_delete
from app.models.product import ProductCreate, ProductOut, product_from_doc
from app.config import settings

router = APIRouter()
_security = HTTPBearer()

CACHE_ALL = "products:all"

def _cache_one(pid: str) -> str:
    return f"products:{pid}"

def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> str:
    if credentials.credentials != settings.admin_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return credentials.credentials

@router.get("", response_model=list[ProductOut])
async def list_products():
    cached = await cache_get(CACHE_ALL)
    if cached:
        return cached
    db = get_db()
    docs = await db.products.find({"in_stock": True}).to_list(length=None)
    products = [product_from_doc(d).model_dump() for d in docs]
    await cache_set(CACHE_ALL, products)
    return products

@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: str):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    cached = await cache_get(_cache_one(product_id))
    if cached:
        return cached
    db = get_db()
    doc = await db.products.find_one({"_id": ObjectId(product_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")
    product = product_from_doc(doc)
    await cache_set(_cache_one(product_id), product.model_dump())
    return product

@router.post("", response_model=ProductOut, status_code=201)
async def create_product(data: ProductCreate, _: str = Depends(verify_token)):
    db = get_db()
    doc = data.model_dump()
    doc["created_at"] = datetime.now(timezone.utc)
    result = await db.products.insert_one(doc)
    doc["_id"] = result.inserted_id
    await cache_delete(CACHE_ALL)
    return product_from_doc(doc)

@router.put("/{product_id}", response_model=ProductOut)
async def update_product(product_id: str, data: ProductCreate, _: str = Depends(verify_token)):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    db = get_db()
    result = await db.products.find_one_and_update(
        {"_id": ObjectId(product_id)},
        {"$set": data.model_dump()},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    await cache_delete(CACHE_ALL)
    await cache_delete(_cache_one(product_id))
    return product_from_doc(result)

@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: str, _: str = Depends(verify_token)):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    db = get_db()
    result = await db.products.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    await cache_delete(CACHE_ALL)
    await cache_delete(_cache_one(product_id))
```

- [ ] **Step 6: Registrar router en main.py**

Añadir al final de los imports y antes del endpoint /health:
```python
# backend/app/main.py — añadir imports:
from app.routers import products as products_router

# añadir después del middleware:
app.include_router(products_router.router, prefix="/products", tags=["products"])
```

- [ ] **Step 7: Ejecutar tests — deben pasar**

```bash
pytest tests/test_products.py -v
```

Expected:
```
PASSED tests/test_products.py::test_list_products_empty
PASSED tests/test_products.py::test_create_product_without_auth_returns_403
PASSED tests/test_products.py::test_create_product
PASSED tests/test_products.py::test_list_products_returns_created
PASSED tests/test_products.py::test_get_product_by_id
PASSED tests/test_products.py::test_get_product_not_found
PASSED tests/test_products.py::test_update_product
PASSED tests/test_products.py::test_delete_product
8 passed
```

- [ ] **Step 8: Commit**

```bash
git add backend/
git commit -m "feat: product model, CRUD router and tests"
git push
```

---

## Task 5: Backend — Modelo de pedido + router WhatsApp + tests

**Files:**
- Create: `backend/app/models/order.py`
- Create: `backend/app/routers/orders.py`
- Create: `backend/tests/test_orders.py`
- Modify: `backend/app/main.py` (agregar router orders)

- [ ] **Step 1: Crear app/models/order.py**

```python
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
```

- [ ] **Step 2: Escribir tests/test_orders.py primero**

```python
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
    assert len(resp.json()) == 1
    assert resp.json()[0]["status"] == "whatsapp_sent"
```

- [ ] **Step 3: Ejecutar tests — deben fallar**

```bash
pytest tests/test_orders.py -v
```

Expected: ImportError o 404 (router no existe)

- [ ] **Step 4: Crear app/routers/orders.py**

```python
# backend/app/routers/orders.py
import urllib.parse
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.db import get_db
from app.models.order import OrderCreate, OrderOut, OrderItem
from app.config import settings

router = APIRouter()
_security = HTTPBearer()

def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> str:
    if credentials.credentials != settings.admin_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return credentials.credentials

def _build_whatsapp_url(items: list[OrderItem], total: float) -> str:
    lines = ["Hola Lumière Beauty! 🌿", "", "Quisiera hacer el siguiente pedido:", ""]
    for item in items:
        subtotal = item.price * item.qty
        lines.append(f"• {item.qty}x {item.name} ({item.size}) — ${subtotal:.2f}")
    lines.extend(["", f"💰 Total estimado: ${total:.2f}", "", "Gracias!"])
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

@router.get("", response_model=list[dict])
async def list_orders(_: str = Depends(verify_token)):
    db = get_db()
    docs = await db.orders.find().sort("created_at", -1).to_list(length=50)
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return docs
```

- [ ] **Step 5: Registrar router en main.py**

```python
# backend/app/main.py — añadir:
from app.routers import orders as orders_router
app.include_router(orders_router.router, prefix="/orders", tags=["orders"])
```

- [ ] **Step 6: Ejecutar todos los tests**

```bash
pytest tests/ -v
```

Expected: 13 tests passed

- [ ] **Step 7: Commit**

```bash
git add backend/
git commit -m "feat: order model, WhatsApp URL builder and tests"
git push
```

---

## Task 6: Backend — Script seed con productos reales

**Files:**
- Create: `backend/app/seed.py`

- [ ] **Step 1: Crear seed.py con los productos del catálogo Nutriplus**

```python
# backend/app/seed.py
import asyncio
from datetime import datetime, timezone
from app.db import connect_db, get_db
from app.config import settings

PRODUCTS = [
    # ── Calming Glow System (Belleza + Serenidad) ──
    {
        "name": "Aloe Glow",
        "brand": "Nutriplus by Farmasi",
        "category": "salud",
        "description": (
            "Bebida de aloe vera con sabor a mandarina. "
            "40% jugo de hoja de aloe, extracto de manzanilla, "
            "endulzado con stevia. 0 calorías por porción (15ml). "
            "Apoya la hidratación calmante y el confort digestivo."
        ),
        "price": 18.99,
        "size": "450 ml",
        "badge": "bestseller",
        "in_stock": True,
        "image_url": f"{settings.images_base_url}/aloe-glow.jpg",
    },
    {
        "name": "Serenity Lemon Tea",
        "brand": "Nutriplus by Farmasi",
        "category": "salud",
        "description": (
            "Té de limón sin cafeína con extracto de té negro, té verde, "
            "cardamomo, malva e hibisco. 6 calorías por sobre (1.7g). "
            "Ayuda a liberar tensiones y apoyar el equilibrio nocturno."
        ),
        "price": 22.99,
        "size": "30 sobres (1.7 g c/u)",
        "badge": "nuevo",
        "in_stock": True,
        "image_url": f"{settings.images_base_url}/serenity-lemon-tea.jpg",
    },
    {
        "name": "Beauty Booster Collagen",
        "brand": "Nutriplus by Farmasi",
        "category": "salud",
        "description": (
            "10,000 mg de colágeno hidrolizado con ácido hialurónico (50mg) "
            "y vitamina C (80mg). 40 calorías, 10g proteína por scoop (10g). "
            "Apoya la firmeza, elasticidad e hidratación profunda de la piel."
        ),
        "price": 34.99,
        "size": "250 g",
        "badge": "bestseller",
        "in_stock": True,
        "image_url": f"{settings.images_base_url}/beauty-booster-collagen.jpg",
    },
    {
        "name": "Restore",
        "brand": "Nutriplus by Farmasi",
        "category": "salud",
        "description": (
            "Mezcla de electrolitos y minerales: magnesio (134mg), zinc (10mg), "
            "vitamina D (7.5mcg), calcio (268mg), hierro, selenio y cromo. "
            "24 calorías por porción (8g). Apoya la relajación nocturna."
        ),
        "price": 28.99,
        "size": "240 g",
        "badge": None,
        "in_stock": True,
        "image_url": f"{settings.images_base_url}/restore.jpg",
    },
    # ── Morning Glow System (Belleza + Energía) ──
    {
        "name": "Morning Glow Collagen",
        "brand": "Nutriplus by Farmasi",
        "category": "salud",
        "description": (
            "Sistema matutino de colágeno con energizantes naturales. "
            "Apoya la vitalidad, el brillo y la energía desde el inicio del día."
        ),
        "price": 32.99,
        "size": "250 g",
        "badge": "nuevo",
        "in_stock": True,
        "image_url": f"{settings.images_base_url}/morning-glow-collagen.jpg",
    },
    {
        "name": "Energy Boost Drink",
        "brand": "Nutriplus by Farmasi",
        "category": "salud",
        "description": (
            "Bebida energizante matutina parte del Morning Glow System. "
            "Formulada para impulsar el metabolismo y la concentración."
        ),
        "price": 19.99,
        "size": "450 ml",
        "badge": "nuevo",
        "in_stock": True,
        "image_url": f"{settings.images_base_url}/energy-boost.jpg",
    },
    # ── Pre-workout ──
    {
        "name": "Nutriplus Pre-workout",
        "brand": "Nutriplus by Farmasi",
        "category": "salud",
        "description": (
            "Suplemento pre-entrenamiento con ingredientes activos para "
            "potenciar el rendimiento, la fuerza y la energía durante el ejercicio."
        ),
        "price": 39.99,
        "size": "300 g",
        "badge": "nuevo",
        "in_stock": True,
        "image_url": f"{settings.images_base_url}/preworkout.jpg",
    },
]

async def seed() -> None:
    await connect_db()
    db = get_db()
    count = await db.products.count_documents({})
    if count > 0:
        print(f"⚠️  La base de datos ya tiene {count} productos. Seed omitido.")
        return
    for product in PRODUCTS:
        product["created_at"] = datetime.now(timezone.utc)
    result = await db.products.insert_many(PRODUCTS)
    print(f"✅ {len(result.inserted_ids)} productos cargados.")

if __name__ == "__main__":
    asyncio.run(seed())
```

- [ ] **Step 2: Ejecutar seed**

```bash
cd backend && source .venv/bin/activate
python -m app.seed
```

Expected: `✅ 7 productos cargados.`

- [ ] **Step 3: Verificar en la API**

```bash
curl http://localhost:8000/products | python -m json.tool | head -30
```

Expected: array con 7 productos en JSON

- [ ] **Step 4: Commit**

```bash
git add backend/app/seed.py
git commit -m "feat: seed script with Nutriplus product catalog"
git push
```

---

## Task 7: Frontend — Scaffold React + Vite + dependencias

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/Dockerfile`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/App.jsx` (placeholder)
- Create: `frontend/src/index.css`

- [ ] **Step 1: Crear el proyecto Vite**

```bash
cd /Users/alfonso/Documents/mama/lumiere-beauty
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

- [ ] **Step 2: Instalar dependencias**

```bash
cd frontend
npm install zustand
```

- [ ] **Step 3: Actualizar vite.config.js para proxy al backend**

```js
// frontend/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

- [ ] **Step 4: Crear frontend/Dockerfile**

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
```

- [ ] **Step 5: Verificar que Vite arranca**

```bash
cd frontend && npm run dev
```

Expected: `VITE v5.x.x  ready in Xms — Local: http://localhost:5173/`

- [ ] **Step 6: Commit**

```bash
cd ..
git add frontend/
git commit -m "feat: React + Vite scaffold with Zustand"
git push
```

---

## Task 8: Frontend — Zustand cart store

**Files:**
- Create: `frontend/src/store/cartStore.js`

- [ ] **Step 1: Crear cartStore.js**

```js
// frontend/src/store/cartStore.js
import { create } from 'zustand'

const useCartStore = create((set, get) => ({
  items: [],

  addItem: (product) =>
    set((state) => {
      const existing = state.items.find((i) => i.id === product.id)
      if (existing) {
        return {
          items: state.items.map((i) =>
            i.id === product.id ? { ...i, qty: i.qty + 1 } : i
          ),
        }
      }
      return { items: [...state.items, { ...product, qty: 1 }] }
    }),

  removeItem: (id) =>
    set((state) => ({ items: state.items.filter((i) => i.id !== id) })),

  updateQty: (id, qty) =>
    set((state) => ({
      items:
        qty <= 0
          ? state.items.filter((i) => i.id !== id)
          : state.items.map((i) => (i.id === id ? { ...i, qty } : i)),
    })),

  clearCart: () => set({ items: [] }),

  getTotal: () =>
    get().items.reduce((sum, i) => sum + i.price * i.qty, 0),

  getCount: () =>
    get().items.reduce((sum, i) => sum + i.qty, 0),
}))

export default useCartStore
```

- [ ] **Step 2: Verificar manualmente en consola**

Abrir DevTools en `http://localhost:5173`, ejecutar:
```js
// En consola del navegador — temporal para verificar
import('/src/store/cartStore.js').then(m => {
  const store = m.default.getState()
  store.addItem({ id: '1', name: 'Test', price: 10, size: '100g' })
  console.log(m.default.getState().items) // debe mostrar [{...qty:1}]
  console.log(m.default.getState().getTotal()) // debe mostrar 10
})
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/store/
git commit -m "feat: Zustand cart store with add/remove/update/clear"
git push
```

---

## Task 9: Frontend — API client

**Files:**
- Create: `frontend/src/api/products.js`
- Create: `frontend/src/api/orders.js`

- [ ] **Step 1: Crear api/products.js**

```js
// frontend/src/api/products.js
const BASE = '/api'

export async function fetchProducts() {
  const res = await fetch(`${BASE}/products`)
  if (!res.ok) throw new Error('Error al cargar productos')
  return res.json()
}

export async function fetchProduct(id) {
  const res = await fetch(`${BASE}/products/${id}`)
  if (!res.ok) throw new Error('Producto no encontrado')
  return res.json()
}
```

- [ ] **Step 2: Crear api/orders.js**

```js
// frontend/src/api/orders.js
const BASE = '/api'

export async function createOrder(items, total) {
  const body = {
    items: items.map((i) => ({
      product_id: i.id,
      name: i.name,
      price: i.price,
      qty: i.qty,
      size: i.size,
    })),
    total,
  }
  const res = await fetch(`${BASE}/orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error('Error al procesar el pedido')
  return res.json()
}
```

- [ ] **Step 3: Verificar fetchProducts en navegador**

Con el backend corriendo (`uvicorn app.main:app --reload` en `/backend`):
```js
// DevTools > Console
fetch('/api/products').then(r => r.json()).then(console.log)
```

Expected: array con los 7 productos del seed

- [ ] **Step 4: Commit**

```bash
git add frontend/src/api/
git commit -m "feat: API client for products and orders"
git push
```

---

## Task 10: Frontend — Hook useCartWarning

**Files:**
- Create: `frontend/src/hooks/useCartWarning.js`

- [ ] **Step 1: Crear hooks/useCartWarning.js**

```js
// frontend/src/hooks/useCartWarning.js
import { useEffect } from 'react'
import useCartStore from '../store/cartStore'

/**
 * Muestra una advertencia del navegador si el usuario intenta
 * cerrar/recargar la pestaña cuando hay items en el carrito.
 * Se desactiva automáticamente cuando el carrito está vacío.
 */
export function useCartWarning() {
  const count = useCartStore((s) => s.getCount())

  useEffect(() => {
    if (count === 0) return

    const handler = (e) => {
      e.preventDefault()
      // Chrome requiere returnValue
      e.returnValue = '¿Seguro que quieres salir? Perderás tu carrito.'
    }

    window.addEventListener('beforeunload', handler)
    return () => window.removeEventListener('beforeunload', handler)
  }, [count])
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/hooks/
git commit -m "feat: useCartWarning hook with beforeunload"
git push
```

---

## Task 11: Frontend — Componentes visuales (diseño premium)

> **IMPORTANTE:** Antes de implementar esta tarea, invocar el skill `/frontend-design` con el siguiente contexto:
> - Referencia visual: `referencias/catalogo-cosmetica.html` (paleta crema/dorado, Cormorant Garamond + Jost)
> - Estilo: premium, moda/skincare de lujo (referencia: Aesop, La Mer)
> - Animaciones: scroll-driven al estilo Apple, fade-in con Intersection Observer
> - Componentes a diseñar: ProductCard, Cart (panel lateral), CartButton (flotante), CheckoutButton

**Files:**
- Create: `frontend/src/index.css`
- Create: `frontend/src/components/ProductCard.jsx`
- Create: `frontend/src/components/Cart.jsx`
- Create: `frontend/src/components/CartButton.jsx`
- Create: `frontend/src/components/CheckoutButton.jsx`

- [ ] **Step 1: Crear index.css con variables y reset**

```css
/* frontend/src/index.css */
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Jost:wght@300;400;500&display=swap');

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --cream: #FAF7F2;
  --warm-white: #FFFDF9;
  --sand: #E8E0D0;
  --gold: #B8954A;
  --gold-light: #D4AF70;
  --dark: #1C1A16;
  --mid: #5C5548;
  --muted: #9A9088;
  --accent: #7A5C3C;
  --rose: #C4897A;
  --sage: #7D8C72;
  --font-display: 'Cormorant Garamond', Georgia, serif;
  --font-body: 'Jost', system-ui, sans-serif;
  --transition: 0.25s ease;
}

html { scroll-behavior: smooth; }

body {
  font-family: var(--font-body);
  background: var(--cream);
  color: var(--dark);
  font-weight: 300;
  letter-spacing: 0.02em;
}

/* Fade-in scroll animation */
.fade-in {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.7s ease, transform 0.7s ease;
}

.fade-in.visible {
  opacity: 1;
  transform: translateY(0);
}
```

- [ ] **Step 2: Crear ProductCard.jsx**

```jsx
// frontend/src/components/ProductCard.jsx
import { useRef, useEffect } from 'react'
import useCartStore from '../store/cartStore'
import styles from './ProductCard.module.css'

const BADGE_LABELS = {
  bestseller: 'Bestseller',
  nuevo: 'Nuevo',
  oferta: 'Oferta',
  popular: 'Popular',
  recomendado: 'Recomendado',
}

export default function ProductCard({ product }) {
  const addItem = useCartStore((s) => s.addItem)
  const cardRef = useRef(null)

  // Scroll fade-in animation
  useEffect(() => {
    const el = cardRef.current
    if (!el) return
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          el.classList.add('visible')
          observer.unobserve(el)
        }
      },
      { threshold: 0.15 }
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  return (
    <article ref={cardRef} className={`fade-in ${styles.card}`}>
      <div className={styles.imageWrap}>
        {product.badge && (
          <span className={`${styles.badge} ${styles[product.badge]}`}>
            {BADGE_LABELS[product.badge]}
          </span>
        )}
        {product.image_url ? (
          <img src={product.image_url} alt={product.name} className={styles.image} />
        ) : (
          <div className={styles.imagePlaceholder}>
            <span>Sin imagen</span>
          </div>
        )}
        <div className={styles.overlay}>
          <button className={styles.addBtn} onClick={() => addItem(product)}>
            Agregar al carrito
          </button>
        </div>
      </div>
      <div className={styles.info}>
        <p className={styles.brand}>{product.brand}</p>
        <h3 className={styles.name}>{product.name}</h3>
        <p className={styles.desc}>{product.description}</p>
        <div className={styles.footer}>
          <span className={styles.price}>${product.price.toFixed(2)}</span>
          <span className={styles.size}>{product.size}</span>
        </div>
      </div>
    </article>
  )
}
```

- [ ] **Step 3: Crear ProductCard.module.css**

```css
/* frontend/src/components/ProductCard.module.css */
.card {
  background: var(--warm-white);
  border: 1px solid var(--sand);
  transition: border-color var(--transition), transform var(--transition);
  cursor: pointer;
}

.card:hover {
  border-color: var(--gold);
  transform: translateY(-4px);
}

.imageWrap {
  position: relative;
  aspect-ratio: 4/5;
  background: var(--cream);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.badge {
  position: absolute;
  top: 14px;
  left: 14px;
  font-size: 8px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  padding: 5px 10px;
  z-index: 1;
  background: var(--dark);
  color: var(--gold-light);
}

.badge.nuevo { background: var(--sage); color: white; }
.badge.oferta { background: var(--rose); color: white; }

.image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.card:hover .image { transform: scale(1.03); }

.imagePlaceholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--muted);
}

.overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background: rgba(28, 26, 22, 0.85);
  opacity: 0;
  transition: opacity var(--transition);
  display: flex;
  justify-content: center;
}

.card:hover .overlay { opacity: 1; }

.addBtn {
  font-family: var(--font-body);
  font-size: 9px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--cream);
  border: 1px solid rgba(232, 224, 208, 0.5);
  background: transparent;
  padding: 10px 24px;
  cursor: pointer;
  transition: background var(--transition), border-color var(--transition);
}

.addBtn:hover {
  background: var(--gold);
  border-color: var(--gold);
  color: var(--dark);
}

.info {
  padding: 20px 22px 24px;
  border-top: 1px solid var(--sand);
}

.brand {
  font-size: 9px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 6px;
}

.name {
  font-family: var(--font-display);
  font-size: 19px;
  font-weight: 400;
  color: var(--dark);
  line-height: 1.3;
  margin-bottom: 8px;
}

.desc {
  font-size: 12px;
  font-weight: 300;
  color: var(--muted);
  line-height: 1.8;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.price {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 400;
  color: var(--dark);
}

.size {
  font-size: 11px;
  color: var(--muted);
  letter-spacing: 0.08em;
}
```

- [ ] **Step 4: Crear CartButton.jsx**

```jsx
// frontend/src/components/CartButton.jsx
import useCartStore from '../store/cartStore'
import styles from './CartButton.module.css'

export default function CartButton({ onClick }) {
  const count = useCartStore((s) => s.getCount())

  return (
    <button
      className={styles.btn}
      onClick={onClick}
      aria-label={`Carrito — ${count} producto${count !== 1 ? 's' : ''}`}
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/>
        <line x1="3" y1="6" x2="21" y2="6"/>
        <path d="M16 10a4 4 0 01-8 0"/>
      </svg>
      {count > 0 && <span className={styles.badge}>{count}</span>}
    </button>
  )
}
```

```css
/* frontend/src/components/CartButton.module.css */
.btn {
  position: fixed;
  bottom: 32px;
  right: 32px;
  width: 56px;
  height: 56px;
  background: var(--dark);
  color: var(--cream);
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 200;
  transition: background var(--transition), transform var(--transition);
  box-shadow: 0 4px 24px rgba(28,26,22,0.25);
}

.btn:hover { background: var(--accent); transform: scale(1.05); }

.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 20px;
  height: 20px;
  background: var(--gold);
  color: var(--dark);
  border-radius: 50%;
  font-size: 11px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

- [ ] **Step 5: Crear CheckoutButton.jsx**

```jsx
// frontend/src/components/CheckoutButton.jsx
import { useState } from 'react'
import useCartStore from '../store/cartStore'
import { createOrder } from '../api/orders'
import styles from './CheckoutButton.module.css'

export default function CheckoutButton({ onClose }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const items = useCartStore((s) => s.items)
  const getTotal = useCartStore((s) => s.getTotal)
  const clearCart = useCartStore((s) => s.clearCart)

  const handleCheckout = async () => {
    if (items.length === 0) return
    setLoading(true)
    setError(null)
    try {
      const { whatsapp_url } = await createOrder(items, getTotal())
      clearCart()
      onClose()
      window.open(whatsapp_url, '_blank', 'noopener')
    } catch {
      setError('Hubo un error al procesar el pedido. Inténtalo de nuevo.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      {error && <p className={styles.error}>{error}</p>}
      <button
        className={styles.btn}
        onClick={handleCheckout}
        disabled={loading || items.length === 0}
      >
        {loading ? 'Procesando...' : '📲 Pedir por WhatsApp'}
      </button>
    </div>
  )
}
```

```css
/* frontend/src/components/CheckoutButton.module.css */
.btn {
  width: 100%;
  padding: 16px;
  background: #25D366;
  color: white;
  border: none;
  font-family: var(--font-body);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  cursor: pointer;
  transition: background var(--transition);
}

.btn:hover:not(:disabled) { background: #1ebe5a; }

.btn:disabled {
  background: var(--sand);
  color: var(--muted);
  cursor: not-allowed;
}

.error {
  font-size: 12px;
  color: var(--rose);
  margin-bottom: 12px;
  text-align: center;
}
```

- [ ] **Step 6: Crear Cart.jsx**

```jsx
// frontend/src/components/Cart.jsx
import useCartStore from '../store/cartStore'
import CheckoutButton from './CheckoutButton'
import styles from './Cart.module.css'

export default function Cart({ isOpen, onClose }) {
  const items = useCartStore((s) => s.items)
  const getTotal = useCartStore((s) => s.getTotal)
  const removeItem = useCartStore((s) => s.removeItem)
  const updateQty = useCartStore((s) => s.updateQty)

  return (
    <>
      {isOpen && <div className={styles.backdrop} onClick={onClose} />}
      <aside className={`${styles.panel} ${isOpen ? styles.open : ''}`}>
        <div className={styles.header}>
          <h2 className={styles.title}>Tu carrito</h2>
          <button className={styles.close} onClick={onClose} aria-label="Cerrar carrito">✕</button>
        </div>

        {items.length === 0 ? (
          <div className={styles.empty}>
            <p>El carrito está vacío.</p>
            <p className={styles.emptyHint}>Agrega productos desde el catálogo.</p>
          </div>
        ) : (
          <>
            <div className={styles.warning}>
              ⚠️ No cierres esta pestaña — perderás tu carrito
            </div>
            <ul className={styles.items}>
              {items.map((item) => (
                <li key={item.id} className={styles.item}>
                  <div className={styles.itemInfo}>
                    <p className={styles.itemName}>{item.name}</p>
                    <p className={styles.itemSize}>{item.size}</p>
                    <p className={styles.itemPrice}>${(item.price * item.qty).toFixed(2)}</p>
                  </div>
                  <div className={styles.itemControls}>
                    <button onClick={() => updateQty(item.id, item.qty - 1)}>−</button>
                    <span>{item.qty}</span>
                    <button onClick={() => updateQty(item.id, item.qty + 1)}>+</button>
                    <button className={styles.remove} onClick={() => removeItem(item.id)}>✕</button>
                  </div>
                </li>
              ))}
            </ul>
            <div className={styles.footer}>
              <div className={styles.total}>
                <span>Total estimado</span>
                <span className={styles.totalAmount}>${getTotal().toFixed(2)}</span>
              </div>
              <CheckoutButton onClose={onClose} />
            </div>
          </>
        )}
      </aside>
    </>
  )
}
```

```css
/* frontend/src/components/Cart.module.css */
.backdrop {
  position: fixed;
  inset: 0;
  background: rgba(28, 26, 22, 0.4);
  z-index: 290;
}

.panel {
  position: fixed;
  top: 0;
  right: 0;
  height: 100dvh;
  width: 400px;
  max-width: 100vw;
  background: var(--warm-white);
  z-index: 300;
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: -4px 0 32px rgba(28, 26, 22, 0.12);
}

.panel.open { transform: translateX(0); }

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 24px 20px;
  border-bottom: 1px solid var(--sand);
}

.title {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 400;
  color: var(--dark);
}

.close {
  background: none;
  border: none;
  font-size: 16px;
  color: var(--mid);
  cursor: pointer;
  padding: 4px 8px;
}

.warning {
  background: #FFF8E7;
  border-bottom: 1px solid #F0D88A;
  padding: 10px 24px;
  font-size: 11px;
  color: #7A6000;
  letter-spacing: 0.04em;
}

.empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--muted);
  font-size: 14px;
}

.emptyHint { font-size: 12px; }

.items {
  flex: 1;
  overflow-y: auto;
  list-style: none;
  padding: 0 24px;
}

.item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 20px 0;
  border-bottom: 1px solid var(--sand);
  gap: 12px;
}

.itemInfo { flex: 1; }

.itemName {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 400;
  margin-bottom: 4px;
}

.itemSize {
  font-size: 11px;
  color: var(--muted);
  margin-bottom: 6px;
}

.itemPrice {
  font-size: 14px;
  color: var(--accent);
  font-weight: 400;
}

.itemControls {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.itemControls button {
  background: none;
  border: 1px solid var(--sand);
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px;
  color: var(--dark);
  transition: background var(--transition);
}

.itemControls button:hover { background: var(--sand); }

.remove { color: var(--rose) !important; }

.itemControls span {
  font-size: 14px;
  font-weight: 400;
  min-width: 20px;
  text-align: center;
}

.footer {
  padding: 20px 24px 24px;
  border-top: 1px solid var(--sand);
}

.total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 13px;
  color: var(--mid);
  letter-spacing: 0.06em;
}

.totalAmount {
  font-family: var(--font-display);
  font-size: 22px;
  color: var(--dark);
}
```

- [ ] **Step 7: Commit**

```bash
git add frontend/src/
git commit -m "feat: ProductCard, Cart panel, CartButton, CheckoutButton components"
git push
```

---

## Task 12: Frontend — Página Catalog + App shell

**Files:**
- Create: `frontend/src/pages/Catalog.jsx`
- Modify: `frontend/src/App.jsx`

- [ ] **Step 1: Crear pages/Catalog.jsx**

```jsx
// frontend/src/pages/Catalog.jsx
import { useState, useEffect } from 'react'
import { fetchProducts } from '../api/products'
import ProductCard from '../components/ProductCard'
import styles from './Catalog.module.css'

const CATEGORIES = [
  { key: 'all', label: 'Todo' },
  { key: 'skincare', label: 'Skincare' },
  { key: 'cabello', label: 'Cabello' },
  { key: 'corporal', label: 'Corporal' },
  { key: 'maquillaje', label: 'Maquillaje' },
  { key: 'salud', label: 'Salud & Bienestar' },
]

export default function Catalog() {
  const [products, setProducts] = useState([])
  const [activeCategory, setActiveCategory] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchProducts()
      .then(setProducts)
      .catch(() => setError('No se pudieron cargar los productos.'))
      .finally(() => setLoading(false))
  }, [])

  const filtered =
    activeCategory === 'all'
      ? products
      : products.filter((p) => p.category === activeCategory)

  if (loading) return <div className={styles.loading}>Cargando catálogo...</div>
  if (error) return <div className={styles.error}>{error}</div>

  return (
    <section className={styles.section} id="catalogo">
      <div className={styles.container}>
        <div className={styles.header}>
          <p className={styles.eyebrow}>Catálogo completo</p>
          <h2 className={styles.title}>
            Explora por <em>categoría</em>
          </h2>
          <p className={styles.desc}>
            Selecciona la categoría que más te interese y descubre nuestra
            selección curada de la línea Nutriplus by Farmasi.
          </p>
        </div>

        <div className={styles.tabs}>
          {CATEGORIES.map((cat) => (
            <button
              key={cat.key}
              className={`${styles.tab} ${activeCategory === cat.key ? styles.active : ''}`}
              onClick={() => setActiveCategory(cat.key)}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {filtered.length === 0 ? (
          <p className={styles.empty}>No hay productos en esta categoría.</p>
        ) : (
          <div className={styles.grid}>
            {filtered.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
```

```css
/* frontend/src/pages/Catalog.module.css */
.section {
  padding: 80px 0;
  background: var(--warm-white);
}

.container {
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 40px;
}

.header {
  text-align: center;
  margin-bottom: 56px;
}

.eyebrow {
  font-size: 10px;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 16px;
}

.title {
  font-family: var(--font-display);
  font-size: clamp(28px, 4vw, 48px);
  font-weight: 300;
  color: var(--dark);
  margin-bottom: 16px;
}

.title em { font-style: italic; color: var(--accent); }

.desc {
  font-size: 14px;
  font-weight: 300;
  color: var(--mid);
  max-width: 520px;
  margin: 0 auto;
  line-height: 1.9;
}

.tabs {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 56px;
}

.tab {
  padding: 10px 24px;
  font-family: var(--font-body);
  font-size: 10px;
  font-weight: 400;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  border: 1px solid var(--sand);
  background: transparent;
  color: var(--mid);
  cursor: pointer;
  transition: all var(--transition);
}

.tab:hover,
.tab.active {
  background: var(--dark);
  border-color: var(--dark);
  color: var(--cream);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 40px 32px;
}

.loading,
.error,
.empty {
  text-align: center;
  padding: 80px 40px;
  color: var(--muted);
  font-size: 14px;
  letter-spacing: 0.08em;
}

.error { color: var(--rose); }

@media (max-width: 768px) {
  .container { padding: 0 20px; }
  .section { padding: 56px 0; }
  .grid { grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 24px; }
}
```

- [ ] **Step 2: Actualizar App.jsx con el shell completo**

```jsx
// frontend/src/App.jsx
import { useState } from 'react'
import Catalog from './pages/Catalog'
import Cart from './components/Cart'
import CartButton from './components/CartButton'
import { useCartWarning } from './hooks/useCartWarning'

export default function App() {
  const [cartOpen, setCartOpen] = useState(false)
  useCartWarning()

  return (
    <>
      {/* ── ANNOUNCEMENT BAR ── */}
      <div style={{
        background: 'var(--dark)', color: 'var(--sand)',
        textAlign: 'center', fontSize: '11px',
        letterSpacing: '0.15em', textTransform: 'uppercase', padding: '10px 20px'
      }}>
        Afiliada oficial Nutriplus by Farmasi · Cosmética de farmacia turca · Envíos disponibles
      </div>

      {/* ── HEADER ── */}
      <header style={{
        background: 'var(--warm-white)', borderBottom: '1px solid var(--sand)',
        position: 'sticky', top: 0, zIndex: 100
      }}>
        <div style={{
          maxWidth: '1320px', margin: '0 auto', padding: '0 40px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '80px'
        }}>
          <div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '26px', fontWeight: 400, letterSpacing: '0.12em' }}>
              Lumière
            </div>
            <div style={{ fontSize: '9px', letterSpacing: '0.25em', textTransform: 'uppercase', color: 'var(--muted)' }}>
              Cosmética & Salud
            </div>
            <div style={{ fontSize: '8.5px', letterSpacing: '0.15em', textTransform: 'uppercase', color: 'var(--gold)', border: '1px solid var(--gold-light)', padding: '2px 8px', display: 'inline-block', marginTop: '4px' }}>
              Nutriplus · Farmasi Affiliate
            </div>
          </div>
          <nav style={{ display: 'flex', gap: '36px', alignItems: 'center' }}>
            {['Skincare', 'Cabello', 'Corporal', 'Salud'].map((label) => (
              <a key={label} href="#catalogo" style={{ fontSize: '11px', letterSpacing: '0.14em', textTransform: 'uppercase', textDecoration: 'none', color: 'var(--mid)' }}>
                {label}
              </a>
            ))}
          </nav>
        </div>
      </header>

      {/* ── MAIN ── */}
      <main>
        <Catalog />
      </main>

      {/* ── CARRITO ── */}
      <CartButton onClick={() => setCartOpen(true)} />
      <Cart isOpen={cartOpen} onClose={() => setCartOpen(false)} />
    </>
  )
}
```

- [ ] **Step 3: Verificar en el navegador**

```bash
cd frontend && npm run dev
```

Abrir `http://localhost:5173`:
- [ ] Catálogo carga productos del backend
- [ ] Tabs filtran por categoría correctamente
- [ ] Click en "Agregar al carrito" suma al contador del botón flotante
- [ ] Panel de carrito se abre/cierra con animación
- [ ] Warning amarillo visible cuando hay items
- [ ] Contador en CartButton se actualiza en tiempo real
- [ ] "+" y "−" modifican cantidades correctamente
- [ ] "✕" en item lo elimina del carrito

- [ ] **Step 4: Commit**

```bash
git add frontend/src/
git commit -m "feat: Catalog page, App shell and complete cart flow"
git push
```

---

## Task 13: Integración Docker completa + smoke test

**Files:**
- Verify: `docker-compose.yml`

- [ ] **Step 1: Arrancar todos los servicios**

```bash
cd /Users/alfonso/Documents/mama/lumiere-beauty
docker compose up --build -d
docker compose ps
```

Expected — todos en estado `running`:
```
NAME                STATUS
lumiere-mongodb     running
lumiere-valkey      running
lumiere-backend     running
lumiere-frontend    running
```

- [ ] **Step 2: Ejecutar seed en el contenedor**

```bash
docker compose exec backend python -m app.seed
```

Expected: `✅ 7 productos cargados.`

- [ ] **Step 3: Smoke test completo**

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# Productos
curl http://localhost:8000/products | python -m json.tool | grep '"name"'
# Expected: 7 líneas con los nombres de productos

# Crear pedido de prueba
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"items":[{"product_id":"test","name":"Aloe Glow","price":18.99,"qty":1,"size":"450ml"}],"total":18.99}'
# Expected: {"order_id":"...","whatsapp_url":"https://wa.me/...","total":18.99}
```

- [ ] **Step 4: Verificar frontend en Docker**

Abrir `http://localhost:5173` y repetir los checks del Task 12 Step 3.

- [ ] **Step 5: Commit final**

```bash
git add .
git commit -m "feat: complete Lumière Beauty catalog — backend + frontend + Docker"
git push
```

Expected: todos los archivos en github.com/alfonsotejeda/lumiere-beauty

---

## Resumen de comandos para el día a día

```bash
# Arrancar todo
docker compose up -d

# Ver logs del backend
docker compose logs backend -f

# Ejecutar tests
cd backend && source .venv/bin/activate && pytest tests/ -v

# Agregar un producto (reemplazar token y datos)
curl -X POST http://localhost:8000/products \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Nuevo Producto","brand":"Nutriplus","category":"salud","description":"...","price":24.99,"size":"200g","in_stock":true,"image_url":"http://localhost:8000/static/images/nuevo.jpg"}'

# Ver pedidos recibidos
curl http://localhost:8000/orders \
  -H "Authorization: Bearer <ADMIN_TOKEN>"

# Parar todo
docker compose down
```
