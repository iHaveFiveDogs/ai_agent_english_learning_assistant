import React, { useState } from 'react';
import './TopBar.css';
import { Link } from 'react-router-dom';

// Hamburger Icon SVG (short, thin lines)
const HamburgerIcon = ({ onClick }) => (
  <button
    className="hamburger-btn"
    onClick={onClick}
    aria-label="Menu"
  >
    <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect y="6" width="20" height="2" rx="1" fill="#222" x="4" />
      <rect y="13" width="20" height="2" rx="1" fill="#222" x="4" />
      <rect y="20" width="20" height="2" rx="1" fill="#222" x="4" />
    </svg>
  </button>
);

const TopBar = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  const handleMenuToggle = () => {
    setMenuOpen((open) => !open);
  };
  const handleMenuClose = () => {
    setMenuOpen(false);
  };

  return (
    <header className="top-bar">
      <div className="top-bar-left" style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
        <HamburgerIcon onClick={handleMenuToggle} />
        {menuOpen && (
          <div className="dropdown-menu" style={{
            position: 'absolute',
            top: '40px',
            left: 0,
            background: '#fff',
            boxShadow: '0 2px 12px rgba(0,0,0,0.15)',
            borderRadius: '8px',
            minWidth: '160px',
            zIndex: 2000,
            padding: '8px 0',
          }}
            onMouseLeave={handleMenuClose}
          >
            <Link to="/upload" className="dropdown-item" style={{
              display: 'block',
              padding: '10px 24px',
              color: '#222',
              textDecoration: 'none',
              fontWeight: 500,
              cursor: 'pointer',
            }}
              onClick={handleMenuClose}
            >
              Upload Article
            </Link>
          </div>
        )}
        <nav style={{ display: 'flex', gap: '18px', alignItems: 'center', marginLeft: 12 }}>
          <Link to="/articles?tag=news" className="nav-link">Articles</Link>
          <Link to="/articles?tag=novels" className="nav-link">Novels</Link>
        </nav>
      </div>
      <div className="top-bar-center" style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <input className="search-input" type="text" placeholder="Search..." style={{ maxWidth: 260 }} />
      </div>
      <div className="top-bar-right" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button className="auth-btn">Sign In</button>
        <button className="auth-btn">Sign Up</button>
      </div>
    </header>
  );
};

export default TopBar;
