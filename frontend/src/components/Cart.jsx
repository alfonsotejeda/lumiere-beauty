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
