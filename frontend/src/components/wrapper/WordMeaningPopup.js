import React from 'react';

export default function WordMeaningPopup({ open, onClose, children, ...props }) {
  if (!open) return null;
  return (
    <div
      className="meaning-popup-overlay"
      onDoubleClick={onClose}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        background: 'rgba(0,0,0,0.22)',
        zIndex: 2000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        animation: 'fadeIn 0.2s',
      }}
    >
      <div
        className="meaning-popup-content"
        style={{
          background: '#fff',
          borderRadius: 16,
          boxShadow: '0 4px 24px rgba(0,0,0,0.13)',
          padding: '32px 32px 24px 32px',
          minWidth: 360,
          maxWidth: 540,
          width: '90vw',
          maxHeight: '80vh',
          overflowY: 'auto',
          position: 'relative',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'stretch',
        }}
        {...props}
      >
        {children}
      </div>
    </div>
  );
}
