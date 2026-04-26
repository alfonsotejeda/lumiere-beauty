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
