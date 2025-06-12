import React from 'react';
import './WordMeaningPopup.css';

export default function WordMeaningPopup({ open, onClose, children, ...props }) {
  if (!open) return null;
  return (
    <div
      className="meaning-popup-overlay"
      onDoubleClick={onClose}
    >
      <div
        className="meaning-popup-content"
        {...props}
      >
        {children}
      </div>
    </div>
  );
}
