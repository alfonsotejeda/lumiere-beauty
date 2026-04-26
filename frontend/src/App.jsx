// frontend/src/App.jsx
import { useState } from 'react'
import Catalog from './pages/Catalog'
import Cart from './components/Cart'
import CartButton from './components/CartButton'
import { useCartWarning } from './hooks/useCartWarning'

export default function App() {
  const [cartOpen, setCartOpen] = useState(false)
  useCartWarning()

  return (
    <>
      {/* ── ANNOUNCEMENT BAR ── */}
      <div style={{
        background: 'var(--dark)', color: 'var(--sand)',
        textAlign: 'center', fontSize: '11px',
        letterSpacing: '0.15em', textTransform: 'uppercase', padding: '10px 20px'
      }}>
        Afiliada oficial Nutriplus by Farmasi · Cosmética de farmacia turca · Envíos disponibles
      </div>

      {/* ── HEADER ── */}
      <header style={{
        background: 'var(--warm-white)', borderBottom: '1px solid var(--sand)',
        position: 'sticky', top: 0, zIndex: 100
      }}>
        <div style={{
          maxWidth: '1320px', margin: '0 auto', padding: '0 40px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '80px'
        }}>
          <div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '26px', fontWeight: 400, letterSpacing: '0.12em' }}>
              Lumière
            </div>
            <div style={{ fontSize: '9px', letterSpacing: '0.25em', textTransform: 'uppercase', color: 'var(--muted)' }}>
              Cosmética & Salud
            </div>
            <div style={{ fontSize: '8.5px', letterSpacing: '0.15em', textTransform: 'uppercase', color: 'var(--gold)', border: '1px solid var(--gold-light)', padding: '2px 8px', display: 'inline-block', marginTop: '4px' }}>
              Nutriplus · Farmasi Affiliate
            </div>
          </div>
          <nav style={{ display: 'flex', gap: '36px', alignItems: 'center' }}>
            {['Skincare', 'Cabello', 'Corporal', 'Salud'].map((label) => (
              <a key={label} href="#catalogo" style={{ fontSize: '11px', letterSpacing: '0.14em', textTransform: 'uppercase', textDecoration: 'none', color: 'var(--mid)' }}>
                {label}
              </a>
            ))}
          </nav>
        </div>
      </header>

      {/* ── MAIN ── */}
      <main>
        <Catalog />
      </main>

      {/* ── CARRITO ── */}
      <CartButton onClick={() => setCartOpen(true)} />
      <Cart isOpen={cartOpen} onClose={() => setCartOpen(false)} />
    </>
  )
}
