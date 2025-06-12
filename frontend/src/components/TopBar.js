import React from 'react';
import './TopBar.css';
import { Link } from 'react-router-dom';

const TopBar = () => {
  return (
    <header className="top-bar">
      <div className="top-bar-left">
        <nav style={{ display: 'flex', gap: '18px', alignItems: 'center', marginLeft: 12 }}>
          <Link to="/" className="nav-link">Home</Link>
          <Link to="/articles?tag=news" className="nav-link">News</Link>
          <Link to="/articles?tag=nonfiction" className="nav-link">Nonfiction</Link>
          <Link to="/articles?tag=novels" className="nav-link">Novels</Link>
          <Link to="/articles?tag=dramas" className="nav-link">Dramas</Link>
        </nav>
      </div>
      <div className="top-bar-right" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button className="auth-btn">Sign In</button>
        <button className="auth-btn">Sign Up</button>
      </div>
    </header>
  );
};

export default TopBar;
