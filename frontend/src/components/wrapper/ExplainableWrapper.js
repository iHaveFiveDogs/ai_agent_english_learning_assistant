import React, { useState, useRef } from 'react';
import WordMeaningPopup from './WordMeaningPopup';
import { explainText } from '../../api/articleService';
// import WordExplanation from '../WordExplanation';

const ExplainableWrapper = ({ children }) => {
  // popup: { visible: bool, word: object|null, message: string|null }
  const [popup, setPopup] = useState({ visible: false, word: null, message: '' });
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
    setPopup({ visible: false, word: null, message: '' });
    setConfirmText(null);
    setShowConfirm(false);
    if (anchorRef.current) {
      anchorRef.current.style.display = 'none';
    }
  };


  // Confirm modal logic
  const handleConfirm = async () => {
    // DEBUG: Log API response

    if (!confirmText) return;
    const textToExplain = confirmText; // capture value
    setShowConfirm(false); // Close confirm popup
    try {
      const data = await explainText(textToExplain);
     
      // Only show plain text explanation
      let message = '';
      if (typeof data === 'string') {
        message = data;
      } else if (data && data.explanation) {
        message = data.explanation;
      } else {
        message = 'No explanation available.';
      }
      setPopup({ visible: true, word: null, message });
    } catch (error) {
      setPopup({ visible: true, word: null, message: 'Error: ' + error });
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
          <div style={{ padding: 18, fontSize: '1.08rem', color: '#333' }}>{popup.message}</div>
        </WordMeaningPopup>
      )}
    </div>
  );
};

export default ExplainableWrapper;
