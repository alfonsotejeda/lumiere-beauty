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
