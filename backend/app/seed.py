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
