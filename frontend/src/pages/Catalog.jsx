// frontend/src/pages/Catalog.jsx
import { useState, useEffect } from 'react'
import { fetchProducts } from '../api/products'
import ProductCard from '../components/ProductCard'
import styles from './Catalog.module.css'

const CATEGORIES = [
  { key: 'all', label: 'Todo' },
  { key: 'skincare', label: 'Skincare' },
  { key: 'cabello', label: 'Cabello' },
  { key: 'corporal', label: 'Corporal' },
  { key: 'maquillaje', label: 'Maquillaje' },
  { key: 'salud', label: 'Salud & Bienestar' },
]

export default function Catalog() {
  const [products, setProducts] = useState([])
  const [activeCategory, setActiveCategory] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchProducts()
      .then(setProducts)
      .catch(() => setError('No se pudieron cargar los productos.'))
      .finally(() => setLoading(false))
  }, [])

  const filtered =
    activeCategory === 'all'
      ? products
      : products.filter((p) => p.category === activeCategory)

  if (loading) return <div className={styles.loading}>Cargando catálogo...</div>
  if (error) return <div className={styles.error}>{error}</div>

  return (
    <section className={styles.section} id="catalogo">
      <div className={styles.container}>
        <div className={styles.header}>
          <p className={styles.eyebrow}>Catálogo completo</p>
          <h2 className={styles.title}>
            Explora por <em>categoría</em>
          </h2>
          <p className={styles.desc}>
            Selecciona la categoría que más te interese y descubre nuestra
            selección curada de la línea Nutriplus by Farmasi.
          </p>
        </div>

        <div className={styles.tabs}>
          {CATEGORIES.map((cat) => (
            <button
              key={cat.key}
              className={`${styles.tab} ${activeCategory === cat.key ? styles.active : ''}`}
              onClick={() => setActiveCategory(cat.key)}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {filtered.length === 0 ? (
          <p className={styles.empty}>No hay productos en esta categoría.</p>
        ) : (
          <div className={styles.grid}>
            {filtered.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
