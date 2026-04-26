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
