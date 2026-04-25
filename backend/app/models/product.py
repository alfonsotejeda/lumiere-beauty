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
