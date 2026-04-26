// frontend/src/components/CheckoutButton.jsx
import { useState } from 'react'
import useCartStore from '../store/cartStore'
import { createOrder } from '../api/orders'
import styles from './CheckoutButton.module.css'

export default function CheckoutButton({ onClose }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const items = useCartStore((s) => s.items)
  const total = useCartStore((s) => s.getTotal())
  const clearCart = useCartStore((s) => s.clearCart)

  const handleCheckout = async () => {
    if (items.length === 0) return
    setLoading(true)
    setError(null)
    try {
      const { whatsapp_url } = await createOrder(items, total)
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
      {error && <p className={styles.error} role="alert">{error}</p>}
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
