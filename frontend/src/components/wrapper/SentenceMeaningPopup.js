import React from 'react';

import './SentenceMeaningPopup.css';

export default function SentenceMeaningPopup({ open, onClose, children, style = {}, ...props }) {
  if (!open) return null;
  return (
    <div
      className="sentence-meaning-popup"
      style={style}
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
