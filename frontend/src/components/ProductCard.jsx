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
          // 'visible' matches the global .fade-in.visible rule in index.css
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
