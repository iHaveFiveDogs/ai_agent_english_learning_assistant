import React, { useState } from 'react';
import './ChunkQuestionPagination.css';
import { answerQuestionFeedback } from '../../api/questionService';
import { explainText } from '../../api/articleService';
import WordMeaningPopup from '../wrapper/WordMeaningPopup';

/**
 * Props:
 *   chunkQuestionsList: Array<{ chunk: string, question: string }>
 */
function ChunkQuestionPagination({ chunkQuestionsList }) {
  // Popup state for explanation
  const [popupOpen, setPopupOpen] = useState(false);
  const [popupLoading, setPopupLoading] = useState(false);
  const [popupContent, setPopupContent] = useState('');

  // Track selected text
  const handleTextMouseUp = async (e) => {
    const selection = window.getSelection();
    const selectedText = selection && selection.toString().trim();
    if (selectedText && selectedText.length > 0) {
      setPopupLoading(true);
      setPopupOpen(true);
      try {
        const result = await explainText(selectedText);
        setPopupContent(result.explanation || JSON.stringify(result));
      } catch (err) {
        setPopupContent(err.message || 'Failed to fetch explanation');
      }
      setPopupLoading(false);
    }
  };

  const [currentIndex, setCurrentIndex] = useState(0);
  const [inputValue, setInputValue] = useState("");

  // Defensive: always treat as array
  const safeList = Array.isArray(chunkQuestionsList) ? chunkQuestionsList : [];
  const total = safeList.length;

  // Reset currentIndex if list changes and index is out of bounds
  React.useEffect(() => {
    if (currentIndex >= total) {
      setCurrentIndex(0);
    }
  }, [total]);

  // Optionally: handle send click
  const [feedback, setFeedback] = useState({ evaluation: '', comment: '', recommanded_answer: '' });

  const [sending, setSending] = useState(false);

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    setSending(true);
    setInputValue(""); // Clear input immediately
    try {
      const res = await answerQuestionFeedback(current.chunk, current.question, inputValue);
      setFeedback({ evaluation: res.evaluation, comment: res.comment, recommanded_answer: res.recommanded_answer });
    } catch (err) {
      setFeedback({ evaluation: '', comment: '', recommanded_answer: '' });
      console.error('Error sending feedback:', err);
      alert('Failed to send answer feedback.');
    }
    setSending(false);
  };

  if (!safeList || total === 0) {
    return <div style={{ color: '#888', margin: '16px 0' }}>No chunk-question pairs available.</div>;
  }

  const current = safeList[currentIndex];
  if (!current) {
    return <div style={{ color: '#888', margin: '16px 0' }}>No chunk-question pair found.</div>;
  }

  return (
    <div className="chunk-question-outer-wrapper">
      <div className="chunk-question-header">
        Chunk {currentIndex + 1} / {total}
      </div>
      <div className="chunk-question-flex-row chunk-question-top-margin">
        {/* LEFT: Chunk content */}
        <div className="chunk-question-chunk-col">
          <div className="chunk-question-card" onMouseUp={handleTextMouseUp} style={{ cursor: 'text' }}>
            <div>Chunk</div>
            <div>{current.chunk || <span style={{color:'#888'}}>No chunk text</span>}</div>
          </div>
        </div>
        {/* RIGHT: Question, Pagination, Input, Send, Feedback */}
        <div className="chunk-question-right-col">
          <div className="chunk-question-question-card">
            <div>Question</div>
            <div onMouseUp={handleTextMouseUp} style={{ cursor: 'text' }}>{current.question}</div>
          </div>
          {/* Pagination */}
          <div className="chunk-question-pagination-row">
            <button
              onClick={() => setCurrentIndex(i => Math.max(0, i - 1))}
              disabled={currentIndex === 0}
            >
              Previous
            </button>
            <span className="chunk-question-pagination-info">{currentIndex + 1} of {total}</span>
            <button
              onClick={() => setCurrentIndex(i => Math.min(total - 1, i + 1))}
              disabled={currentIndex === total - 1}
            >
              Next
            </button>
          </div>
          <div className="chunk-question-input-row">
            <textarea
              placeholder="Type your answer..."
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              className="chunk-question-input"
              rows={1}
              style={{resize: 'vertical', minHeight: 38}}
            />
            <button
              onClick={handleSend}
              className="chunk-question-send-btn"
              disabled={!inputValue.trim() || sending}
            >
              {sending ? 'Sending...' : 'Send'}
            </button>
          </div>
          {feedback.evaluation && (
            <div className="chunk-question-feedback">
              <div><strong>Evaluation:</strong> <span className={feedback.evaluation === 'Correct' ? 'feedback-correct' : feedback.evaluation === 'Incorrect' ? 'feedback-incorrect' : 'feedback-other'}>{feedback.evaluation}</span></div>
              <div><strong>Comment:</strong> {feedback.comment}</div>
              <div><strong>Recommended answer:</strong> {feedback.recommanded_answer}</div>
            </div>
          )}
        </div>
      </div>
      {/* Popup for explanation */}
      <WordMeaningPopup open={popupOpen} onClose={() => setPopupOpen(false)}>
        <button
          onClick={() => setPopupOpen(false)}
          style={{ position: 'absolute', top: 18, right: 18, background: 'none', border: 'none', fontSize: 22, color: '#888', cursor: 'pointer', zIndex: 10 }}
          aria-label="Close"
        >
          &times;
        </button>
        {popupLoading ? (
          <div style={{ padding: 24, minWidth: 220 }}>Loading...</div>
        ) : (
          <div style={{ padding: 24, minWidth: 220, whiteSpace: 'pre-wrap' }}>{popupContent}</div>
        )}
      </WordMeaningPopup>
    </div>
  );
}

export default ChunkQuestionPagination;
