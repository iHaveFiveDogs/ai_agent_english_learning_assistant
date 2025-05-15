import React, { useState } from 'react';
import './FloatingChatButton.css';

export default function FloatingChatButton() {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Floating Chat Bubble Button */}
      <button
        className="floating-chat-bubble"
        onClick={() => setOpen((o) => !o)}
        aria-label="Open chat"
      >
        <span role="img" aria-label="chat" style={{ marginRight: 6 }}>💬</span>
        Chat
      </button>

      {/* Chat Popup */}
      {open && (
        <div className="floating-chat-popup">
          <div className="floating-chat-header">
            <span>Chat</span>
            <button className="floating-chat-close" onClick={() => setOpen(false)} aria-label="Close chat">×</button>
          </div>
          <div className="floating-chat-body">
            <div style={{ color: '#888', fontSize: 14, margin: '16px 0', textAlign: 'center' }}>
              Start a conversation! (Chat integration goes here)
            </div>
            {/* Example input for future integration */}
            <input
              className="floating-chat-input"
              placeholder="Type a message..."
              disabled
            />
          </div>
        </div>
      )}
    </>
  );
}
