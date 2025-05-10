import React from 'react';
import './WordExplanation.css';

// Renders a word explanation card
function ExplanationCard({ w, onClose }) {
  if (!w) return null;
  return (
    <div className="explanation-card">
      {onClose && (
        <button
          onClick={onClose}
          className="close-button"
        >
          &times;
        </button>
      )}
      <div style={{ fontWeight: 700, fontSize: '1.7rem', marginBottom: 8, color: '#1976d2', letterSpacing: '0.5px', textAlign: 'center' }}>
        {w.word} {w.ipa && <span style={{ color: '#888', fontSize: '1.1rem', marginLeft: 8 }}>({w.ipa})</span>}
      </div>
      {w.base_word && <div style={{ marginBottom: 6, fontSize: '1.08rem' }}><strong>Base Word:</strong> {w.base_word}</div>}
      {w.explanation && <div style={{ marginBottom: 6, fontSize: '1.08rem' }}><strong>Explanation:</strong> {w.explanation}</div>}
      {w.contextual_meaning && <div style={{ marginBottom: 6, fontSize: '1.08rem' }}><strong>Contextual Meaning:</strong> {w.contextual_meaning}</div>}
      {w.etymology && <div style={{ marginBottom: 6, fontSize: '1.08rem' }}><strong>Etymology:</strong> {w.etymology}</div>}
      {w.example_sentences && w.example_sentences.length > 0 && (
        <div style={{ marginBottom: 6, fontSize: '1.08rem', width: '100%' }}><strong>Example Sentences:</strong>
          <ul style={{ margin: '6px 0 0 18px', padding: 0 }}>
            {w.example_sentences.map((ex, i) => <li key={i} style={{ marginBottom: 4 }}>{ex}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}

export default function WordExplanation({ word, onClose }) {
  // Support both single word object and array (for batch dictionary results)
  if (Array.isArray(word)) {
    return (
      <div>
        {word.map((w, i) => <ExplanationCard key={w.word || i} w={w} onClose={onClose} />)}
      </div>
    );
  } else if (word) {
    return <ExplanationCard w={word} onClose={onClose} />;
  } else {
    return <div style={{ color: '#888', padding: 24, textAlign: 'center' }}>No explanation found.</div>;
  }
}


