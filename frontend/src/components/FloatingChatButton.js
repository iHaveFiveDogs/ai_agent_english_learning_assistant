// import React, { useState } from 'react';
// import './FloatingChatButton.css';

// // Temporarily omitted for UI
// export default function FloatingChatButton() {
//   return null;
// }
//   const [open, setOpen] = useState(false);
//   const [hovered, setHovered] = useState(false);

//   // Show the chat box when hovered or open
//   const showChat = open || hovered;

  // return (
  //   <div
  //     className={`floating-chat-container${showChat ? ' open' : ''}`}
  //     onMouseEnter={() => setHovered(true)}
  //     onMouseLeave={() => { setHovered(false); setOpen(false); }}
  //     style={{ position: 'fixed', bottom: 32, right: 0, zIndex: 1200 }}
  //   >
      {/* The always-visible tab }
      <div
        className="floating-chat-tab"
        onClick={() => setOpen((o) => !o)}
        aria-label="Open chat"
        tabIndex={0}
        role="button"
        style={{ outline: 'none' }}
      >
        <span role="img" aria-label="chat" style={{ marginBottom: 6 }}>💬</span>
      </div>

      // {/* Sliding Chat Popup only (no cloud button) */}
      // <div className={`floating-chat-bubble-wrapper${showChat ? ' open' : ''}`}>
      //   {showChat && (
      //     <div className="floating-chat-popup">
      //       <div className="floating-chat-header">
      //         <span>Chat</span>
      //         <button className="floating-chat-close" onClick={() => setOpen(false)} aria-label="Close chat">×</button>
      //       </div>
      //       <div className="floating-chat-body">
      //         <div style={{ color: '#888', fontSize: 14, margin: '16px 0', textAlign: 'center' }}>
      //           Start a conversation! (Chat integration goes here)
      //         {/* </div>
              {/* Example input for future integration }
              <input
                className="floating-chat-input"
                placeholder="Type a message..."
                disabled
              />
            </div>
          </div>
        )}
      </div>
    </div>
  ); */}
            
  
      
