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
