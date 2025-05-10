import React, { useState, useRef } from 'react';
import WordMeaningPopup from './WordMeaningPopup';

const ExplainableWrapper = ({ children }) => {
  const [popup, setPopup] = useState({ visible: false, message: '' });
  const [confirmText, setConfirmText] = useState(null);
  const [showConfirm, setShowConfirm] = useState(false);
  const anchorRef = useRef(null);

  const handleTextSelection = (event) => {
    if (event) {
      // Only proceed if not a right-click
      if (event.button === 2) return;
      event.stopPropagation();
      event.preventDefault();
    }
    const selection = window.getSelection();
    const text = selection.toString().trim();
    // Only show confirm if actual selection (not just caret or scroll)
    if (text.length > 0 && selection.type === 'Range') {
      setConfirmText(text);
      setShowConfirm(true);
    }
  };


  const closePopup = () => {
    setPopup({ visible: false, message: '' });
    setConfirmText(null);
    setShowConfirm(false);
    if (anchorRef.current) {
      anchorRef.current.style.display = 'none';
    }
  };


  // Confirm modal logic
  const handleConfirm = async () => {
    if (!confirmText) return;
    const textToExplain = confirmText; // capture value
    setShowConfirm(false); // Close confirm popup
    try {
      const response = await fetch('/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToExplain }),
      });
      if (response.ok) {
        const data = await response.json();
        let message = data.explanation || '';
        setPopup({
          visible: true,
          message: message || 'No explanation available.'
        });
      } else {
        setPopup({ visible: true, message: 'Failed to fetch explanation.' });
      }
    } catch (error) {
      setPopup({ visible: true, message: 'Error: ' + error });
    }
  };
  const handleCancel = () => setShowConfirm(false);

  return (
    <div style={{ position: 'relative' }} onMouseUp={handleTextSelection}>
      {children}
      <span ref={anchorRef} style={{ display: 'none', position: 'absolute' }} />
      <div id="bubble" className="hidden"></div>
      {showConfirm && (
        <WordMeaningPopup open={showConfirm} onClose={() => setShowConfirm(false)}>
          <div style={{fontWeight:600, fontSize:'1.1rem', marginBottom:12}}>Explain the selected text?</div>
          <div style={{marginBottom:18, padding:'10px 14px', background:'#f6fafd', borderRadius:8, color:'#1976d2', fontSize:'1.07rem'}}>{confirmText}</div>
          <div style={{display:'flex', gap:16, justifyContent:'center'}}>
            <button onClick={handleConfirm} style={{padding:'7px 22px', background:'#1976d2', color:'#fff', border:'none', borderRadius:8, fontWeight:600, fontSize:'1rem', cursor:'pointer'}}>Confirm</button>
            <button onClick={handleCancel} style={{padding:'7px 22px', background:'#eee', color:'#1976d2', border:'none', borderRadius:8, fontWeight:600, fontSize:'1rem', cursor:'pointer'}}>Cancel</button>
          </div>
        </WordMeaningPopup>
      )}
      {popup.visible && (
        <WordMeaningPopup open={popup.visible} onClose={closePopup}>
          <button onClick={closePopup} style={{position:'absolute',top:18,right:18,background:'none',border:'none',fontSize:22,color:'#888',cursor:'pointer'}}>&times;</button>
          {popup.message}
        </WordMeaningPopup>
      )}
    </div>
  );
};

export default ExplainableWrapper;
