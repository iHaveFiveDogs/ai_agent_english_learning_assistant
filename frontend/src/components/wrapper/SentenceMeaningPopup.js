import React from 'react';

export default function SentenceMeaningPopup({ open, onClose, children, style = {}, ...props }) {
  if (!open) return null;
  return (
    <div
      className="sentence-meaning-popup"
      style={{
        position: 'fixed',
        top: 'calc(50% + 240px)', // slightly below the main popup
        left: '50%',
        transform: 'translate(-50%, 0)',
        background: '#fff',
        borderRadius: 16,
        boxShadow: '0 4px 24px rgba(0,0,0,0.13)',
        padding: '24px 32px',
        minWidth: 280,
        maxWidth: 480,
        width: '70vw',
        zIndex: 2010,
        fontSize: '1.08rem',
        color: '#222',
        fontFamily: 'inherit',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        ...style,
      }}
      {...props}
    >
      {onClose && (
        <button
          onClick={onClose}
          style={{ position: 'absolute', top: 16, right: 20, background: 'none', border: 'none', fontSize: 20, color: '#888', cursor: 'pointer' }}
          aria-label="Close"
        >
          &times;
        </button>
      )}
      <div style={{ width: '100%', textAlign: 'left' }}>{children}</div>
    </div>
  );
}
