# Lumière Beauty — Diseño del Sistema
**Fecha:** 2026-04-25  
**Stack:** React + Vite · FastAPI · MongoDB + Motor · Valkey  
**Repositorio:** github.com/alfonsotejeda/lumiere-beauty (público)

---

## 1. Visión general

Catálogo web premium para **Lumière Beauty**, afiliada de **Nutriplus by Farmasi** (cosmética turca de farmacia). Los clientes navegan el catálogo, arman un carrito y envían su pedido por WhatsApp. El administrador gestiona productos mediante API REST protegida con token.

### Productos actuales (seed inicial)
Tres líneas de la gama Nutriplus:
- **Calming Glow System** (Belleza + Serenidad): Aloe Glow, Serenity Lemon Tea, Beauty Booster Collagen, Restore
- **Morning Glow System** (Belleza + Energía): productos del catálogo matutino
- **Pre-workout Nutriplus**: suplemento de rendimiento

Categorías: Skincare · Cabello · Corporal · Maquillaje · Salud & Bienestar

---

## 2. Arquitectura

```
lumiere-beauty/
├── docker-compose.yml
├── .env                        # No va al repo
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── products.py
│   │   │   └── orders.py
│   │   ├── models/
│   │   │   ├── product.py
│   │   │   └── order.py
│   │   ├── db.py               # Motor (MongoDB async)
│   │   ├── cache.py            # Valkey (redis-py async)
│   │   └── seed.py             # Carga inicial de productos
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProductCard.jsx
│   │   │   ├── Cart.jsx
│   │   │   ├── CartButton.jsx
│   │   │   └── CheckoutButton.jsx
│   │   ├── pages/
│   │   │   └── Catalog.jsx
│   │   ├── store/
│   │   │   └── cartStore.js    # Zustand
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── referencias/
│   └── catalogo-cosmetica.html
└── products/                   # PDFs de catálogo Nutriplus
```

---

## 3. Infraestructura Docker

```yaml
services:
  mongodb:
    image: mongo:7
    ports: ["27017:27017"]
    volumes: [mongo_data:/data/db]

  valkey:
    image: valkey/valkey:7
    ports: ["6379:6379"]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [mongodb, valkey]

  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    depends_on: [backend]
```

### Variables de entorno (`.env`)
```
MONGO_URL=mongodb://mongodb:27017
MONGO_DB=lumiere
VALKEY_URL=redis://valkey:6379
ADMIN_TOKEN=<token-secreto>
WHATSAPP_NUMBER=+1XXXXXXXXXX
CACHE_TTL_SECONDS=600
```

---

## 4. Modelos de datos

### Colección `products`
```json
{
  "_id": "ObjectId",
  "name": "Beauty Booster Collagen",
  "brand": "Nutriplus",
  "category": "salud",
  "description": "10,000mg colágeno hidrolizado con ácido hialurónico y vitamina C",
  "price": 29.99,
  "size": "250g",
  "badge": "bestseller | nuevo | oferta | null",
  "in_stock": true,
  "image_url": "/images/beauty-booster.jpg",
  "created_at": "ISODate"
}
```

### Colección `orders`
```json
{
  "_id": "ObjectId",
  "items": [
    {"product_id": "ObjectId", "name": "string", "price": 29.99, "qty": 2}
  ],
  "total": 59.98,
  "status": "whatsapp_sent",
  "whatsapp_url": "https://wa.me/...",
  "created_at": "ISODate"
}
```

---

## 5. API REST

### Endpoints públicos (sin auth)
| Método | Ruta | Descripción | Cache |
|--------|------|-------------|-------|
| `GET` | `/products` | Lista todos los productos | Valkey 10 min |
| `GET` | `/products/{id}` | Detalle de un producto | Valkey 10 min |
| `POST` | `/orders` | Crear pedido, retorna URL de WhatsApp | No |

### Endpoints admin (`Authorization: Bearer <token>`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/products` | Crear producto |
| `PUT` | `/products/{id}` | Editar producto (invalida cache) |
| `DELETE` | `/products/{id}` | Eliminar producto (invalida cache) |
| `GET` | `/orders` | Historial de pedidos |

### Respuesta de `POST /orders`
```json
{
  "order_id": "abc123",
  "whatsapp_url": "https://wa.me/+1XXXXXXXXXX?text=...",
  "total": 78.97
}
```

---

## 6. Carrito y flujo de pedido

### Estado (Zustand — en memoria, sin persistencia)
```js
{
  items: [{ product_id, name, price, qty, size }],
  addItem(product),
  removeItem(product_id),
  updateQty(product_id, qty),
  clearCart()
}
```

### Advertencia de pestaña (beforeunload)
- Se activa cuando `items.length > 0`
- Muestra: *"¿Seguro que quieres salir? Perderás tu carrito"*
- Se desactiva automáticamente después de `clearCart()` (post-pedido)
- Banner visible en la UI: *"Tu carrito no se guarda si cierras esta pestaña"*

### Flujo completo
1. Cliente navega catálogo → agrega productos al carrito
2. Panel lateral (Cart) muestra items, cantidades, total en tiempo real
3. Cliente pulsa "Pedir por WhatsApp"
4. Frontend llama `POST /orders` con items y total
5. Backend guarda pedido en MongoDB con `status: "whatsapp_sent"`
6. Backend construye mensaje y retorna `whatsapp_url`
7. Frontend abre `wa.me/...` en nueva pestaña
8. `clearCart()` — carrito se vacía, `beforeunload` se desactiva

### Mensaje de WhatsApp generado
```
Hola Lumière Beauty! 🌿

Quisiera hacer el siguiente pedido:

• 2x Beauty Booster Collagen (250g) — $59.98
• 1x Aloe Glow (450ml) — $18.99

💰 Total estimado: $78.97

Gracias!
```

---

## 7. Frontend — Diseño visual

### Referencias y estética
- **Base visual:** `referencias/catalogo-cosmetica.html` — paleta crema/dorado, tipografías Cormorant Garamond + Jost
- **Estilo objetivo:** Premium, moda/skincare de lujo, comparable a Aesop, La Mer, Charlotte Tilbury
- **Animaciones:** Scroll-driven al estilo Apple — fade-in, parallax suave, elementos que aparecen progresivamente al hacer scroll
- **Transiciones:** Fluidas, 60fps, sin ser llamativas. CSS `@keyframes` + Intersection Observer API

### Variables de diseño (heredadas del catálogo)
```css
--cream: #FAF7F2
--gold: #B8954A
--gold-light: #D4AF70
--dark: #1C1A16
--font-display: 'Cormorant Garamond'
--font-body: 'Jost'
```

### Skill a invocar en implementación
Al construir el frontend se invocará `/frontend-design` con el contexto completo de esta spec para generar un diseño premium detallado.

---

## 8. Gestión de productos (Admin — Fase 1)

API REST protegida con Bearer token. El administrador usa Postman o curl.

```bash
# Crear producto
curl -X POST http://localhost:8000/products \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Aloe Glow", "price": 18.99, "category": "salud", ...}'
```

**Fase 2 (futuro):** Panel `/admin` en React con formularios CRUD — no impacta la arquitectura actual.

---

## 9. Estrategia de caché (Valkey)

| Clave | TTL | Invalida cuando |
|-------|-----|-----------------|
| `products:all` | 10 min | POST/PUT/DELETE en `/products` |
| `products:{id}` | 10 min | PUT/DELETE en `/products/{id}` |

---

## 10. Imágenes de productos

El campo `image_url` siempre almacena una URL completa para que el código funcione igual en local y producción.

### Local (desarrollo)
- Carpeta: `backend/static/images/`
- FastAPI sirve los archivos en `GET /static/images/<filename>`
- `image_url` ejemplo: `http://localhost:8000/static/images/beauty-booster.jpg`
- Para agregar imagen: copiar archivo a esa carpeta + `PUT /products/{id}` con nueva URL

### Producción (futura)
- Imágenes en **Cloudinary** (tier gratuito: 25GB almacenamiento + CDN global)
- `image_url` ejemplo: `https://res.cloudinary.com/lumiere/image/upload/beauty-booster.jpg`
- Variable de entorno `IMAGES_BASE_URL` controla la base; el código no cambia

### Arquitectura de producción recomendada
```
Frontend  →  Vercel (gratis, CDN automático)
Backend   →  Railway o Render (~$5/mes, Docker soportado)
MongoDB   →  MongoDB Atlas (tier M0 gratuito para empezar)
Valkey    →  Upstash (tier gratuito, compatible Redis)
Imágenes  →  Cloudinary (tier gratuito)
Dominio   →  Namecheap / Google Domains (~$12/año)
```

**Al pasar a producción:** solo se cambian variables de entorno. El código Docker Compose se adapta o se despliega servicio por servicio. Cero cambios en el código de la aplicación.

---

## 11. Fuera de alcance (V1)

- Autenticación de usuarios / cuentas de cliente
- Pagos en línea
- Panel admin visual
- Notificaciones push / email
- Múltiples idiomas
